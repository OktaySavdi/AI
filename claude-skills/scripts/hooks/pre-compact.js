#!/usr/bin/env node
/**
 * Pre-compact hook — save important state before context is compacted.
 */

const { claudePath, readJsonFile, writeJsonFile, timestamp } = require('../lib/utils');

const compactLogFile = claudePath('session', 'compact-log.json');
const log = readJsonFile(compactLogFile, { compactions: [] });

log.compactions.push({ at: timestamp(), cwd: process.cwd() });
if (log.compactions.length > 20) {
  log.compactions = log.compactions.slice(-20);
}
writeJsonFile(compactLogFile, log);

process.stderr.write('[ECC] Pre-compact: state saved.\n');
