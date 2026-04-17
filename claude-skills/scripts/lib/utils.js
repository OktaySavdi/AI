/**
 * Cross-platform utilities for ECC scripts.
 */

const os = require('os');
const path = require('path');
const fs = require('fs');

const HOME = os.homedir();
const CLAUDE_DIR = path.join(HOME, '.claude');

function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

function readJsonFile(filePath, defaultValue = {}) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return defaultValue;
  }
}

function writeJsonFile(filePath, data) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n', 'utf8');
}

function claudePath(...parts) {
  return path.join(CLAUDE_DIR, ...parts);
}

function timestamp() {
  return new Date().toISOString();
}

module.exports = { HOME, CLAUDE_DIR, ensureDir, readJsonFile, writeJsonFile, claudePath, timestamp };
