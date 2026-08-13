from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "NGC-AI-Official-Source-Fetcher/1.0 "
    "(Educational college AI project)"
)


def fetch_page(url: str) -> dict:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=20,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
    ]):
        element.decompose()

    title = ""

    if soup.title:
        title = soup.title.get_text(
            " ",
            strip=True
        )

    text = soup.get_text(
        " ",
        strip=True
    )

    return {
        "url": response.url,
        "title": title,
        "content": text,
        "status_code": response.status_code,
    }


def same_domain(base_url: str, target_url: str) -> bool:
    return (
        urlparse(base_url).netloc
        == urlparse(target_url).netloc
    )


def extract_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")

    links = set()

    for anchor in soup.find_all("a", href=True):
        absolute_url = urljoin(
            base_url,
            anchor["href"]
        )

        if same_domain(
            base_url,
            absolute_url
        ):
            links.add(absolute_url)

    return sorted(links)