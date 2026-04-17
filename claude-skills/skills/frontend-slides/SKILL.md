---
name: "frontend-slides"
description: >
  HTML slide decks and PPTX-to-web presentation workflows. Covers Reveal.js,
  Marp, and custom CSS presentations. Activate for slide deck work.
metadata:
  version: 1.0.0
  category: content
---

# Frontend Slides Skill

## Tool Selection

| Need | Tool |
|---|---|
| Code-heavy technical slides | Reveal.js |
| Markdown-to-slides fast | Marp |
| Designer-quality output | HTML/CSS from scratch |
| PPTX → Web | LibreOffice → HTML export + cleanup |

## Reveal.js Starter

```html
<!DOCTYPE html>
<html>
<head>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/theme/white.css">
</head>
<body>
  <div class="reveal"><div class="slides">

    <section>
      <h1>Title Slide</h1>
      <p>Subtitle or tagline</p>
    </section>

    <section>
      <h2>Point with Code</h2>
      <pre><code data-trim class="language-python">
def hello():
    print("Hello, world!")
      </code></pre>
    </section>

    <section data-auto-animate>
      <h2>Animated slide</h2>
    </section>

  </div></div>
  <script src="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js"></script>
  <script>Reveal.initialize({ hash: true, plugins: [RevealHighlight] });</script>
</body>
</html>
```

## Marp Markdown (Quick)

```markdown
---
marp: true
theme: default
paginate: true
---

# Title Slide

---

## Agenda

- Point 1
- Point 2
- Point 3

---

## Code Example

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

---
```

Build: `npx @marp-team/marp-cli slides.md -o slides.html`

## Slide Design Principles

- Max 30 words per slide
- One concept per slide
- Code: max 10-15 lines visible without scrolling
- Diagrams > bullet points for complex relationships
- Dark code backgrounds on light slides (or vice versa)

## PPTX to Web Workflow

```bash
# Convert PPTX to HTML
libreoffice --headless --convert-to html presentation.pptx

# Clean up generated HTML (remove inline styles, normalize)
# Then style with CSS to match brand
```
