from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


USER_AGENT = (
    "NGC-AI-Official-Source-Fetcher/1.0 "
    "(Educational college AI project)"
)


def fetch_page(url: str) -> dict:
    """
    Fetch an official webpage and extract readable text.
    """

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

    # Remove elements that don't contain useful page content.
    for element in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer"
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
    """
    Check whether a URL belongs to the same domain.
    """

    base_domain = urlparse(base_url).netloc
    target_domain = urlparse(target_url).netloc

    return base_domain == target_domain


def extract_links(base_url: str, html: str) -> list[str]:
    """
    Extract links belonging to the same official domain.
    """

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]

        absolute_url = urljoin(
            base_url,
            href
        )

        if same_domain(
            base_url,
            absolute_url
        ):
            links.add(absolute_url)

    return sorted(links)

from backend.test_source_fetcher import fetch_page


url = "https://www.telangana.gov.in/"

try:
    result = fetch_page(url)

    print("Source fetched successfully!")
    print()
    print("URL:")
    print(result["url"])

    print()
    print("TITLE:")
    print(result["title"])

    print()
    print("CONTENT PREVIEW:")
    print(result["content"][:1000])

except Exception as e:
    print("SOURCE FETCH FAILED:")
    print(repr(e))