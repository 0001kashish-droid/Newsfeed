import json
import os
import urllib.request
import urllib.error
from datetime import datetime

BUTTONDOWN_API_KEY = os.environ.get('BUTTONDOWN_API_KEY', '4821cd7d-3406-43fb-8b85-ec98c392cbc9')

def send_via_buttondown(subject, markdown_body):
    """Sends the daily digest to all subscribers via the Buttondown REST API."""
    if not BUTTONDOWN_API_KEY:
        print("[BUTTONDOWN] No API key configured. Skipping email delivery.")
        return False

    url = "https://api.buttondown.com/v1/emails"
    payload = json.dumps({
        "subject": subject,
        "body": markdown_body,
        "status": "about_to_send"
    }).encode('utf-8')

    headers = {
        "Authorization": f"Token {BUTTONDOWN_API_KEY}",
        "Content-Type": "application/json",
        "X-Buttondown-Live-Dangerously": "true"
    }

    req = urllib.request.Request(url, data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[BUTTONDOWN SUCCESS] Daily digest dispatched! Email ID: {data.get('id')} (Status: {data.get('status')})")
            return True
    except urllib.error.HTTPError as e:
        err_content = e.read().decode('utf-8', errors='ignore')
        print(f"[BUTTONDOWN ERROR] HTTP {e.code}: {err_content}")
        return False
    except Exception as e:
        print(f"[BUTTONDOWN ERROR] Failed to send email: {e}")
        return False

def generate_newsletter(send_email=True):
    news_file = os.path.join(os.path.dirname(__file__), 'data', 'news.json')
    if not os.path.exists(news_file):
        print(f"Error: {news_file} not found.")
        return

    with open(news_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get('articles', [])
    if not articles:
        print("No articles found.")
        return

    # Sort articles by importance_score (highest first)
    top_articles = sorted(articles, key=lambda a: a.get('importance_score') or 0, reverse=True)[:5]

    today_str = datetime.now().strftime("%B %d, %Y")
    subject_title = f"🌐 News Colossal — Daily Executive Digest: {today_str}"
    
    md_output = f"# 🌐 News Colossal — Daily Executive Digest\n\n"
    md_output += f"**{today_str}** | *Top 5 Noise-Free Macro Intelligence Stories*\n\n"
    md_output += f"> ⚡ **Interactive Experience**: Explore 130+ real-time verified stories, hands-free voice briefings, and interactive 3D global mapping on the live command center at **[News Colossal](https://0001kashish-droid.github.io/Newsfeed/)**.\n\n"
    md_output += f"---\n\n"

    for idx, art in enumerate(top_articles, 1):
        title = art.get('title', 'Untitled Story')
        source = art.get('source', 'Unknown')
        category = art.get('category', 'General')
        region = art.get('region', 'Global')
        link = art.get('link', '#')

        md_output += f"### {idx}. {title}\n"
        md_output += f"**Publisher:** {source} | **Category:** {category} | **Region:** {region}\n\n"
        
        annotation = art.get('annotation') or {}
        if annotation.get('what'):
            md_output += f"**✦ What Happened:** {annotation['what']}\n\n"
        if annotation.get('why'):
            md_output += f"**✦ Why It Matters:** {annotation['why']}\n\n"
            
        md_output += f"🔗 [Read full report on {source}]({link}) • [View on News Colossal](https://0001kashish-droid.github.io/Newsfeed/)\n\n---\n\n"

    md_output += f"### 🚀 Explore News Colossal Overarching Features\n\n"
    md_output += f"- 🌐 **[Live 3D News Command Center](https://0001kashish-droid.github.io/Newsfeed/)** — Full real-time global briefing with interactive category filters and hands-free audio.\n"
    md_output += f"- ☕ **[Support on Ko-fi](https://ko-fi.com/kashishbhushan)** — Fuel ad-free independent news aggregation.\n"
    md_output += f"- 📰 **[Web Archive](https://buttondown.com/0001kashish)** — Read past editions and share with colleagues.\n\n"
    md_output += f"---\n\n"
    md_output += f"*You are receiving this because you subscribed to News Colossal Daily Digest.*"

    # Save to newsletters folder
    newsletters_dir = os.path.join(os.path.dirname(__file__), 'newsletters')
    os.makedirs(newsletters_dir, exist_ok=True)
    output_filename = f"daily_digest_{datetime.now().strftime('%Y_%m_%d')}.md"
    output_path = os.path.join(newsletters_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)

    print(f"[SUCCESS] Newsletter generated: {output_path}")

    # Dispatch email if requested
    if send_email:
        send_via_buttondown(subject_title, md_output)

if __name__ == '__main__':
    generate_newsletter(send_email=True)

