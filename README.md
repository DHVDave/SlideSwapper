# SlideSwapper

Convert HTML presentations to PowerPoint (.pptx) by screenshotting each slide.

## How it works

1. Opens your HTML file in a headless Chromium browser (via Playwright)
2. Detects slide elements automatically (`<section>`, `.slide`, `[data-slide]`) or uses a custom CSS selector
3. Screenshots each slide at 1920×1080 for crisp output
4. Assembles the screenshots into a widescreen PowerPoint file

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

```bash
# Basic — auto-detects slides, outputs presentation.pptx
python html_to_pptx.py presentation.html

# Custom output path
python html_to_pptx.py presentation.html -o my_deck.pptx

# Custom slide selector
python html_to_pptx.py presentation.html -s ".my-slide-class"

# Custom viewport size
python html_to_pptx.py presentation.html --width 2560 --height 1440
```

## Supported HTML structures

The tool auto-detects slides using these selectors (in order):

| Selector       | Frameworks / Conventions       |
|----------------|-------------------------------|
| `section`      | reveal.js, generic            |
| `.slide`       | Common convention             |
| `[data-slide]` | Data attribute convention     |

If none match, the full page is captured as a single slide.

You can always override with `-s "your-selector"`.
