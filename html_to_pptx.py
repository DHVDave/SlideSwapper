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


# Default viewport matching a 16:9 slide at 2x for crisp screenshots
VIEWPORT_WIDTH = 1920
VIEWPORT_HEIGHT = 1080

# Common CSS selectors for slide elements across popular frameworks
DEFAULT_SLIDE_SELECTORS = [
    "section",           # reveal.js, generic
    ".slide",            # common convention
    "[data-slide]",      # data attribute convention
]


def find_slides(page, selectors):
    """Try each selector until we find slides. Returns a list of locators."""
    for selector in selectors:
        elements = page.locator(selector)
        count = elements.count()
        if count > 0:
            return selector, count
    return None, 0


def screenshot_slides(html_path, output_dir, slide_selector=None, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT):
    """Open the HTML file in a headless browser and screenshot each slide.

    Returns a list of screenshot file paths in slide order.
    """
    html_path = Path(html_path).resolve()
    if not html_path.exists():
        print(f"Error: HTML file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    file_url = html_path.as_uri()
    screenshots = []

    with sync_playwright() as pw:
        # Use PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH env var if set, otherwise auto-detect
        executable = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH")
        browser = pw.chromium.launch(executable_path=executable, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(file_url, wait_until="networkidle")

        # Determine which selector finds slides
        selectors = [slide_selector] if slide_selector else DEFAULT_SLIDE_SELECTORS
        selector, count = find_slides(page, selectors)

        if count == 0:
            # Fallback: screenshot the entire page as one slide
            print("No slide elements found — capturing full page as a single slide.")
            out = Path(output_dir) / "slide_001.png"
            page.screenshot(path=str(out), full_page=True)
            screenshots.append(out)
        else:
            print(f"Found {count} slides using selector: {selector}")
            for i in range(count):
                element = page.locator(selector).nth(i)

                # Scroll element into view and wait for any animations
                element.scroll_into_view_if_needed()
                page.wait_for_timeout(200)

                out = Path(output_dir) / f"slide_{i + 1:03d}.png"
                element.screenshot(path=str(out))
                screenshots.append(out)
                print(f"  Captured slide {i + 1}/{count}")

        browser.close()

    return screenshots


def build_pptx(screenshot_paths, output_path, width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT):
    """Create a PowerPoint file with each screenshot as a full-bleed slide image."""
    prs = Presentation()

    # Set slide dimensions to 16:9 widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]  # blank layout

    for img_path in screenshot_paths:
        slide = prs.slides.add_slide(blank_layout)

        # Get image dimensions to maintain aspect ratio
        with Image.open(img_path) as img:
            img_w, img_h = img.size

        img_aspect = img_w / img_h
        slide_aspect = prs.slide_width / prs.slide_height

        # Fit image to slide, centering if aspect ratios differ
        if img_aspect > slide_aspect:
            # Image is wider — fit to width
            pic_width = prs.slide_width
            pic_height = int(pic_width / img_aspect)
            left = 0
            top = int((prs.slide_height - pic_height) / 2)
        else:
            # Image is taller — fit to height
            pic_height = prs.slide_height
            pic_width = int(pic_height * img_aspect)
            left = int((prs.slide_width - pic_width) / 2)
            top = 0

        slide.shapes.add_picture(str(img_path), left, top, pic_width, pic_height)

    prs.save(output_path)
    print(f"\nPowerPoint saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert an HTML presentation to PowerPoint (.pptx)",
        epilog="Example: python html_to_pptx.py presentation.html -o output.pptx",
    )
    parser.add_argument("html_file", help="Path to the HTML presentation file")
    parser.add_argument("-o", "--output", default=None, help="Output .pptx file path (default: same name as input)")
    parser.add_argument("-s", "--selector", default=None, help="CSS selector for slide elements (auto-detected if omitted)")
    parser.add_argument("--width", type=int, default=VIEWPORT_WIDTH, help=f"Viewport width in pixels (default: {VIEWPORT_WIDTH})")
    parser.add_argument("--height", type=int, default=VIEWPORT_HEIGHT, help=f"Viewport height in pixels (default: {VIEWPORT_HEIGHT})")

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
