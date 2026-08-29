from pathlib import Path

import pytest

from myproject.myproject import build_site, create_app


@pytest.fixture()
def client():
    app = create_app({"TESTING": True})
    return app.test_client()


@pytest.mark.parametrize("path", ["/", "/research/"])
def test_public_pages_render(client, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "slug",
    ["2021-08-27", "2022-02-22", "2022-10-25"],
)
def test_existing_posts_render(client, slug: str) -> None:
    response = client.get(f"/research/{slug}/")
    assert response.status_code == 200
    assert b"data-pagefind-body" in response.data


def test_missing_post_returns_404(client) -> None:
    assert client.get("/research/does-not-exist/").status_code == 404


@pytest.mark.parametrize(
    ("old_path", "new_path"),
    [
        ("/blog/", "/research/"),
        ("/blog/2022-10-25/", "/research/2022-10-25/"),
    ],
)
def test_old_blog_urls_redirect_permanently(
    client, old_path: str, new_path: str
) -> None:
    response = client.get(old_path)
    assert response.status_code == 301
    assert response.headers["Location"] == new_path


def test_static_site_builds(tmp_path: Path) -> None:
    destination = build_site(tmp_path / "site")

    homepage = destination / "index.html"
    assert homepage.is_file()
    research_index = destination / "research" / "index.html"
    assert research_index.is_file()
    assert (destination / "research" / "2022-10-25" / "index.html").is_file()
    legacy_index = destination / "blog" / "index.html"
    assert "url=../research/" in legacy_index.read_text()
    legacy_post = destination / "blog" / "2022-10-25" / "index.html"
    assert "url=../../research/2022-10-25/" in legacy_post.read_text()
    assert (destination / "static" / "css" / "style.css").is_file()
    assert (destination / "static" / "Kaitlyn_DeValk-Hammond_Resume.pdf").is_file()
    assert (destination / "CNAME").read_text() == "kaitlyndevalk.com\n"
    homepage_html = homepage.read_text()
    assert "Explore My Work" in homepage_html
    assert 'href="#research">View Research</a>' in homepage_html
    assert 'href="#home"' in homepage_html
    assert 'href="#work"' in homepage_html
    assert 'id="home"' in homepage_html
    assert 'id="work"' in homepage_html
    assert "#mainheader" not in homepage_html
    assert "#highlights" not in homepage_html
    assert "Download Résumé" in homepage_html
    assert "Average CrossFitter and Amateur Baker" in homepage_html
    assert "jquery" not in homepage_html.lower()
    assert "bootstrap" not in homepage_html.lower()
    assert "font-awesome" not in homepage_html.lower()
    assert "<pagefind-input" in research_index.read_text()
    oscp_html = (destination / "research" / "2022-02-22" / "index.html").read_text()
    assert 'src="../../../static/img/oscp_tools.png"' in oscp_html
