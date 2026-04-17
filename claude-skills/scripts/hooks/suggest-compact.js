#!/usr/bin/env node
/**
 * Suggest compact hook — fires when context approaches capacity.
 * Prints a suggestion to compact if context is getting large.
 */

const threshold = parseInt(process.env.COMPACT_SUGGEST_THRESHOLD || '50', 10);
const usagePct = parseInt(process.env.CLAUDE_CONTEXT_USAGE_PCT || '0', 10);

if (usagePct >= threshold) {
  process.stderr.write(
    `[ECC] Context at ${usagePct}%. Consider running /compact to preserve quality.\n`
  );
}
