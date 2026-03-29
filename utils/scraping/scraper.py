"""
scraper.py
----------
Scrapes clean text from an arXiv paper URL.
Tries the HTML version first; falls back to the abstract page.
"""

import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def _abs_to_html(url: str) -> str:
    """Convert an arXiv abs URL to its HTML full-text URL."""
    return url.replace("abs", "html")


def _abs_to_pdf_url(url: str) -> str:
    """Convert an arXiv abs URL to its PDF URL (for reference only)."""
    return url.replace("abs", "pdf")


def scrape_arxiv(url: str) -> dict:
    """
    Scrape an arXiv paper and return a dict with:
      - full_text : str  (all paragraph text joined)
      - figures   : list[str]  (figure captions)
      - title     : str
      - source    : str  ('html' | 'abstract')
    """
    result = {
        "full_text": "",
        "figures": [],
        "title": "",
        "source": "",
    }

    # ── 1. Try the HTML full-text version ──────────────────────────────────
    html_url = _abs_to_html(url)
    try:
        resp = requests.get(html_url, headers=HEADERS, timeout=30)
        if resp.status_code == 200 and "<article" in resp.text.lower():
            soup = BeautifulSoup(resp.text, "lxml")

            # Title - try multiple selectors for arXiv HTML
            title_tag = (soup.find("h1", class_="ltx_title") or 
                        soup.find("h1", class_="title") or 
                        soup.find("title") or
                        soup.find("h1"))
            if title_tag:
                result["title"] = title_tag.get_text(separator=" ", strip=True)

            # Body content - extract all text from the main article
            article = soup.find("article") or soup.find("div", class_="ltx_page_main")
            if not article:
                article = soup.find("body")
            
            if article:
                # Extract all text content, preserving structure
                text_parts = []
                
                # Get all text elements in order
                for element in article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'div', 'section']):
                    # Skip if element is empty or contains only whitespace
                    text = element.get_text(separator=" ", strip=True)
                    if text and len(text) > 10:  # Skip very short elements
                        text_parts.append(text)
                
                # Also extract any remaining text that might be missed
                remaining_text = article.get_text(separator=" ", strip=True)
                if remaining_text and len(remaining_text) > len(result["full_text"]):
                    result["full_text"] = remaining_text
                else:
                    result["full_text"] = "\n\n".join(text_parts)
            else:
                # Fallback to all paragraphs
                paragraphs = soup.find_all("p")
                text_parts = [p.get_text(separator=" ", strip=True) for p in paragraphs if p.get_text(strip=True)]
                result["full_text"] = "\n\n".join(text_parts)

            # Figure captions
            for fig in soup.find_all("figcaption"):
                caption = fig.get_text(separator=" ", strip=True)
                if caption:
                    result["figures"].append(caption)

            result["source"] = "html"
            print(f"[Scraper] HTML scrape successful - {len(result['full_text'])} chars")
            print(f"full_text: {result['full_text']}")
            return result
    except Exception as e:
        print(f"[Scraper] HTML scrape failed: {e}")

    # ── 2. Fallback: abstract page ─────────────────────────────────────────
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        # Title
        title_tag = soup.find("h1", class_="title")
        if title_tag:
            result["title"] = title_tag.get_text(separator=" ", strip=True).replace("Title:", "").strip()

        # Abstract block
        abstract_tag = soup.find("blockquote", class_="abstract")
        if abstract_tag:
            result["full_text"] = abstract_tag.get_text(separator=" ", strip=True).replace("Abstract:", "").strip()

        result["source"] = "abstract"
        print(f"[Scraper] WARNING: Fallback to abstract page - {len(result['full_text'])} chars")
        return result
    except Exception as e:
        print(f"[Scraper] ERROR: Abstract fallback also failed: {e}")

    return result
