import os
import requests
import urllib3
from bs4 import BeautifulSoup

# Suppress insecure request warnings for unverified HTTPS connections
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PublicCaseScraper:
    """Scraper designed to extract case progression data from public court pages or local files."""

    def __init__(self):
        """Initializes the scraper with necessary configuration, including browser headers."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def scrape_jusbrasil_or_public(self, url_or_path: str) -> str:
        """
        Determines the source (local file or URL), fetches the HTML content,
        and extracts relevant text blocks representing legal movements.
        """
        html_content = ""

        if os.path.exists(url_or_path):
            print(f"[DEBUG] Reading from local file: {url_or_path}")
            with open(url_or_path, "r", encoding="utf-8", errors="ignore") as file_handler:
                html_content = file_handler.read()
        else:
            try:
                response = requests.get(url_or_path, headers=self.headers, timeout=15, verify=False)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                print(f"[ERROR] Falha ao fazer o scraping da URL {url_or_path}: {e}")
                return ""

        extracted_text = []
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Target standard HTML elements commonly used to structure case movements
        target_tags = ["div", "li", "p", "tr"]
        movements = soup.find_all(target_tags)

        for mov in movements:
            text = " ".join(mov.get_text(separator=" ", strip=True).split())
            
            # Filter out short, non-informational UI text
            if text and len(text) > 25: 
                extracted_text.append(text)

        # Remove duplicate entries caused by nested HTML elements
        extracted_text = list(dict.fromkeys(extracted_text))

        return "\n".join(extracted_text)
