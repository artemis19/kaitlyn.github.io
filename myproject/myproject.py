"""Local authoring server and static-site builder for Kaitlyn's Korner."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path
from typing import Any

from flask import Flask, redirect, render_template, url_for
from flask_flatpages import FlatPages
from flask_frozen import Freezer

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUILD_DIR = PROJECT_ROOT / "build"
CUSTOM_DOMAIN_FILE = PROJECT_ROOT / "CNAME"
POST_DIR = "blog_posts"


def create_app(config: dict[str, Any] | None = None) -> Flask:
    """Create the local Flask application used for authoring and freezing."""
    app = Flask(__name__)
    app.config.from_mapping(
        FLATPAGES_AUTO_RELOAD=False,
        FLATPAGES_EXTENSION=".md",
        FLATPAGES_MARKDOWN_EXTENSIONS=["fenced_code", "tables"],
        FLATPAGES_ROOT="content",
        FREEZER_DESTINATION=str(DEFAULT_BUILD_DIR),
        FREEZER_IGNORE_MIMETYPE_WARNINGS=True,
        FREEZER_RELATIVE_URLS=True,
        PAGEFIND_ENABLED=False,
        STATIC_EXPORT=False,
    )
    if config:
        app.config.update(config)

    pages = FlatPages(app)
    freezer = Freezer(app)

    def all_posts() -> list[Any]:
        posts = [page for page in pages if page.path.startswith(POST_DIR)]
        return sorted(posts, key=lambda item: item["date"], reverse=True)

    @app.get("/")
    def index() -> str:
        return render_template("index.html", posts=all_posts()[:3])

    @app.get("/research/")
    def research() -> str:
        return render_template("posts.html", posts=all_posts())

    @app.get("/research/<name>/")
    def research_post(name: str) -> str:
        page = pages.get_or_404(f"{POST_DIR}/{name}")
        return render_template("post.html", post=page)

    @app.get("/blog/")
    def legacy_blog():
        destination = url_for("research")
        if app.config["STATIC_EXPORT"]:
            return render_template("redirect.html", destination="../research/")
        return redirect(destination, code=301)

    @app.get("/blog/<name>/", endpoint="legacy_post")
    def legacy_post_route(name: str):
        destination = url_for("research_post", name=name)
        if app.config["STATIC_EXPORT"]:
            static_destination = f"../../research/{name}/"
            return render_template("redirect.html", destination=static_destination)
        return redirect(destination, code=301)

    @freezer.register_generator
    def post_urls():
        for page in all_posts():
            name = page.path.removeprefix(f"{POST_DIR}/")
            yield url_for("research_post", name=name)

    @freezer.register_generator
    def legacy_post():
        for page in all_posts():
            name = page.path.removeprefix(f"{POST_DIR}/")
            yield {"name": name}

    app.extensions["kaitlyn_freezer"] = freezer
    return app


def build_site(destination: Path = DEFAULT_BUILD_DIR) -> Path:
    """Freeze the complete static site into ``destination``."""
    build_app = create_app(
        {
            "FREEZER_DESTINATION": str(destination.resolve()),
            "PAGEFIND_ENABLED": True,
            "STATIC_EXPORT": True,
        }
    )
    build_app.extensions["kaitlyn_freezer"].freeze()
    shutil.copyfile(CUSTOM_DOMAIN_FILE, destination / "CNAME")
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    serve_parser = subparsers.add_parser("serve", help="run the local authoring server")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", default=5000, type=int)

    build_parser = subparsers.add_parser("build", help="build the static site")
    build_parser.add_argument("--destination", default=DEFAULT_BUILD_DIR, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.command == "build":
        destination = build_site(args.destination)
        print(f"Static site built in {destination.resolve()}")
        return

    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    local_app = create_app({"FLATPAGES_AUTO_RELOAD": debug})
    local_app.run(
        host=getattr(args, "host", "127.0.0.1"),
        port=getattr(args, "port", 5000),
        debug=debug,
    )


app = create_app()


if __name__ == "__main__":
    main()
