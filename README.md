# Personal website mockup

A small, text-first personal website with an about page, writing archive, and two sample posts. Everything served to the browser is plain HTML and CSS in `dist/`; no dependencies or JavaScript are required.

The name, biography, posts, and contact information are placeholders for this mockup. The GitHub link opens GitHub's homepage. Replace these before making the site public and remove the mockup footer labels.

## Preview

Run `python3 -m http.server 4173 --bind 127.0.0.1 --directory dist` from this directory and open `http://127.0.0.1:4173`.

## GitHub Pages

The contents of `dist/` can be published directly as static assets with GitHub Pages. The current private review link uses Sites. A later Jekyll version can reuse this design, use shared layouts, and turn Markdown files into posts automatically.

## Edit

- `dist/index.html`: about page and recent writing.
- `dist/writing/index.html`: writing archive.
- `dist/writing/*/index.html`: individual posts.
- `dist/styles.css`: shared typography, spacing, and responsive layout.
