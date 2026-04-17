Generate a Kyverno CEL ClusterPolicy using the kubernetes-expert skill.

Requirements from: $ARGUMENTS

Follow these rules:
- API: `kyverno.io/v1` + CEL expressions
- Include both Validate AND Mutate rules where sensible
- `validationFailureAction: Audit` (never Enforce directly)
- Add `background: true`
- Use proper CEL gotchas:
  - Unquoted field names in object{} constructors
  - Backtick-escape label keys with dots/slashes
  - No enumerate() — use index filter pattern
  - Map key checks: "key" in map (not has())
- Add annotations: title, category, severity, description
- Include a PolicyException template as a comment at the bottom

Output the complete YAML policy file.
