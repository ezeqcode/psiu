"""Assemble video.html from the real PSIU page: its stylesheet, cutout filters, illustrations and mark."""
import re
from pathlib import Path

WORK = Path(__file__).parent
APP = WORK.parents[1] / "public" / "index.html"

app = APP.read_text()


def first(pattern: str) -> str:
    match = re.search(pattern, app, flags=re.S)
    if not match:
        raise SystemExit(f"not found in index.html: {pattern}")
    return match.group(0)


pieces = {
    "{{APP_CSS}}": re.search(r"<style>(.*?)</style>", app, flags=re.S).group(1),
    "{{DEFS}}": first(r'<svg class="defs".*?</svg>'),
    "{{ART_PEDIR}}": first(r'<svg class="art" id="artPedir".*?</svg>\s*(?=\n\s*<h1>)'),
    "{{ART_ENVIAR}}": first(r'<svg class="art is-open" id="artEnviar".*?</svg>\s*(?=\n\s*<div id="sendPaste">)'),
    "{{MARK}}": first(r'<svg class="mark".*?</svg>'),
}

html = (WORK / "video.template.html").read_text()
for key, value in pieces.items():
    html = html.replace(key, value)
# the Enviar art starts open in the video and snaps shut by script
html = html.replace('class="art is-open" id="artEnviar"', 'class="art" id="artEnviar"')

(WORK / "video.html").write_text(html)
print("video.html", len(html), "bytes")
