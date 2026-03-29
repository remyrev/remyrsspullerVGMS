import requests
import sys

# Configuration from your API documentation
# I added &limit=15 and &gender=f to match your specific needs
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/?wm=uVv1N&client_ip=request_ip&format=json&limit=15&gender=f"
AFFILIATE_TEMPLATE = "https://chaturbate.com/in/?tour=YrCr&campaign=uVv1N&track=rss&room={username}"
OUTPUT_FILE = "cb_trending_feed.xml"

def generate_rss():
    try:
        print(f"Connecting to Chaturbate API...")
        response = requests.get(API_URL, timeout=20)
        response.raise_for_status()
        
        # The API returns a JSON object
        data = response.json()
        rooms = data.get('results', [])

        if not rooms:
            print("API returned 0 rooms. Check your parameters.")
            sys.exit(1)

        rss_items = ""
        for room in rooms:
            name = room.get('username')
            subject = room.get('room_subject', 'Live Now')
            
            # Format your specific affiliate URL
            affiliate_url = AFFILIATE_TEMPLATE.format(username=name)
            
            rss_items += f"""
    <item>
      <title>{name} - {subject}</title>
      <link>{affiliate_url}</link>
      <description>{name} is currently live! Click to watch.</description>
    </item>"""

        rss_content = f"""<?xml version='1.0' encoding='utf-8'?>
<rss version="2.0">
  <channel>
    <title>Trending CB Rooms</title>
    <link>https://chaturbate.com/</link>
    <description>Top 15 trending rooms via Public API</description>
    {rss_items}
  </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_content)
            
        print(f"Success! {OUTPUT_FILE} created with {len(rooms)} rooms.")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()        blacklist = {'/female-cams/', '/male-cams/', '/trans-cams/', '/couple-cams/', '/tags/', '/auth/', '/terms/', '/privacy/', '/help/'}
        
        usernames = []
        for link in links:
            href = link.get('href')
            if href not in blacklist:
                name = href.strip('/')
                if name not in usernames:
                    usernames.append(name)
            
            if len(usernames) >= LIMIT:
                break

        if not usernames:
            print("ERROR: Found 0 usernames. The site layout might have changed.")
            sys.exit(1)

        # Build RSS
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
        print(f"CRITICAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_rss()
