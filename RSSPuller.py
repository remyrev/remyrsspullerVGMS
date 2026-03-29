import requests
from bs4 import BeautifulSoup
import urllib.parse
import sys
import re
import html

# --- CONFIGURATION ---
TARGET_URL = "https://www.amazon.com/gp/movers-and-shakers/videogames/"
AFFILIATE_TAG = "saintrem-20"
BRIDGE_BASE = "https://remyrev.github.io/remyrsspullerVGMS/redirect.html"
OUTPUT_FILE = "my_custom_feed.xml"

def generate_amazon_feed():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br"
    }

    try:
        print(f"Connecting to Amazon Movers & Shakers...")
        response = requests.get(TARGET_URL, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Look for the Product Containers (the "Cards")
        # Amazon uses specific classes for these grid items
        items = soup.find_all('div', id=lambda x: x and x.startswith('p13n-asin-index-'))
        
        if not items:
            # Fallback for different layout versions
            items = soup.find_all('li', class_='zg-item-immersion')

        rss_items = ""
        count = 0

        for item in items:
            if count >= 15: break
            
            try:
                # 2. Extract ASIN (Product ID)
                # Look for the link inside the item
                link_elem = item.find('a', href=re.compile(r'/dp/[A-Z0-9]{10}'))
                if not link_elem: continue
                
                href = link_elem.get('href', '')
                asin = re.search(r'/dp/([A-Z0-9]{10})', href).group(1)
                
                # 3. Extract the TITLE (The missing piece)
                # The image 'alt' tag is the most stable source for the title
                img_elem = item.find('img')
                raw_title = img_elem.get('alt', '').strip() if img_elem else ""
                
                # If image alt is missing, try looking for the specific title div
                if not raw_title:
                    title_elem = item.find('div', class_='_cDEBy_p13n-sc-css-line-clamp-3_1796V')
                    raw_title = title_elem.get_text(strip=True) if title_elem else f"Game {asin}"

                print(f"Found: {raw_title}") # This shows up in your GitHub Action logs

                # 4. Construct & Mask the Link
                raw_affiliate_url = f"https://www.amazon.com/dp/{asin}/?tag={AFFILIATE_TAG}"
                encoded_target = urllib.parse.quote(raw_affiliate_url, safe='')
                masked_link = f"{BRIDGE_BASE}?target={encoded_target}"
                safe_link = html.escape(masked_link)

                rss_items += f"""
    <item>
      <title><![CDATA[{raw_title}]]></title>
      <link>{safe_link}</link>
      <description><![CDATA[Trending now in Video Games.]]></description>
    </item>"""
                count += 1
            except Exception as e:
                continue

        if count == 0:
            print("ERROR: Could not find products. Amazon might have updated their layout.")
            sys.exit(1)

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0">
  <channel>
    <title>Amazon Gaming Deals</title>
    <link>{TARGET_URL}</link>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        
        print(f"Success! Captured {count} titles.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_amazon_feed()
