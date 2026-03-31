import os
import subprocess
import argparse
import re
import json
import sys
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import ollama

# Load environment variables from .env file if it exists
load_dotenv()

# --- Tools ---

def search_repository(regex_pattern: str, file_extension: str = "", context_lines: int = 5) -> str:
    r"""
    Searches the local repository for a specific regex pattern to find where functions are called or defined.
    Provides surrounding context lines.
    
    Args:
        regex_pattern: The regular expression pattern to search for.
        file_extension: Optional. The file extension to limit the search to (e.g., '.py', '.cs').
        context_lines: Number of context lines to show around each match.
    """
    target_directory = "." 
    command = ["grep", "-rnEI", f"-C{context_lines}", "--exclude-dir=.git", "--exclude-dir=__pycache__", "--exclude-dir=venv"]
    
    if file_extension:
        if not file_extension.startswith("*"):
            include_pattern = f"*{file_extension}"
        else:
            include_pattern = file_extension
        command.extend(["--include", include_pattern])
        
    command.extend([regex_pattern, target_directory])
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.stdout:
            output = result.stdout
            max_chars = 15000 
            if len(output) > max_chars:
                return output[:max_chars] + "\n... [Output truncated due to length.]"
            return output
        elif result.stderr:
            if result.returncode == 1 and not result.stderr:
                 return f"No matches found for pattern: '{regex_pattern}'"
            return f"Error during search: {result.stderr}"
        else:
            return f"No matches found for pattern: '{regex_pattern}'"
    except Exception as e:
        return f"System error executing search: {str(e)}"

def read_file(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """
    Reads the content of a file, with optional line bounds.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        if start_line is not None or end_line is not None:
            start = (start_line - 1) if start_line else 0
            end = end_line if end_line else len(lines)
            selected_lines = lines[start:end]
            return "".join(selected_lines)
        else:
            return "".join(lines)
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_directory_tree(path: str = ".", depth: int = 2) -> str:
    """
    Returns a hierarchical map of folders and files in the repository.
    """
    output = []
    ignored_dirs = {'.git', '__pycache__', 'node_modules', 'obj', 'bin', 'venv'}
    def _walk(current_path, current_depth):
        if current_depth > depth:
            return
        try:
            entries = sorted(os.listdir(current_path))
        except Exception as e:
            return
        for entry in entries:
            if entry in ignored_dirs:
                continue
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                output.append(f"{'  ' * current_depth}DIR: {entry}/")
                _walk(full_path, current_depth + 1)
            else:
                output.append(f"{'  ' * current_depth}FILE: {entry}")
    output.append(f"Project Tree (depth={depth}):")
    _walk(path, 0)
    return "\n".join(output)

def get_file_symbols(file_path: str) -> str:
    """
    Scans a file and returns class names, method signatures, and important symbols.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File not found: {file_path}"
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        symbols = []
        patterns = [
            (r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'Function (Python)'),
            (r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[:\(]', 'Class (Python)'),
            (r'^\s*(?:(?:public|private|protected|internal|static|async|virtual|override|abstract|sealed|partial|new)\s+)*([\w\<\>\[\]]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'Method (C#/Java)'),
            (r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{', 'Class (C#/Java/JS)'),
        ]
        lines = content.splitlines()
        for i, line in enumerate(lines):
            for pattern, symbol_type in patterns:
                match = re.search(pattern, line)
                if match:
                    if symbol_type == 'Method (C#/Java)':
                        symbol_name = match.group(2)
                        symbols.append(f"Line {i+1}: [{symbol_type}] {symbol_name}")
                    else:
                        symbol_name = match.group(1)
                        symbols.append(f"Line {i+1}: [{symbol_type}] {symbol_name}")
                    break
        if not symbols:
            return f"No significant symbols found in {file_path}."
        return f"Symbols in {file_path}:\n" + "\n".join(symbols)
    except Exception as e:
        return f"Error extracting symbols: {str(e)}"

# --- Tool Definitions for Ollama ---

tools = [
    {
        'type': 'function',
        'function': {
            'name': 'search_repository',
            'description': 'Searches the local repository for a specific regex pattern to find where functions are called or defined.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'regex_pattern': {'type': 'string', 'description': 'The regular expression pattern to search for (e.g., "def my_function" or "my_function\(").'},
                    'file_extension': {'type': 'string', 'description': 'Optional. The file extension to limit the search to (e.g., ".py", ".cs", ".js").'},
                    'context_lines': {'type': 'integer', 'description': 'Optional. Number of context lines to show around each match.'},
                },
                'required': ['regex_pattern'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'read_file',
            'description': 'Reads the content of a file, with optional line bounds.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {'type': 'string', 'description': 'Path to the file to read.'},
                    'start_line': {'type': 'integer', 'description': 'Optional. The 1-based line number to start reading from.'},
                    'end_line': {'type': 'integer', 'description': 'Optional. The 1-based line number to end reading at (inclusive).'},
                },
                'required': ['file_path'],
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'list_directory_tree',
            'description': 'Returns a hierarchical map of folders and files in the repository.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'path': {'type': 'string', 'description': 'The directory to list.'},
                    'depth': {'type': 'integer', 'description': 'How many levels deep to go.'},
                },
            },
        },
    },
    {
        'type': 'function',
        'function': {
            'name': 'get_file_symbols',
            'description': 'Scans a file and returns class names, method signatures, and important symbols.',
            'parameters': {
                'type': 'object',
                'properties': {
                    'file_path': {'type': 'string', 'description': 'Path to the file.'},
                },
                'required': ['file_path'],
            },
        },
    },
]

available_functions = {
    'search_repository': search_repository,
    'read_file': read_file,
    'list_directory_tree': list_directory_tree,
    'get_file_symbols': get_file_symbols,
}

# --- Orchestration ---

def run_chat(prompt: str, model: str):
    messages = [{'role': 'user', 'content': prompt}]
    
    print(f"Asking Local Model ({model}): {prompt}\n")
    
    try:
        # First request
        response = ollama.chat(
            model=model,
            messages=messages,
            tools=tools,
        )
        
        messages.append(response['message'])
        
        # Log if we got a response content
        if response['message'].get('content'):
            print(f"--- Model initial thought ---\n{response['message']['content']}\n")

        # Handle tool calls
        if response['message'].get('tool_calls'):
            for tool in response['message']['tool_calls']:
                func_name = tool['function']['name']
                func_args = tool['function']['arguments']
                
                if func_name in available_functions:
                    print(f"--- Calling tool: {func_name}({func_args}) ---")
                    func_to_call = available_functions[func_name]
                    # Ensure args are passed correctly
                    try:
                        func_result = func_to_call(**func_args)
                    except TypeError as te:
                        # Sometimes models pass strings that need to be ints
                        print(f"Warning: Argument type mismatch, attempting conversion... {te}")
                        # Simple fix for common int args
                        for int_arg in ['start_line', 'end_line', 'context_lines', 'depth']:
                            if int_arg in func_args and isinstance(func_args[int_arg], str):
                                func_args[int_arg] = int(func_args[int_arg])
                        func_result = func_to_call(**func_args)
                    
                    messages.append({
                        'role': 'tool',
                        'content': str(func_result),
                        'name': func_name
                    })
                else:
                    print(f"Error: Tool {func_name} not found.")

            # Get final response from model after tool results
            print("--- Generating final response... ---")
            final_response = ollama.chat(model=model, messages=messages)
            print("\nModel's Final Response:")
            print(final_response['message']['content'])
        else:
            if not response['message'].get('content'):
                print("No content or tool calls returned from model.")
            else:
                print("\nModel's Response:")
                print(response['message']['content'])
                
    except Exception as e:
        print(f"An error occurred during chat: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A toolbelt for local repo search using Ollama.")
    parser.add_argument("prompt", type=str, help="Your prompt for the model.")
    parser.add_argument("--model", type=str, default="qwen2.5:7b", help="The Ollama model to use.")
    
    args = parser.parse_args()
    
    run_chat(args.prompt, args.model)
