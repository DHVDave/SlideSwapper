---
name: html-to-pptx
description: Convert an HTML presentation to PowerPoint (.pptx) by screenshotting each slide. Use when user has an HTML file with slides and wants a .pptx output.
argument-hint: [html-file] [output-file (optional)]
allowed-tools: Bash, Read, Glob
---

# HTML to PowerPoint Converter

Convert the HTML presentation at `$0` to a PowerPoint file.

## Steps

1. Verify the HTML file exists at the given path. If `$0` is empty or not provided, search the current directory for `.html` files and ask which one to convert.

2. If an output filename was provided as `$1`, use that. Otherwise, default to the same filename with a `.pptx` extension.

3. Check if `html_to_pptx.py` exists in the current directory or repo root. If it does, use it. If not, create the converter script inline (see below).

4. Ensure dependencies are installed:

```bash
pip install playwright python-pptx Pillow 2>/dev/null
playwright install chromium 2>/dev/null
```

5. Run the converter:

```bash
python html_to_pptx.py "$HTML_FILE" -o "$OUTPUT_FILE"
```

6. If Playwright can't find Chromium, try auto-detecting it:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(find ~/.cache -name "chrome" -path "*/chrome-linux/*" 2>/dev/null | head -1) python html_to_pptx.py "$HTML_FILE" -o "$OUTPUT_FILE"
```

7. Confirm success and tell the user where the `.pptx` file was saved.

## Self-contained converter script

If `html_to_pptx.py` is not found anywhere, write this file to the current directory before running it:

```python
#!/usr/bin/env python3
"""Convert an HTML presentation to PowerPoint by screenshotting each slide."""

import argparse
import os
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright
from pptx import Presentation
from pptx.util import Inches

VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

DEFAULT_SLIDE_SELECTORS = [
    "section",
    ".slide",
    "[data-slide]",
]


def find_slides(page, selectors):
    for selector in selectors:
        elements = page.locator(selector)
        count = elements.count()
        if count > 0:
            return selector, count
    return None, 0


def screenshot_slides(html_path, output_dir, slide_selector=None, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT):
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    file_url = html_path.as_uri()
    screenshots = []

    with sync_playwright() as pw:
        executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
        browser = pw.chromium.launch(executable_path=executable, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(file_url, wait_until="networkidle")

        selectors = [slide_selector] if slide_selector else DEFAULT_SLIDE_SELECTORS
        selector, count = find_slides(page, selectors)

        if count == 0:
            print("No slide elements found — capturing full page as a single slide.")
            out = Path(output_dir) / "slide_001.png"
            page.screenshot(path=str(out), full_page=True)
            screenshots.append(out)
        else:
            print(f"Found {count} slides using selector: {selector}")
            for i in range(count):
                element = page.locator(selector).nth(i)
                element.scroll_into_view_if_needed()
                page.wait_for_timeout(200)
                out = Path(output_dir) / f"slide_{i + 1:03d}.png"
                element.screenshot(path=str(out))
                screenshots.append(out)
                print(f"  Captured slide {i + 1}/{count}")

        browser.close()

    return screenshots


def build_pptx(screenshot_paths, output_path, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for img_path in screenshot_paths:
        slide = prs.slides.add_slide(blank_layout)
        with Image.open(img_path) as img:
            img_w, img_h = img.size

        img_aspect = img_w / img_h
        slide_aspect = prs.slide_width / prs.slide_height

        if img_aspect > slide_aspect:
            pic_width = prs.slide_width
            pic_height = int(pic_width / img_aspect)
            left = 0
            top = int((prs.slide_height - pic_height) / 2)
        else:
            pic_height = prs.slide_height
            pic_width = int(pic_height * img_aspect)
            left = int((prs.slide_width - pic_width) / 2)
            top = 0

        slide.shapes.add_picture(str(img_path), left, top, pic_width, pic_height)

    prs.save(output_path)
    print(f"\nPowerPoint saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert an HTML presentation to PowerPoint (.pptx)")
    parser.add_argument("html_file", help="Path to the HTML presentation file")
    parser.add_argument("-o", "--output", default=None, help="Output .pptx file path")
    parser.add_argument("-s", "--selector", default=None, help="CSS selector for slide elements")
    parser.add_argument("--width", type=int, default=VIEWPORT_WIDTH, help="Viewport width in pixels")
    parser.add_argument("--height", type=int, default=VIEWPORT_HEIGHT, help="Viewport height in pixels")
    args = parser.parse_args()

    html_path = Path(args.html_file)
    output_path = args.output or html_path.with_suffix(".pptx")

    with tempfile.TemporaryDirectory(prefix="slideswapper_") as tmp_dir:
        print(f"Screenshotting slides from: {html_path}")
        shots = screenshot_slides(html_path, tmp_dir, args.selector, args.width, args.height)
        print(f"\nBuilding PowerPoint with {len(shots)} slide(s)...")
        build_pptx(shots, output_path, args.width, args.height)


if __name__ == "__main__":
    main()
```

## Optional flags

If the user mentions a custom CSS selector for their slides, pass it with `-s`.
If the user requests a specific resolution, pass `--width` and `--height`.
