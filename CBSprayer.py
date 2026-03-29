import requests
from bs4 import BeautifulSoup
import re

# Your Configuration
TARGET_URL = "https://chaturbate.com/teen-cams/female/"
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
OUTPUT_FILE = "cb_trending_feed.xml"
LIMIT = 15

def generate_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(TARGET_URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all room links. They usually look like /username/
        # We look for <a> tags where the href starts with / and ends with /
        links = soup.find_all('a', href=re.compile(r'^/[a-zA-Z0-9_-]+/$'))
        
        # Blacklist of common non-username paths on the site
        blacklist = {'/female-cams/', '/male-cams/', '/trans-cams/', '/couple-cams/', '/tags/', '/auth/', '/terms/', '/privacy/', '/help/'}
        
        usernames = []
        for link in links:
            href = link.get('href')
            if href not in blacklist:
                # Clean the username (remove slashes)
                name = href.strip('/')
                if name not in usernames:
                    usernames.append(name)
            
            if len(usernames) >= LIMIT:
                break

        # Build the RSS structure
        rss_items = ""
        for name in usernames:
            affiliate_url = AFFILIATE_TEMPLATE.format(username=name)
            rss_items += f"""
    <item>
      <title>{name} is Live</title>
      <link>{affiliate_url}</link>
      <description>Check out {name} on the trending list.</description>
    </item>"""

        rss_content = f"""<?xml version='1.0' encoding='utf-8'?>
<rss version="2.0">
  <channel>
    <title>Trending CB Female Cams</title>
    <link>{TARGET_URL}</link>
    <description>Top 15 trending rooms with affiliate tracking.</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print(f"Successfully generated {OUTPUT_FILE} with {len(usernames)} items.")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    generate_rss()
