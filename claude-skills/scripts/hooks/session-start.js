#!/usr/bin/env node
/**
 * Session start hook — load project context.
 * Runs at the beginning of each Claude Code session.
 */

const { claudePath, readJsonFile, writeJsonFile, timestamp } = require('../lib/utils');
const path = require('path');
const fs = require('fs');

const sessionFile = claudePath('session', 'current.json');
const instinctsFile = claudePath('instincts', 'pending.json');

// Load pending instincts count for display
const instincts = readJsonFile(instinctsFile, { pending: [] });
const pendingCount = instincts.pending?.length || 0;

// Write session start record
writeJsonFile(sessionFile, {
  startedAt: timestamp(),
  cwd: process.cwd(),
  pendingInstincts: pendingCount,
});

if (pendingCount > 0) {
  process.stderr.write(`[ECC] ${pendingCount} pending instinct(s). Run /instinct-status to review.\n`);
}
