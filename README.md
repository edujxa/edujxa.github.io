# EDUJXA

Projects, records, and things I’m figuring out. Plain HTML, CSS, and local photographs; no JavaScript, package dependencies, analytics, forms, or build step.

## Preview and check

```sh
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
python3 scripts/check-site.py
```

Open http://127.0.0.1:4173. Serve only `dist`, never the repository root.

## GitHub Pages

Source: https://github.com/edujxa/edujxa.github.io. Website: https://edujxa.github.io/.

The site uses GitHub Pages’ built-in publishing from the root of `gh-pages`. That branch contains only the validated contents of `dist/`. The source stays on `main`; a normal source push does not publish. No custom workflow or extra workflow permission is needed.

After committing a change and pushing `main`, publish deliberately with:

```sh
python3 scripts/publish-pages.py
```

The script validates the public files, requires committed source, and pushes a new `gh-pages` commit without force-pushing. It uses the existing GitHub CLI login; it does not store a token. GitHub then publishes that branch automatically.

In **Settings → Pages**, the source is **Deploy from a branch**, `gh-pages`, `/ (root)`, with **Enforce HTTPS** enabled. See [GitHub’s publishing-source documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [HTTPS setup](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

## Editing and privacy

- `dist/index.html`: homepage.
- `dist/writing/`: archive and two posts.
- `dist/styles.css`: shared styles.
- `dist/images/`: website copies of the photos. Strip GPS/EXIF/XMP/IPTC metadata from new images before adding them. Inspect the visible picture for sensitive details too.
- `.local/` and `*-writing-notes.md`: ignored local drafts/research notes; do not force-add them.
- `.openai/hosting.json`: existing private preview configuration; not part of the uploaded Pages artifact.

Each page includes a restrictive meta Content Security Policy (local styles/images only; scripts and forms blocked) and a no-referrer policy. This does not configure server response headers: meta CSP cannot enforce `frame-ancestors`, and HTTPS must be checked on the actual host. See [MDN’s CSP guidance](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP).

The public email, employer, social links, and personal stories are intentional site content. A public source repository also exposes Git history and commit author information. Automated checks catch common accidental exposures; they are not a guarantee that every secret or identifying detail will be detected. GitHub account access and repository permissions remain separate controls.
