import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from typing import List
logger = logging.getLogger(__name__)
REQUEST_TIMEOUT_SECONDS = 15
USER_AGENT = "Mozilla/5.0 (compatible; AIKnowledgeStudio/1.0; +https://example.com/bot)"
MAX_CONTENT_BYTES = 10 * 1024 * 1024

NOISE_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript"]

def load_web(url :str , doc_id : str) -> list[Document]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http" , "https") or not parsed.netloc:
        raise ValueError(f"Invalid URL: '{url}'. Must include scheme (http/https) and a domain.")
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(
            url , 
            headers=headers,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream = True, 
            allow_redirects=  True, 
        
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout fetching '{url}'")
        raise ValueError(f"Request to '{url}' timed out after {REQUEST_TIMEOUT_SECONDS}s") from e
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error fetching '{url}': {e}")
        raise ValueError(f"'{url}' returned HTTP error: {response.status_code}") from e
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error fetching '{url}': {e}")
        raise
    content_type = response.headers.get("Content-Type", "")
    if "text/html" not in content_type:
        raise ValueError(f"'{url}' is not an HTML page (Content-Type: {content_type})")
    content_length = int(response.headers.get("Content-Length", 0))
    if content_length > MAX_CONTENT_BYTES:
        raise ValueError(f"'{url}' content exceeds max allowed size ({MAX_CONTENT_BYTES} bytes)")
    
    html = response.text
    soup = BeautifulSoup(html , "html.parser")
    for tag_name in NOISE_TAGS:
        for tag in soup.find_all(tag_name):
            tag.decompose()
    page_title = soup.title.string.strip() if soup.title and soup.title.string else url
    main_content = soup.find("main") or soup.find("article") or soup.find("body")
    if main_content is None:
        raise ValueError(f"Could not locate any body content in '{url}'")

    text = main_content.get_text(separator="\n", strip=True)
    text = "\n".join(line for line in text.splitlines() if line.strip())
    if len(text) < 50:
        raise ValueError(f"'{url}' produced negligible extractable text ({len(text)} chars) — likely JS-rendered content")

    doc = Document(
        page_content=text,
        metadata={
            "source": url,
            "doc_id": doc_id,
            "page_title": page_title,
            "domain": parsed.netloc,
            "file_type": "web",
            "char_count": len(text),
        },
    )

    logger.info(f"Loaded web page '{url}': {len(text)} chars, title='{page_title}'")
    return [doc]


