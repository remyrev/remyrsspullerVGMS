import requests
import sys
import html

# Adding &hd=true ensures the API prioritizes HD-capable rooms
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/?wm=uVv1N&client_ip=request_ip&format=json&limit=15&gender=f&hd=true"
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
            sys.exit(1)

        rss_items = ""
        for room in rooms:
            name = html.escape(room.get('username', ''))
            subject = html.escape(room.get('room_subject', 'Live Now'))
            
            # THE HACK: Grab the standard URL and try to remove the "small" suffix
            # If the API gives us 'image_url', we strip the size tag to find the source
            raw_img = room.get('image_url', '')
            high_res_img = raw_img.replace('_360x270', '').replace('_450x338', '') 
            safe_thumb = html.escape(high_res_img)
            
            raw_url = AFFILIATE_TEMPLATE.format(username=name)
            affiliate_url = html.escape(raw_url)
            
            rss_items += f"""
    <item>
      <title><![CDATA[{name} - {subject}]]></title>
      <link>{affiliate_url}</link>
      <description><![CDATA[{name} is live now.]]></description>
      <media:content url="{safe_thumb}" medium="image" />
    </item>"""

        rss_content = f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/">
  <channel>
    <title>Trending CB Rooms (Max Res)</title>
    <link>https://chaturbate.com/</link>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
        print("Success! Forced higher resolution snapshots.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
