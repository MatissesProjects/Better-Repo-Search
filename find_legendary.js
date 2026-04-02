const SALT = 'friend-2026-401';

const RARITY_WEIGHTS = {
  common: 60,
  uncommon: 25,
  rare: 10,
  epic: 4,
  legendary: 1,
};

const RARITIES = ['common', 'uncommon', 'rare', 'epic', 'legendary'];

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function hashString(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function rollRarity(rng) {
  const total = Object.values(RARITY_WEIGHTS).reduce((a, b) => a + b, 0);
  let rollValue = rng() * total;
  for (const rarity of RARITIES) {
    rollValue -= RARITY_WEIGHTS[rarity];
    if (rollValue < 0) return rarity;
  }
  return 'common';
}

function checkSeed(userId) {
  const key = userId + SALT;
  const rng = mulberry32(hashString(key));
  
  const rarity = rollRarity(rng);
  if (rarity !== 'legendary') return false;
  
  // Skip Species (2nd call)
  rng(); 
  // Skip Eyes (3rd call)
  rng();
  // Hat call (4th call) - only exists for non-common
  rng();
  
  // Shiny check (5th call)
  const isShiny = rng() < 0.01;
  return isShiny;
}

console.log("Searching for Legendary Shiny User IDs...");
let found = 0;
for (let i = 0; i < 1000000; i++) {
  const userId = i.toString();
  if (checkSeed(userId)) {
    console.log(`FOUND: ID "${userId}" results in a Legendary Shiny!`);
    found++;
    if (found >= 5) break;
  }
}
