# DESIGN.md — Claude (Anthropic)

> Design system for Claude by Anthropic — the AI assistant interface.
> Drop this file in your project root and tell your AI agent: "Build UI following DESIGN.md"

---

## 01 — VISUAL THEME & ATMOSPHERE

**Mood**: Warm editorial intelligence. The feeling of a trusted expert in a well-lit study.
**Density**: Comfortable. Generous line-height, breathing room. Never cramped.
**Philosophy**: Human conversation deserves warmth. AI should feel approachable, not clinical.
**Character**: Thoughtful, refined, unhurried. Cream canvas as editorial floor,
coral as brand voltage, dark as product-chrome surface.

The dual-mode system is critical:
- **Light mode**: Parchment/cream canvas. Warm whites, never cold grays. Serif display type.
- **Dark mode**: Deep warm charcoal (`#181715`), elevated surfaces in `#252320`. Not cold black.

---

## 02 — COLOR PALETTE & ROLES

### Brand

| Token | Hex | Role |
|---|---|---|
| `brand-coral` | `#CC785C` | Primary brand, CTAs, active states |
| `brand-coral-active` | `#A9583E` | Pressed / deeper state |
| `brand-coral-light` | `#E8A48A` | Hover tints, subtle highlights |
| `brand-teal` | `#5DB8A6` | Secondary accent, success states |
| `brand-amber` | `#E8A55A` | Warning, special callouts |

### Light Mode Surfaces

| Token | Hex | Role |
|---|---|---|
| `canvas` | `#FAF9F5` | Page background — warm parchment |
| `surface-soft` | `#F5F0E8` | Section backgrounds, subtle separation |
| `surface-card` | `#EFE9DE` | Cards, panels, raised content |
| `surface-border` | `#E6DFD8` | Hairline dividers, borders |
| `surface-elevated` | `#E8E2D8` | Hover state backgrounds |

### Dark Mode Surfaces

| Token | Hex | Role |
|---|---|---|
| `dark-base` | `#181715` | Page background — warm charcoal |
| `dark-elevated` | `#252320` | Cards, sidebars, raised panels |
| `dark-overlay` | `#2E2B27` | Modals, dropdown backgrounds |
| `dark-border` | `#3A3630` | Dividers and borders |
| `dark-hover` | `#302D29` | Hover state backgrounds |

### Typography Colors

| Token | Hex | Role |
|---|---|---|
| `ink` | `#141413` | Primary text (light mode) |
| `body` | `#3D3D3A` | Body copy, secondary text |
| `muted` | `#6C6A64` | Captions, labels, meta |
| `on-dark` | `#FAF9F5` | Primary text (dark mode) |
| `on-dark-muted` | `#B5AFA7` | Muted text on dark surfaces |
| `placeholder` | `#A09890` | Input placeholder text |

### Semantic

| Token | Hex | Role |
|---|---|---|
| `semantic-error` | `#C0392B` | Error states |
| `semantic-warning` | `#E8A55A` | Warning callouts |
| `semantic-success` | `#5DB8A6` | Success (teal brand) |
| `semantic-info` | `#4A90D9` | Info states |

---

## 03 — TYPOGRAPHY RULES

### Font Stack

```
Display: "Copernicus", "EB Garamond", Georgia, serif
Body:    "StyreneB", "Inter", system-ui, sans-serif
Code:    "JetBrains Mono", "Fira Code", "Consolas", monospace
```

> Copernicus is Anthropic's proprietary display serif. Use EB Garamond (Google Fonts)
> or Georgia as an open substitute. For body copy, Inter is the best open substitute
> for StyreneB (Anthropic's proprietary sans).

### Type Scale

| Level | Size | Weight | Line-Height | Font | Use |
|---|---|---|---|---|---|
| `display-xl` | 64px | 400 | 1.05 | Serif | Hero headings |
| `display-lg` | 48px | 400 | 1.1 | Serif | Page titles |
| `display-md` | 36px | 400 | 1.15 | Serif | Section headings |
| `display-sm` | 28px | 400 | 1.2 | Serif | Card titles |
| `heading-lg` | 22px | 600 | 1.3 | Sans | Sub-section headers |
| `heading-md` | 18px | 600 | 1.35 | Sans | Component headers |
| `body-lg` | 18px | 400 | 1.65 | Sans | Lead paragraphs |
| `body-md` | 16px | 400 | 1.55 | Sans | Standard body text |
| `body-sm` | 14px | 400 | 1.5 | Sans | Secondary text |
| `caption` | 13px | 500 | 1.4 | Sans | Labels, meta, badges |
| `code` | 14px | 400 | 1.6 | Mono | Inline and block code |
| `code-sm` | 12px | 400 | 1.5 | Mono | Code annotations |

### Rules

- Display headings always use the serif face — even in dark mode
- Body copy uses only the sans-serif face
- Code always uses the monospace face, never serif or sans
- Headings should be set in natural weight (400) for serif — never bold
- Maximum line width: 68ch for body text (readability)
- Minimum contrast: 4.5:1 for body, 3:1 for large display text

---

## 04 — COMPONENT STYLINGS

### Primary Button

```
background: brand-coral (#CC785C)
text: white
font: 15px / 500 / sans
padding: 10px 20px
border-radius: 8px (md)
border: none

hover:
  background: brand-coral-active (#A9583E)
  transform: none

pressed:
  background: #8A4732
  transform: scale(0.98)

disabled:
  opacity: 0.45
  cursor: not-allowed
```

### Secondary / Ghost Button

```
background: transparent
border: 1.5px solid surface-border (#E6DFD8)
text: body (#3D3D3A)
padding: 10px 20px
border-radius: 8px

hover:
  background: surface-soft (#F5F0E8)
  border-color: muted (#6C6A64)

dark mode:
  border-color: dark-border (#3A3630)
  text: on-dark (#FAF9F5)
  hover background: dark-hover (#302D29)
```

### Chat Input (Textarea)

```
background: surface-card (#EFE9DE)
border: 1.5px solid surface-border
border-radius: 12px (lg)
padding: 14px 16px
font: body-md, sans
color: ink
min-height: 52px
max-height: 200px (scrollable)

focused:
  border-color: brand-coral (#CC785C)
  box-shadow: 0 0 0 3px rgba(204,120,92,0.15)

placeholder: color: placeholder (#A09890)

dark mode:
  background: dark-elevated (#252320)
  border-color: dark-border
  color: on-dark
```

### Message Bubble — User

```
background: brand-coral (#CC785C)
text: white
border-radius: 18px 18px 4px 18px
padding: 12px 16px
max-width: 75%
font: body-md
align: right
```

### Message Bubble — Claude

```
background: transparent (or surface-soft in some views)
text: ink / on-dark
border-radius: 0 (flat, full-width in most views)
padding: 16px 0
max-width: 720px (prose width)
font: body-md
align: left
line-height: 1.65

code blocks:
  background: surface-card (#EFE9DE) / dark: dark-elevated (#252320)
  border: 1px solid surface-border
  border-radius: 8px
  padding: 16px
  font: code (JetBrains Mono 14px)
  header bar: language label + copy button
```

### Card

```
background: surface-card (#EFE9DE)
border: 1px solid surface-border (#E6DFD8)
border-radius: 12px
padding: 20px 24px
box-shadow: 0 1px 3px rgba(0,0,0,0.04)

hover:
  box-shadow: 0 4px 12px rgba(0,0,0,0.08)
  border-color: muted

dark mode:
  background: dark-elevated (#252320)
  border-color: dark-border (#3A3630)
```

### Navigation / Sidebar

```
background: surface-soft (#F5F0E8) / dark: dark-base (#181715)
width: 260px
padding: 16px 8px

nav item:
  height: 36px
  padding: 0 12px
  border-radius: 8px
  font: 14px / 500
  color: body

active:
  background: surface-card (#EFE9DE) / dark: dark-elevated
  color: ink
  font-weight: 600

hover:
  background: surface-elevated (#E8E2D8) / dark: dark-hover

section header:
  font: caption, UPPERCASE, letter-spacing: 0.08em
  color: muted
  padding: 16px 12px 4px
```

### Tag / Badge

```
background: surface-card
border: 1px solid surface-border
text: muted
font: caption (13px / 500)
padding: 3px 10px
border-radius: pill (999px)

variant coral:
  background: rgba(204,120,92,0.12)
  border-color: rgba(204,120,92,0.3)
  text: brand-coral-active

variant teal:
  background: rgba(93,184,166,0.12)
  border-color: rgba(93,184,166,0.3)
  text: #3D9485
```

### Divider / Hairline

```
border: none
border-top: 1px solid surface-border (#E6DFD8)
margin: 24px 0

dark mode: border-color: dark-border (#3A3630)
```

---

## 05 — LAYOUT PRINCIPLES

### Spacing Scale

| Token | Value | Use |
|---|---|---|
| `space-xxs` | 4px | Micro gaps, icon padding |
| `space-xs` | 8px | Tight internal padding |
| `space-sm` | 12px | Component internal spacing |
| `space-md` | 16px | Standard padding |
| `space-lg` | 24px | Between components |
| `space-xl` | 32px | Section separations |
| `space-xxl` | 48px | Major section gaps |
| `space-section` | 96px | Full-page section breaks |

### Border Radius Scale

| Token | Value |
|---|---|
| `radius-xs` | 4px |
| `radius-sm` | 6px |
| `radius-md` | 8px |
| `radius-lg` | 12px |
| `radius-xl` | 16px |
| `radius-pill` | 999px |
| `radius-full` | 50% |

### Layout Grid

```
Chat interface:
  sidebar: 260px fixed left
  conversation: flex-1, centered content
  content max-width: 720px
  padding: 0 24px
  margin: 0 auto

Marketing / landing:
  max-width: 1200px
  columns: 12
  gutter: 24px
  margin: 0 auto
  section padding: 96px 0
```

### Prose Width

Maximum comfortable reading width is `68ch` (~720px in body-md).
Never allow conversation text to span full page width on wide screens.

---

## 06 — DEPTH & ELEVATION

Claude uses **subtle shadow layering** with warm-tinted shadows:

| Level | Surface | Shadow |
|---|---|---|
| Flat | Canvas, page bg | none |
| Resting | Cards, panels | `0 1px 3px rgba(0,0,0,0.04)` |
| Raised | Dropdowns, popovers | `0 4px 16px rgba(0,0,0,0.10)` |
| Floating | Modals, dialogs | `0 8px 32px rgba(0,0,0,0.16)` |
| Overlay | Command palette | `0 16px 64px rgba(0,0,0,0.24)` |

### Surface Hierarchy (Light Mode)

```
Canvas (FAF9F5)           ← Page floor
  └── Surface-soft (F5F0E8)    ← Section backgrounds
        └── Surface-card (EFE9DE)  ← Cards, inputs
              └── Surface-border (E6DFD8)  ← Dividers
```

### Surface Hierarchy (Dark Mode)

```
Dark-base (181715)        ← Page floor
  └── Dark-elevated (252320)   ← Cards, sidebars
        └── Dark-overlay (2E2B27)   ← Dropdowns, modals
              └── Dark-border (3A3630)  ← Dividers
```

---

## 07 — DO'S AND DON'TS

### Do

- Use the serif (EB Garamond / Copernicus) exclusively for display headings
- Keep body text at `body-md` (16px) with generous 1.55 line-height
- Use warm cream (`#FAF9F5`) as the light mode floor — never cold white
- Maintain the dark mode warm charcoal (`#181715`) — never pure black
- Use `brand-coral` only for primary CTAs — not for decorative use
- Let teal (`#5DB8A6`) be the secondary confirmation/success signal
- Pair rounded corners (radius-lg 12px, radius-xl 16px) with soft shadows
- Treat prose blocks with `max-width: 720px` — never full bleed

### Don't

- Don't use cold grays — all surfaces must have a warm undertone
- Don't bold the serif display headings — let weight 400 carry elegance
- Don't use more than two accent colors in one view (coral + one secondary)
- Don't stack box shadows deeper than `0 8px 32px` for in-page elements
- Don't use border-radius below 6px for interactive cards or buttons
- Don't center-align body paragraphs — only titles when decorative
- Don't use stark white (#FFFFFF) backgrounds in light mode
- Don't use code blocks in a sans or serif face — always monospace

---

## 08 — RESPONSIVE BEHAVIOR

### Breakpoints

| Name | Width | Behavior |
|---|---|---|
| Mobile | < 768px | Single column, full-width. Sidebar becomes bottom sheet or hamburger |
| Tablet | 768–1024px | Collapsible sidebar (overlay). Conversation full-width |
| Desktop | 1024–1440px | Fixed 260px sidebar. Conversation centered in remaining space |
| Wide | > 1440px | Sidebar 260px. Conversation max-width 720px, horizontally centered |

### Mobile Adaptations

- Chat input pinned to bottom viewport
- Sidebar becomes modal drawer (slides in from left)
- Display type scales down: `display-xl` → 36px, `display-lg` → 28px
- Spacing scale shifts down by one step (`space-lg` → `space-md` for sections)
- Touch targets minimum 44×44px

### Tablet Adaptations

- Sidebar collapsible via hamburger icon
- Code blocks allow horizontal scroll (no word wrap)
- Two-column card grids collapse to single column

---

## 09 — AGENT PROMPT GUIDE

### Quick Color Reference

```
Light Mode:
  Canvas:      #FAF9F5   Surface:     #F5F0E8   Card:        #EFE9DE
  Ink:         #141413   Body:        #3D3D3A   Muted:       #6C6A64
  Coral:       #CC785C   Teal:        #5DB8A6   Amber:       #E8A55A

Dark Mode:
  Base:        #181715   Elevated:    #252320   Overlay:     #2E2B27
  On-dark:     #FAF9F5   Muted:       #B5AFA7
```

### Ready-to-Use Prompts

```
"Build a Claude-style chat interface following DESIGN.md —
warm cream canvas (#FAF9F5), coral send button, EB Garamond
display headings, Inter body text, chat input with focus ring"

"Create a card grid using DESIGN.md — surface-card (#EFE9DE)
background, 1px hairline border, 12px radius, subtle shadow,
coral accent hover state, teal badge for status"

"Design a sidebar navigation matching DESIGN.md — warm gray
background (#F5F0E8), coral active indicator, 36px item height,
caption-size UPPERCASE section headers, pill badges"

"Build a dark mode variant of the chat UI following DESIGN.md —
warm charcoal base (#181715), elevated panels (#252320),
maintain coral brand accent, on-dark text (#FAF9F5)"

"Create a hero section following DESIGN.md — EB Garamond
display-xl at 64px weight 400, cream canvas background,
coral CTA button, generous 96px section padding"

"Design a code block component matching DESIGN.md — surface-card
background (#EFE9DE), JetBrains Mono 14px, language label header,
copy button, rounded 8px corners, hairline border"
```

### Persona Summary

> Claude's UI is the visual expression of thoughtful intelligence.
> Warm cream and charcoal surfaces create a reading environment —
> never a dashboard. The serif display type signals depth and care.
> Coral punctuates without dominating. When in doubt: more space,
> less decoration, let the words breathe.
