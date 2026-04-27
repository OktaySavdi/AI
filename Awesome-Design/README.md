# AI Design System Files — Usage Guide

A collection of DESIGN.md files for VS Code and Claude (Anthropic), formatted for use with AI coding agents (GitHub Copilot, Claude Code, Cursor, etc.).

## Files

| File | Design System | Theme |
|---|---|---|
| `DESIGN-vscode.md` | Visual Studio Code | Dark IDE, blue accent, developer-focused |
| `DESIGN-claude.md` | Claude (Anthropic) | Warm editorial, coral + cream, serif typography |

---

## How It Works

Each DESIGN.md file contains a complete design system specification that AI agents can read and follow when generating UI code. Instead of describing colors and spacing in every prompt, you reference the file once and the agent applies all tokens consistently.

---

## Quick Start

### Option 1 — Copy file to your project root

```bash
cp DESIGN-vscode.md /path/to/your/project/DESIGN.md
# or
cp DESIGN-claude.md /path/to/your/project/DESIGN.md
```

Then in any prompt:

```
Build a sidebar navigation component following DESIGN.md
```

### Option 2 — Reference by name in your prompt

If the file is already open in your editor or in the workspace, reference it directly:

```
Using the design tokens from DESIGN-vscode.md, create a file explorer component
```

### Option 3 — Paste specific sections

Copy only the section you need (e.g., section 02 Color Palette) and include it inline in your prompt.

---

## Usage with GitHub Copilot (VS Code)

### Chat panel

1. Open the file in your editor: `DESIGN-vscode.md` or `DESIGN-claude.md`
2. In the Copilot Chat panel, use `#file` to attach it:

```
#file:DESIGN-vscode.md

Create a tab bar component with an active blue top border indicator
```

### Inline suggestions

Add a comment at the top of your CSS/component file:

```css
/* Follows DESIGN-vscode.md color tokens */

.sidebar {
  /* Copilot will suggest using #252526 and related tokens */
}
```

### With `.github/copilot-instructions.md`

Add a global instruction so every Copilot response respects the design system:

```markdown
# Copilot Instructions

When generating UI components, follow the design tokens defined in DESIGN-vscode.md
at the project root. Use the exact hex values and spacing scale from that file.
```

---

## Usage with Claude Code (CLI)

### Reference the file in your prompt

```bash
claude "Read DESIGN-claude.md and build a React chat bubble component 
for user messages using the coral brand color and inter font"
```

### Add to CLAUDE.md (project-level memory)

Create a `CLAUDE.md` in your project root:

```markdown
# Project Context

## Design System
Follow DESIGN-claude.md for all UI work:
- Light mode: canvas #FAF9F5, coral accent #CC785C
- Dark mode: base #181715, elevated #252320
- Fonts: EB Garamond (display), Inter (body), JetBrains Mono (code)
```

---

## Usage with Cursor

### Add to `.cursorrules`

```
When writing UI code, follow the design system in DESIGN-vscode.md.
Use the exact color tokens, spacing scale, and typography rules defined there.
Do not introduce colors or fonts not listed in the file.
```

### Reference in chat

```
@DESIGN-vscode.md Create a notification toast component with the correct
severity border colors and dark background
```

---

## Section Reference

Each DESIGN.md file contains 9 sections. Reference a specific one if you only need part of it:

| Section | What it contains | When to reference |
|---|---|---|
| `01 — Visual Theme` | Mood, philosophy, character | Starting a new project |
| `02 — Color Palette` | All hex tokens with roles | Setting CSS variables or Tailwind config |
| `03 — Typography` | Font stacks, size scale | Setting up a type system |
| `04 — Components` | Buttons, inputs, cards, nav | Building specific UI components |
| `05 — Layout` | Spacing scale, grid, max-widths | Page structure and spacing |
| `06 — Depth & Elevation` | Shadow system, surface hierarchy | Cards, modals, overlays |
| `07 — Do's and Don'ts` | Rules and anti-patterns | Code review or design audit |
| `08 — Responsive` | Breakpoints, mobile behavior | Responsive layouts |
| `09 — Agent Prompts` | Ready-to-use prompts | Copy-paste starting points |

---

## Setting Up CSS Custom Properties

Use section 02 to generate your CSS variables file:

```
Read section 02 of DESIGN-vscode.md and generate a :root CSS custom properties
block I can paste into my global stylesheet
```

Expected output:

```css
:root {
  --bg-editor: #1E1E1E;
  --bg-sidebar: #252526;
  --accent-blue: #007ACC;
  --fg-primary: #CCCCCC;
  --fg-muted: #858585;
  /* ... */
}
```

## Setting Up Tailwind Config

```
Read DESIGN-claude.md and generate a tailwind.config.js colors and fontSize
section that maps all design tokens
```

---

## Example Prompts

### VS Code design system

```
Following DESIGN-vscode.md, create a React component for an editor tab bar.
Include: active tab with blue top border, inactive tab dimming, modified dot indicator,
close button on hover. Use CSS modules and the exact hex values from the file.
```

```
Using the color tokens from DESIGN-vscode.md section 02, generate a Tailwind CSS
config object for the VS Code dark theme palette.
```

```
Build a command palette overlay matching DESIGN-vscode.md — dark input on #3C3C3C,
search results with match highlights in accent-blue, keyboard shortcut badges,
44px item height, escape to close.
```

### Claude design system

```
Following DESIGN-claude.md, create a chat message list component with:
- User messages: coral bubble (#CC785C), right-aligned
- Claude messages: full-width prose, canvas background, EB Garamond for any headings
- Code blocks: surface-card background, JetBrains Mono, copy button
```

```
Using DESIGN-claude.md, build a dark mode landing page hero section with:
warm charcoal base (#181715), EB Garamond display-xl heading,
Inter body text, coral CTA button, 96px section padding.
```

```
Create a Tailwind CSS v4 theme config from DESIGN-claude.md covering
all surface tokens for both light and dark mode.
```

---

## Tips

- **Be specific about sections**: `"Using section 04 of DESIGN-vscode.md, build a button"` is more focused than a broad reference
- **Combine with a framework**: `"Following DESIGN-claude.md, build this in React with Tailwind CSS"`
- **Ask for token extraction first**: `"List all color tokens from DESIGN-vscode.md as CSS variables"` — then use those in subsequent prompts
- **Enforce consistency**: `"Do not use any colors not defined in DESIGN-claude.md"`
- **Use the persona summary**: Section 09 ends with a persona description — paste it when you want the agent to adopt the aesthetic as a north star
