"""Check this intentionally static site's public files before deployment."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re

ROOT = Path(__file__).resolve().parents[1] / "dist"
CSP = "default-src 'none'; img-src 'self'; style-src 'self'; base-uri 'none'; form-action 'none'"
ERRORS = []


def require(condition, path, message):
    if not condition:
        ERRORS.append(f"{path.relative_to(ROOT)}: {message}")


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path, self.ids, self.links = path, set(), []
        self.csp = self.referrer = False
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        require(tag not in {"script", "iframe", "object", "embed", "form", "base", "style"},
                self.path, f"unexpected active element: {tag}")
        require(not any(k.startswith("on") or k in {"style", "srcdoc", "srcset"} for k in a),
                self.path, "unexpected inline behavior or resource attribute")
        if "id" in a:
            require(a["id"] not in self.ids, self.path, "duplicate element ID")
            self.ids.add(a["id"])
        if tag == "h1":
            self.headings += 1
        if tag == "meta":
            if a.get("http-equiv", "").lower() == "content-security-policy":
                self.csp = a.get("content") == CSP
            if a.get("name") == "referrer":
                self.referrer = a.get("content") == "no-referrer"
        if tag == "img":
            require(bool(a.get("alt")) and bool(a.get("width")) and bool(a.get("height")),
                    self.path, "image needs alt text and dimensions")
        for key in ("href", "src"):
            if key not in a:
                continue
            value = a[key] or ""
            url = urlsplit(value)
            if url.scheme or url.netloc:
                require(tag == "a" and key == "href" and url.scheme in {"https", "mailto"},
                        self.path, "unexpected external resource or URL scheme")
                continue
            require(not url.path.startswith("/"), self.path, "use relative links for project Pages")
            target = (self.path.parent / unquote(url.path)).resolve() if url.path else self.path
            if target.is_dir():
                target /= "index.html"
            require(target.is_relative_to(ROOT) and target.is_file(), self.path,
                    f"missing or out-of-site link: {value}")
            self.links.append((target, unquote(url.fragment)))


pages = {}
files = [p for p in ROOT.rglob("*") if p.is_file() or p.is_symlink()]
require((ROOT / "index.html").is_file(), ROOT, "homepage missing")
require((ROOT / ".nojekyll").is_file(), ROOT, ".nojekyll missing")
for path in files:
    require(not path.is_symlink(), path, "symlinks must not be published")
    if path.is_symlink():
        continue
    require(not any(part.startswith(".") for part in path.relative_to(ROOT).parts)
            or path == ROOT / ".nojekyll", path, "hidden file in public output")
    require(path.suffix in {".html", ".css", ".jpg", ".jpeg"} or path.name == ".nojekyll",
            path, "unexpected public file type")
    if path.suffix in {".jpg", ".jpeg"}:
        data = path.read_bytes()
        require(data.startswith(b"\xff\xd8") and data.endswith(b"\xff\xd9"), path, "invalid JPEG")
        # Detect metadata payloads while allowing image and color-profile data.
        require(not any(marker in data for marker in (
            b"Exif\x00\x00", b"http://ns.adobe.com/xap/1.0/", b"http://ns.adobe.com/xmp/extension/",
            b"Photoshop 3.0\x00")), path, "remove personal image metadata before publication")
        continue
    text = path.read_text()
    require(not re.search(r"(?i)localhost|127\.0\.0\.1|/Users/|/home/|sample post|draft posts|mockup", text),
            path, "local reference or draft content")
    require(not re.search(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}|\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{35,}|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b", text),
            path, "possible secret; review before publishing")
    if path.suffix == ".css":
        require(not re.search(r"(?i)@import|url\s*\(", text), path, "unexpected CSS resource loading")
    if path.suffix == ".html":
        page = Page(path)
        page.feed(text)
        require(page.csp and page.referrer, path, "missing expected security policy")
        require(page.headings == 1, path, "expected one main heading")
        pages[path] = page

for path, page in pages.items():
    for target, fragment in page.links:
        if fragment and target in pages:
            require(fragment in pages[target].ids, path, f"missing anchor: {fragment}")

if ERRORS:
    raise SystemExit("\n".join(ERRORS))
print(f"PASS: {len(pages)} pages and {len(files)} public files; links, static-only policy, and image metadata checked.")
