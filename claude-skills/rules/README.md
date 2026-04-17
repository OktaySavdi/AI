# Rules Directory

Language-specific coding rules that extend the `common/` base rules.

## Structure

```
rules/
├── common/           # Always-apply rules for all languages
│   ├── agents.md     # Agent delegation
│   ├── coding-style.md
│   ├── git-workflow.md
│   ├── hooks.md
│   ├── patterns.md
│   ├── performance.md
│   ├── security.md
│   └── testing.md
├── golang/
│   └── rules.md
├── php/
│   └── rules.md
├── python/
│   └── rules.md
├── swift/
│   └── rules.md
└── typescript/
    └── rules.md
```

## How Rules Are Applied

Rules in `common/` apply to **every task**. Language rules apply when working
in that language.

Configure in `.claude/settings.json`:

```json
{
  "rules": {
    "always": ["common/"],
    "byFileType": {
      "*.py": ["python/"],
      "*.ts": ["typescript/"],
      "*.go": ["golang/"],
      "*.swift": ["swift/"],
      "*.php": ["php/"]
    }
  }
}
```

## Adding a New Language Rule Set

1. Create `rules/<language>/rules.md`
2. Start with `# <Language> Rules` heading
3. Reference `common/` rules with: "Extends `common/` rules"
4. Cover: formatter, linter, type safety, error handling, testing, tools
