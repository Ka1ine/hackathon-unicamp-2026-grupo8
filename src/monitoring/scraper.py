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
        path_str = str(url_or_path)
        html_content = ""

        if os.path.exists(path_str):
            print(f"[DEBUG] Reading from local file: {path_str}")
            with open(path_str, "r", encoding="utf-8", errors="ignore") as file_handler:
                html_content = file_handler.read()
        elif path_str.startswith("http"):
            try:
                # Reduce timeout to 5 seconds to prevent long loading states
                response = requests.get(path_str, headers=self.headers, timeout=5, verify=False)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                print(f"[ERROR] Failed scraping URL {path_str}: {e}")
                return ""
        else:
            print(f"[ERROR] Path not found and not a valid URL: {path_str}")
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
