---
name: make-slides
description: Generate a complete HTML presentation from a topic or outline, then convert it to PowerPoint (.pptx). Use when user wants to create a presentation from scratch.
argument-hint: [topic or description of the presentation]
allowed-tools: Bash, Read, Write, Glob
---

# Generate Presentation and Convert to PowerPoint

Create a professional HTML presentation based on the user's request, then convert it to PowerPoint.

## Step 1: Generate the HTML presentation

Write a single self-contained HTML file called `presentation.html` in the current directory. The presentation must follow these rules:

- Each slide is a `<section>` element (so the converter can auto-detect them)
- Each section is exactly `width: 1920px; height: 1080px` (16:9 at 1x)
- Use `display: flex` with centering for slide layout
- All styles are inline or in a `<style>` block (no external dependencies)
- Use modern, visually appealing design with gradients, good typography, and contrast
- Include 5-10 slides unless the user specifies otherwise
- Structure: title slide, content slides, closing/summary slide

The user's request: $ARGUMENTS

## Step 2: Convert to PowerPoint

Use the `/html-to-pptx` skill to convert:

```
/html-to-pptx presentation.html presentation.pptx
```

If the `/html-to-pptx` skill is not available, follow these steps manually:

1. Ensure dependencies are installed:

```bash
pip install playwright python-pptx Pillow 2>/dev/null
playwright install chromium 2>/dev/null
```

2. Check if `html_to_pptx.py` exists in the current directory or repo root. If not, create it using the converter script embedded in the `/html-to-pptx` skill documentation, or write it fresh following the same pattern: use Playwright to screenshot each `<section>` element, then use python-pptx to assemble them into a widescreen .pptx.

3. Run:

```bash
python html_to_pptx.py presentation.html -o presentation.pptx
```

4. If Playwright can't find Chromium:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(find ~/.cache -name "chrome" -path "*/chrome-linux/*" 2>/dev/null | head -1) python html_to_pptx.py presentation.html -o presentation.pptx
```

## Step 3: Confirm

Tell the user:
- The HTML file is at `presentation.html` (they can iterate on this)
- The PowerPoint is at `presentation.pptx`
- They can re-run `/html-to-pptx presentation.html` after editing the HTML to regenerate the .pptx
