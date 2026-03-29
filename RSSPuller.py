import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys

# --- CONFIGURATION ---
TARGET_URL = "https://www.amazon.com/gp/movers-and-shakers/videogames/ref=zg_bsms_nav_videogames_0"
AFFILIATE_TAG = "saintrem-20"
# Your personal bridge page URL
BRIDGE_BASE = "https://remyrev.github.io/remyrsspullerVGMS/redirect.html"
OUTPUT_FILE = "my_custom_feed.xml"

def generate_amazon_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        print("Fetching Amazon Trending Games...")
        response = requests.get(TARGET_URL, headers=headers, timeout=20)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Amazon usually keeps items in these 'p13n-grid-content' divs
        items = soup.find_all('div', id=lambda x: x and x.startswith('p13n-asin-index-'))
        
        rss_items = ""
        count = 0

        for item in items:
            if count >= 15: break # Keep it light for X
            
            try:
                # 1. Extract Title and ASIN (Product ID)
                title_elem = item.find('div', class_='_cDEBy_p13n-sc-css-line-clamp-3_1796V') or item.find('span')
                title = title_elem.get_text(strip=True) if title_elem else "Great Gaming Deal"
                
                # Get the ASIN from the data-asin attribute or the link
                link_elem = item.find('a', class_='a-link-normal')
                if not link_elem: continue
                
                # Extract ASIN from URL
                href = link_elem.get('href', '')
                asin = href.split('/dp/')[1].split('/')[0] if '/dp/' in href else None
                if not asin: continue

                # 2. CREATE THE MASK (The "Cloak")
                # Direct Affiliate Link
                raw_affiliate_url = f"https://www.amazon.com/dp/{asin}/?tag={AFFILIATE_TAG}"
                
                # URL Encode the Amazon link so it doesn't break our bridge link
                encoded_target = urllib.parse.quote(raw_affiliate_url)
                
                # FINAL MASKED LINK: Your site + the target
                masked_link = f"{BRIDGE_BASE}?target={encoded_target}"

                # 3. Build RSS Item
                rss_items += f"""
    <item>
      <title><![CDATA[Trending: {title}]]></title>
      <link>{masked_link}</link>
      <description>Amazon's current Mover & Shaker in Video Games.</description>
    </item>"""
                count += 1
                
            except Exception as e:
                print(f"Skipping an item due to error: {e}")
                continue

        # 4. Wrap it in the XML Shell
        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Amazon Gaming Movers</title>
    <link>{TARGET_URL}</link>
    <description>Top trending game deals, masked for X.</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        print(f"Success! {OUTPUT_FILE} created with {count} masked links.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_amazon_feed()
