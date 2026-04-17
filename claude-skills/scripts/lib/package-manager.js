/**
 * Package manager detection for ECC setup scripts.
 */

const { execSync } = require('child_process');
const fs = require('fs');

const LOCKFILES = {
  'package-lock.json': 'npm',
  'yarn.lock': 'yarn',
  'pnpm-lock.yaml': 'pnpm',
  'bun.lockb': 'bun',
};

function detectFromLockfile(dir = process.cwd()) {
  for (const [file, pm] of Object.entries(LOCKFILES)) {
    if (fs.existsSync(`${dir}/${file}`)) {
      return pm;
    }
  }
  return null;
}

function isInstalled(cmd) {
  try {
    execSync(`which ${cmd}`, { stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function detect(dir) {
  const fromLock = detectFromLockfile(dir);
  if (fromLock) return fromLock;
  for (const pm of ['bun', 'pnpm', 'yarn', 'npm']) {
    if (isInstalled(pm)) return pm;
  }
  return 'npm';
}

function runCommand(pm, args) {
  const cmds = {
    npm: `npm ${args}`,
    yarn: `yarn ${args}`,
    pnpm: `pnpm ${args}`,
    bun: `bun ${args}`,
  };
  return cmds[pm] || `npm ${args}`;
}

module.exports = { detect, detectFromLockfile, isInstalled, runCommand };
