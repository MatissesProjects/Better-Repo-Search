---
name: better-repo-search
description: Executes a local Python script that uses Tree-sitter and an Ollama model to perform deep, multi-step semantic code searches and dependency analysis. Trigger this when a user asks for complex codebase analysis.
---
# Local Code Search Skill

You have access to a Python script named `search_tool.py` located in the exact same directory as this `SKILL.md` file (typically `~/.gemini/skills/local-code-search/Better-Repo-Search/search_tool.py` or `.gemini/skills/local-code-search/Better-Repo-Search/search_tool.py`). 

This script utilizes local LLMs (via Ollama) and Tree-sitter to autonomously explore, search, and extract code blocks from the repository.

## Usage Instructions
When a user asks you to perform a deep codebase analysis, semantic search, or extract dependencies, delegate the task to this script.

Use your shell execution tool to run the following command:
```bash
python <PATH_TO_SKILL_DIR>/search_tool.py "<USER_PROMPT>"
```

Arguments:
<USER_PROMPT>: The natural language instruction describing what needs to be found or analyzed. Pass the user's intent directly to this argument.

--repo: The path to the repository to search. Default to . (the current working directory) unless specified otherwise.

-v or --verbose: Append this flag if the user explicitly asks to see the detailed thought process and logs.
