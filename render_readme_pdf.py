"""Render README.md to README.pdf using headless Chrome.

Usage:
    python3 render_readme_pdf.py             # renders ./README.md -> ./README.pdf
    python3 render_readme_pdf.py INPUT.md    # custom input (output is INPUT.pdf)
    python3 render_readme_pdf.py INPUT.md OUTPUT.pdf

Requirements:
    - Google Chrome installed at the standard macOS path.
    - Python `markdown` package. If missing, the script installs it for the
      current user automatically.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = os.path.join(PROJECT_DIR, "README.md")
DEFAULT_OUTPUT = os.path.join(PROJECT_DIR, "README.pdf")

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]

CSS = """
:root { color-scheme: light; }
body {
  font-family: -apple-system, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 12pt;
  line-height: 1.55;
  color: #1f2328;
  max-width: 880px;
  margin: 0 auto;
  padding: 1.2em 1.4em 2em;
}
h1, h2, h3, h4, h5, h6 { font-weight: 700; line-height: 1.25; margin-top: 1.4em; margin-bottom: 0.5em; }
h1 { font-size: 2em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
h2 { font-size: 1.5em; border-bottom: 1px solid #d0d7de; padding-bottom: 0.25em; }
h3 { font-size: 1.2em; }
h4 { font-size: 1.05em; }
p, ul, ol, blockquote, table, pre { margin: 0.6em 0 1em; }
a { color: #0969da; text-decoration: none; }
a:hover { text-decoration: underline; }
code {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.88em;
  background: #f3f4f6;
  padding: 0.15em 0.35em;
  border-radius: 4px;
}
pre {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.85em;
  background: #f6f8fa;
  padding: 0.9em 1em;
  border-radius: 6px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
pre code { background: transparent; padding: 0; font-size: 1em; }
blockquote { border-left: 4px solid #d0d7de; color: #57606a; padding: 0.1em 1em; margin-left: 0; }
table { border-collapse: collapse; width: 100%; font-size: 0.92em; }
table th, table td { border: 1px solid #d0d7de; padding: 6px 10px; text-align: center; }
table th { background: #f6f8fa; font-weight: 600; }
img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 1.6em 0; }
sup, sub { font-size: 0.75em; }
@page { size: A4; margin: 15mm; }
"""


def ensure_markdown_pkg():
    try:
        import markdown
        return markdown
    except ImportError:
        pass

    print("[setup] Installing `markdown` package for current user...", flush=True)
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--user", "--quiet", "markdown"]
    )
    # The --user site is on sys.path by default for non-conda envs; otherwise
    # add it explicitly so this same process can import it without restarting.
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.insert(0, user_site)
    import markdown
    return markdown


def find_chrome():
    for path in CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    raise RuntimeError(
        "Could not find Chrome/Chromium. Looked in:\n  " + "\n  ".join(CHROME_CANDIDATES)
    )


def md_to_html(markdown_mod, md_text, base_uri):
    body = markdown_mod.markdown(
        md_text,
        extensions=["fenced_code", "tables", "attr_list", "sane_lists"],
        output_format="html5",
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <base href="{base_uri}">
  <title>README</title>
  <style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def render_pdf(chrome_path, html_path, pdf_path, timeout_s=90):
    user_data_dir = tempfile.mkdtemp(prefix="_chrome_pdf_")
    try:
        cmd = [
            chrome_path,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--no-sandbox",
            # Wait up to 10s for any deferred work (image loads, web fonts, etc.)
            # before printing. This also helps Chrome exit promptly afterwards.
            "--virtual-time-budget=10000",
            f"--user-data-dir={user_data_dir}",
            f"--print-to-pdf={pdf_path}",
            "file://" + html_path,
        ]
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=True)
        except subprocess.TimeoutExpired:
            # Headless Chrome sometimes hangs *after* writing the PDF. If the
            # file exists and looks valid, treat the run as successful.
            if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1024:
                print(
                    f"[warn] Chrome did not exit within {timeout_s}s, but PDF was written. "
                    "Continuing.",
                    flush=True,
                )
            else:
                raise
    finally:
        shutil.rmtree(user_data_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Render a markdown file to PDF via headless Chrome.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, help="Markdown file to render (default: README.md)")
    parser.add_argument("output", nargs="?", default=None, help="Output PDF path (default: <input>.pdf)")
    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        sys.exit(f"Input markdown file not found: {input_path}")
    output_path = os.path.abspath(args.output) if args.output else os.path.splitext(input_path)[0] + ".pdf"
    if input_path == DEFAULT_INPUT and args.output is None:
        output_path = DEFAULT_OUTPUT

    markdown_mod = ensure_markdown_pkg()
    chrome_path = find_chrome()

    with open(input_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    base_uri = "file://" + os.path.dirname(input_path) + "/"
    html_doc = md_to_html(markdown_mod, md_text, base_uri)

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".html", delete=False
    ) as tmp:
        tmp.write(html_doc)
        tmp_html = tmp.name

    try:
        render_pdf(chrome_path, tmp_html, output_path)
    finally:
        try:
            os.remove(tmp_html)
        except OSError:
            pass

    print(f"[done] Wrote {output_path} ({os.path.getsize(output_path):,} bytes)")


if __name__ == "__main__":
    main()
