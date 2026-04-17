#!/usr/bin/env node
/**
 * Evaluate session hook — extract patterns from completed session.
 * Runs at session end or on /learn-eval command.
 */

const { claudePath, readJsonFile, writeJsonFile, timestamp } = require('../lib/utils');

const sessionFile = claudePath('session', 'current.json');
const instinctsFile = claudePath('instincts', 'pending.json');

const session = readJsonFile(sessionFile, {});
const instincts = readJsonFile(instinctsFile, { pending: [] });

// Placeholder: in a real implementation this would call a summarization model
// to extract patterns from the session transcript.
// For now, log that evaluation was requested.
process.stderr.write(`[ECC] Session evaluation triggered at ${timestamp()}.\n`);
process.stderr.write('[ECC] Run /learn-eval to extract and save instincts from this session.\n');
