#!/usr/bin/env node
/**
 * Session end hook — save session state.
 */

const { claudePath, readJsonFile, writeJsonFile, timestamp } = require('../lib/utils');

const sessionFile = claudePath('session', 'current.json');
const historyFile = claudePath('session', 'history.json');

const current = readJsonFile(sessionFile, {});
const history = readJsonFile(historyFile, { sessions: [] });

if (current.startedAt) {
  history.sessions.push({
    ...current,
    endedAt: timestamp(),
  });
  // Keep last 50 sessions
  if (history.sessions.length > 50) {
    history.sessions = history.sessions.slice(-50);
  }
  writeJsonFile(historyFile, history);
}
