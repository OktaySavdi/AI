#!/usr/bin/env node
/**
 * Interactive package manager setup.
 * Saves preference to ~/.claude/settings.json
 */

const readline = require('readline');
const { claudePath, readJsonFile, writeJsonFile } = require('./lib/utils');

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => new Promise((res) => rl.question(q, res));

(async () => {
  console.log('\nECC Package Manager Setup\n');
  console.log('Options: npm, yarn, pnpm, bun');
  const pm = (await ask('Choose package manager [npm]: ')).trim() || 'npm';

  const settingsFile = claudePath('settings.json');
  const settings = readJsonFile(settingsFile, {});
  settings.packageManager = pm;
  writeJsonFile(settingsFile, settings);

  console.log(`\nPackage manager set to: ${pm}`);
  rl.close();
})();
