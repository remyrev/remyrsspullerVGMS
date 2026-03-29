import requests
import sys
import html

# Official API Configuration
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/?wm=uVv1N&client_ip=request_ip&format=json&limit=15&gender=f"
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
OUTPUT_FILE = "cb_trending_feed.xml"

def generate_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=20)
        response.raise_for_status()
        data = response.json()
        rooms = data.get('results', [])

        if not rooms:
            print("No rooms found.")
            sys.exit(1)

        rss_items = ""
        for room in rooms:
            name = html.escape(room.get('username', ''))
            subject = html.escape(room.get('room_subject', 'Live Now'))
            
            # 1. Grab the image URL from the API
            thumb_url = room.get('image_url_360x270', '')
            safe_thumb = html.escape(thumb_url)
            
            raw_url = AFFILIATE_TEMPLATE.format(username=name)
            affiliate_url = html.escape(raw_url)
            
            # 2. We add the <media:content> tag so IFTTT can "see" the image
            rss_items += f"""
    <item>
      <title><![CDATA[{name} - {subject}]]></title>
      <link>{affiliate_url}</link>
      <description><![CDATA[{name} is live now.]]></description>
      <media:content url="{safe_thumb}" medium="image" />
    </item>"""

        # 3. We add the xmlns:media line to the header to enable media tags
        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Trending CB Rooms</title>
    <link>https://chaturbate.com/</link>
    <description>Top 15 Trending with Images</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print("Success! RSS feed updated with Media tags.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
