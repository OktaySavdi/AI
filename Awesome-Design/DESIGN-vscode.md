# DESIGN.md — Visual Studio Code

> Design system inspired by Visual Studio Code (Dark+ / One Dark Pro default theme).
> Drop this file in your project root and tell your AI agent: "Build UI following DESIGN.md"

---

## 01 — VISUAL THEME & ATMOSPHERE

**Mood**: Precision-engineered dark IDE. Functional before beautiful. Zero ornamentation.
**Density**: High. Information-dense panels, compact spacing, no wasted whitespace.
**Philosophy**: Every pixel earns its place. The editor is the hero — chrome recedes.
**Character**: Authoritative, technical, trusted. The tool that professionals live in.

Dark-first, always. Light theme exists but is secondary. The default dark theme
(`#1E1E1E`) has become the de-facto standard for developer tooling worldwide.

---

## 02 — COLOR PALETTE & ROLES

### Backgrounds (surface hierarchy)

| Token | Hex | Role |
|---|---|---|
| `bg-editor` | `#1E1E1E` | Main editor area — the canvas |
| `bg-sidebar` | `#252526` | File explorer, extensions panel |
| `bg-activity-bar` | `#333333` | Left icon rail |
| `bg-tab-inactive` | `#2D2D2D` | Inactive editor tabs |
| `bg-tab-active` | `#1E1E1E` | Active tab matches editor bg |
| `bg-panel` | `#1E1E1E` | Terminal, output, problems panel |
| `bg-statusbar` | `#007ACC` | Bottom status bar (default blue) |
| `bg-titlebar` | `#3C3C3C` | Window title bar |
| `bg-input` | `#3C3C3C` | Search inputs, command palette |
| `bg-dropdown` | `#3C3C3C` | Dropdown menus |
| `bg-hover` | `#2A2D2E` | List item hover state |
| `bg-selection` | `#264F78` | Editor text selection |

### Accent & Interactive

| Token | Hex | Role |
|---|---|---|
| `accent-blue` | `#007ACC` | Primary interactive — links, buttons, status bar |
| `accent-blue-hover` | `#1177BB` | Button hover state |
| `accent-focus` | `#007FD4` | Focus rings on inputs and elements |
| `accent-modified` | `#E2C08D` | Modified file indicator (tab top border) |

### Foreground

| Token | Hex | Role |
|---|---|---|
| `fg-primary` | `#CCCCCC` | Default text, editor foreground |
| `fg-muted` | `#858585` | Line numbers, inactive labels |
| `fg-dim` | `#6A6A6A` | Placeholders, disabled items |
| `fg-bright` | `#FFFFFF` | Active tab title, status bar text |
| `fg-on-accent` | `#FFFFFF` | Text on blue accent backgrounds |

### Syntax (Dark+ defaults)

| Token | Hex | Role |
|---|---|---|
| `syntax-string` | `#CE9178` | String literals |
| `syntax-keyword` | `#569CD6` | Language keywords |
| `syntax-function` | `#DCDCAA` | Function names |
| `syntax-number` | `#B5CEA8` | Numeric literals |
| `syntax-comment` | `#6A9955` | Code comments |
| `syntax-type` | `#4EC9B0` | Type names, class names |
| `syntax-variable` | `#9CDCFE` | Variable names |
| `syntax-operator` | `#D4D4D4` | Operators, punctuation |
| `syntax-constant` | `#4FC1FF` | Constants, `this` |

### Semantic

| Token | Hex | Role |
|---|---|---|
| `semantic-error` | `#F44747` | Error squiggles, error icons |
| `semantic-warning` | `#CCA700` | Warning squiggles |
| `semantic-info` | `#75BEFF` | Info squiggles |
| `semantic-success` | `#89D185` | Test pass, git added |
| `border-default` | `#474747` | Panel and sidebar borders |
| `border-active` | `#007ACC` | Active panel top border |

---

## 03 — TYPOGRAPHY RULES

### Font Stack

```
UI:     "Segoe UI", system-ui, -apple-system, sans-serif
Editor: "Consolas", "Courier New", monospace
```

> VS Code uses system fonts for UI panels. The editor uses Consolas by default on
> Windows, but Menlo/Monaco on macOS, and "Droid Sans Mono" on Linux.
> For web reproductions, use JetBrains Mono or Fira Code as Consolas proxies.

### Type Scale

| Level | Size | Weight | Line-Height | Use |
|---|---|---|---|---|
| `editor-code` | 14px | 400 | 1.5 | Editor code content |
| `panel-label` | 11px | 700 | 1.4 | Section headers (UPPERCASE) |
| `tab-title` | 13px | 400 | 1.4 | Editor tab filenames |
| `sidebar-item` | 13px | 400 | 1.5 | File tree items |
| `status-bar` | 12px | 400 | 1.0 | Status bar items |
| `tooltip` | 12px | 400 | 1.4 | Hover tooltips |
| `input-text` | 13px | 400 | 1.4 | Search inputs, command palette |
| `badge` | 11px | 600 | 1.0 | Notification badges (numbers) |

### Rules

- Panel section headers: `ALL CAPS`, `11px`, `font-weight: 700`, `letter-spacing: 1px`
- Tab filenames: `13px`, not bold, truncated with ellipsis
- Line numbers: `fg-muted` color, right-aligned, monospace
- Never use decorative fonts — this is an engineering tool

---

## 04 — COMPONENT STYLINGS

### Activity Bar (leftmost icon column)

```
width: 48px
background: bg-activity-bar (#333333)
icon color (inactive): fg-muted (#858585)
icon color (active): fg-primary (#CCCCCC)
active indicator: 2px solid accent-blue left border
badge: accent-blue bg, white text, 16px circle
```

### Sidebar / File Explorer

```
background: bg-sidebar (#252526)
item height: 22px
item padding: 0 12px
hover: bg-hover (#2A2D2E)
active selection: #094771 (muted blue)
indent per level: 16px
expand arrow: fg-muted, 8px
```

### Editor Tabs

```
height: 35px
inactive tab bg: bg-tab-inactive (#2D2D2D)
active tab bg: bg-editor (#1E1E1E)
active tab top border: 1px solid accent-blue
inactive tab text: fg-muted
active tab text: fg-primary
modified indicator: dot or top border accent-modified
close icon: appears on hover, fg-muted
```

### Status Bar

```
height: 22px
background: accent-blue (#007ACC)
text: fg-on-accent (#FFFFFF)
font-size: 12px
item padding: 0 8px
separator: 1px rgba(255,255,255,0.2)
debugging state: #CC6633 (orange-brown)
```

### Command Palette / Quick Open

```
overlay background: rgba(0,0,0,0.6)
input container: bg-input (#3C3C3C)
input border-bottom: 1px solid accent-focus
item height: 44px
item padding: 0 16px
focused item: bg-hover
match highlight: accent-blue, bold
description text: fg-muted
keyboard shortcut badge: bg-darker, fg-muted
```

### Input / Search Box

```
height: 28px
background: bg-input (#3C3C3C)
text: fg-primary
border: 1px solid transparent
focused border: 1px solid accent-focus
placeholder: fg-dim
border-radius: 2px
```

### Buttons

```
primary:
  background: accent-blue (#007ACC)
  text: white
  padding: 4px 14px
  border-radius: 2px
  hover: accent-blue-hover (#1177BB)
  font-size: 13px

secondary:
  background: transparent
  border: 1px solid #6F6F6F
  text: fg-primary
  hover: bg-hover

icon button:
  background: transparent
  hover: rgba(255,255,255,0.1)
  size: 20-24px
  border-radius: 4px
```

### Notification Toast (bottom-right)

```
background: bg-input (#3C3C3C)
border-left: 3px solid (error=#F44747 / warning=#CCA700 / info=#75BEFF)
width: 320px
padding: 12px 16px
font-size: 13px
action button: inline text link, accent-blue
```

### Tree / List Items

```
height: 22px
hover: bg-hover
selected (active): #094771
selected (inactive): rgba(9,71,113,0.5)
focused outline: 1px solid #007ACC
icon: 16x16, positioned left of label
```

### Badge

```
background: accent-blue
text: white
min-width: 18px
height: 18px
border-radius: 10px
font-size: 11px
font-weight: 600
```

---

## 05 — LAYOUT PRINCIPLES

### Spacing Scale

| Token | Value | Use |
|---|---|---|
| `space-1` | 4px | Icon padding, micro gaps |
| `space-2` | 8px | Item padding, small gaps |
| `space-3` | 12px | Form element padding |
| `space-4` | 16px | Section padding, sidebar indent |
| `space-6` | 24px | Panel section gaps |
| `space-8` | 32px | Large panel separations |

### Grid / Layout Structure

```
┌──────────────────────────────────────────────────────┐
│ Title Bar (32px)                                     │
├────┬──────────────────────────────────┬──────────────┤
│ A  │ Sidebar (240-300px default)      │ Panel (opt.) │
│ c  │ ┌──────────────────────────────┐ │              │
│ t  │ │ Editor Tabs (35px)           │ │              │
│ i  │ ├──────────────────────────────┤ │              │
│ v  │ │                              │ │              │
│ i  │ │ Editor Area                  │ │              │
│ t  │ │ (fills remaining height)     │ │              │
│ y  │ │                              │ │              │
│    │ └──────────────────────────────┘ │              │
│ B  ├──────────────────────────────────┤              │
│ a  │ Terminal / Output / Problems     │              │
│ r  │ (collapsible, ~30% height)       │              │
│    ├──────────────────────────────────┴──────────────┤
│    │ Status Bar (22px)                               │
└────┴─────────────────────────────────────────────────┘
 48px
```

### Rules

- All panels use consistent 0 margins at edges — content touches container walls
- Section labels are UPPERCASE with generous letter-spacing
- Icons align on 4px grid
- Sidebar sections use 8px top padding before their header label
- Never use rounded corners larger than 4px for chrome elements
- Flat design — avoid box-shadows except on modals/overlays

---

## 06 — DEPTH & ELEVATION

VS Code uses **color contrast** not shadows for elevation:

| Level | Surface | Color |
|---|---|---|
| Floor | Editor | `#1E1E1E` |
| Raised | Sidebar, panels | `#252526` |
| Floating | Activity bar | `#333333` |
| Modal | Dialogs, command palette | `#252526` + overlay |
| Tooltip | Hover cards | `#2C2C2C` with 1px border |

Shadows are used **only** for:
- Command palette (center modal): `0 2px 8px rgba(0,0,0,0.6)`
- Context menus: `0 2px 4px rgba(0,0,0,0.5)`
- Notification toasts: `0 0 8px rgba(0,0,0,0.5)`

---

## 07 — DO'S AND DON'TS

### Do

- Use ALL CAPS for panel section headers (Explorer, OUTLINE, TIMELINE)
- Make the editor/content area the visual focus — chrome should recede
- Use `accent-blue` (#007ACC) exclusively for interactive primary actions
- Show keyboard shortcuts everywhere — this audience uses them
- Use monospace font for all code, paths, terminal output, filenames
- Keep icon sizes consistent: 16px for tree icons, 20px for toolbar icons
- Use status bar to communicate state without interrupting the workflow

### Don't

- Don't use rounded corners > 4px on UI chrome elements (tabs, inputs, panels)
- Don't add drop shadows to panels or sidebars
- Don't use more than one accent color for interactive elements
- Don't use light backgrounds in dark mode — maintain the dark surface hierarchy
- Don't add decorative illustrations or gradients to UI chrome
- Don't use font sizes below 11px
- Don't use animations that exceed 150ms for panel transitions

---

## 08 — RESPONSIVE BEHAVIOR

VS Code is a desktop-first application. For web-based reproductions:

| Breakpoint | Width | Behavior |
|---|---|---|
| Compact | < 600px | Hide sidebar; activity bar icons only; single panel |
| Mobile | 600–768px | Sidebar as drawer overlay; no split editor |
| Tablet | 768–1024px | Sidebar 200px; single editor pane |
| Desktop | 1024–1440px | Full layout; sidebar 240px |
| Wide | > 1440px | Max editor width unconstrained; extra padding |

### Touch Targets

- Minimum tap target: 44×44px (sidebar items are 22px tall — add padding for mobile)
- Activity bar icons: 48×48px
- Tab close buttons: 20×20px (desktop), 28×28px (mobile)

---

## 09 — AGENT PROMPT GUIDE

### Quick Color Reference

```
Editor bg:   #1E1E1E    Sidebar bg:   #252526    Activity:    #333333
Primary:     #007ACC    Text:         #CCCCCC    Muted:       #858585
Error:       #F44747    Warning:      #CCA700    Success:     #89D185
String:      #CE9178    Keyword:      #569CD6    Comment:     #6A9955
```

### Ready-to-Use Prompts

```
"Build a file explorer sidebar component matching DESIGN.md —
dark #252526 background, 22px item height, accent-blue selection,
ALL CAPS section headers in 11px, Segoe UI font"

"Create an editor tab bar following DESIGN.md — dark tabs, blue
active top border, modified dot indicator, Consolas filename text"

"Design a command palette overlay using DESIGN.md — dark input
on #3C3C3C, match highlights in accent-blue, keyboard shortcut
badges, 44px item height"

"Build a status bar component: #007ACC background, 22px height,
12px white Segoe UI text, icon + label pairs with 8px padding"

"Create a notification toast matching DESIGN.md — dark #3C3C3C
background, colored left border by severity, 13px text, inline action"
```

### Persona Summary

> VS Code is where developers spend 8+ hours a day. The UI must be invisible —
> functional, precise, and completely unobtrusive. If you notice the chrome,
> it has failed. Dark surfaces, blue accents, monospace text, zero decoration.
