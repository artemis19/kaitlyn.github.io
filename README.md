# Kaitlyn's Korner

Kaitlyn's portfolio, projects, and cybersecurity research site. Flask, Jinja,
and Markdown are used locally to author the site; Frozen-Flask builds the static
HTML published to GitHub Pages. Pagefind provides browser-side full-text search.

## Local development

Install [`uv`](https://docs.astral.sh/uv/), then create the locked environment:

```bash
uv sync
```

Run the local authoring server:

```bash
uv run python -m myproject.myproject serve
```

Open <http://localhost:5000>.

## Static preview

Build the production site and its search index:

```bash
uv run python -m myproject.myproject build
uv run python -m pagefind --site build --serve
```

Pagefind prints the local preview URL. The generated `build/` directory is not
committed; GitHub Actions recreates and deploys it for every push to `main`.

## Quality checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest
```

Install the optional local Git hooks with `uv run pre-commit install`.

## Publishing

The `Deploy GitHub Pages` workflow freezes the site, creates the Pagefind index,
and publishes the resulting artifact. The root `CNAME` file configures the Pages
site for `kaitlyndevalk.com`. In the repository's **Settings → Pages**, select
**GitHub Actions** as the publishing source before the first deployment.
