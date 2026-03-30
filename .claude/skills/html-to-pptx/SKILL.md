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

3. Run the converter script:

```bash
python html_to_pptx.py "$HTML_FILE" -o "$OUTPUT_FILE"
```

If `html_to_pptx.py` is not in the current directory, look for it at the root of the repository. If dependencies are missing, install them first:

```bash
pip install -r requirements.txt
playwright install chromium
```

4. If the script fails because Playwright can't find Chromium, try setting the environment variable to a known Chromium path:

```bash
PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=$(find /root/.cache -name "chrome" -path "*/chrome-linux/*" 2>/dev/null | head -1) python html_to_pptx.py "$HTML_FILE" -o "$OUTPUT_FILE"
```

5. Confirm success and tell the user where the `.pptx` file was saved.

## Optional flags

If the user mentions a custom CSS selector for their slides, pass it with `-s`:

```bash
python html_to_pptx.py "$HTML_FILE" -o "$OUTPUT_FILE" -s "$SELECTOR"
```

If the user requests a specific resolution, pass `--width` and `--height`.
