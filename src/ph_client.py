"""Product Hunt HTTP client using high-speed Atom feed and redirect resolution."""
import datetime
import html
import logging
import re
import xml.etree.ElementTree as ET
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ProductHuntClient:
    def __init__(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.client = httpx.Client(headers=headers, follow_redirects=True, timeout=15)
        self.raw_client = httpx.Client(headers=headers, follow_redirects=False, timeout=10)

    def fetch_products(self, category="ai", max_items=30, enrich_details=True):
        """Fetches trending/daily products for a specific topic or all launches."""
        if category == "all" or not category:
            target_url = "https://www.producthunt.com/feed"
        else:
            clean_cat = category.strip().lower().replace(" ", "-")
            target_url = f"https://www.producthunt.com/feed?topic={clean_cat}"

        logging.info("Querying Product Hunt feed: %s", target_url)
        resp = self.client.get(target_url)
        if resp.status_code != 200:
            logging.error("Failed to fetch feed %s (HTTP %s)", target_url, resp.status_code)
            return []

        try:
            root = ET.fromstring(resp.text)
        except Exception as e:
            logging.error("XML parse error on feed: %s", e)
            return []

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        logging.info("Discovered %d launch entries in feed", len(entries))

        products = []
        seen = set()
        for e in entries:
            if len(products) >= max_items:
                break

            title_elem = e.find("atom:title", ns)
            link_elem = e.find("atom:link", ns)
            id_elem = e.find("atom:id", ns)
            content_elem = e.find("atom:content", ns)

            name = title_elem.text.strip() if title_elem is not None and title_elem.text else "Product"
            ph_url = link_elem.attrib.get("href", "") if link_elem is not None else ""
            raw_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
            content_text = content_elem.text if content_elem is not None and content_elem.text else ""

            if ph_url in seen:
                continue
            seen.add(ph_url)

            # Extract tagline from first <p>
            p_matches = re.findall(r"<p>\s*(.*?)\s*</p>", content_text, re.DOTALL)
            tagline = html.unescape(p_matches[0].strip()) if p_matches else ""

            # Extract redirect URL to official product site
            redir_match = re.findall(r'href=[\"\'](https://www\.producthunt\.com/r/p/[^\"\']+)[\"\']', content_text)
            clean_website = ""
            raw_website = ""
            if enrich_details and redir_match:
                try:
                    head_resp = self.raw_client.get(redir_match[0])
                    loc = head_resp.headers.get("location") or ""
                    if loc:
                        raw_website = loc
                        clean_website = loc.split("?")[0].rstrip("/")
                except Exception as ex:
                    logging.debug("Could not resolve redirect %s: %s", redir_match[0], ex)

            product_item = {
                "id": raw_id.split("/")[-1] if "/" in raw_id else raw_id,
                "name": name,
                "tagline": tagline,
                "category": category,
                "productHuntUrl": ph_url,
                "websiteUrl": raw_website or clean_website,
                "cleanWebsite": clean_website,
                "description": tagline,
                "votesCount": 0,
                "extractedAt": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

            products.append(product_item)
            logging.info("Extracted product: %s (%s)", name, clean_website or "no website")

        logging.info("Total products successfully extracted: %d", len(products))
        return products
