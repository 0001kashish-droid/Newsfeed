import json
import os
import sys
import re
import math
import urllib.request
import urllib.error
from datetime import datetime

# Prevent Windows cp1252 / character encoding crashes across console environments
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

BUTTONDOWN_API_KEY = os.environ.get('BUTTONDOWN_API_KEY', '').strip()


def _sanitize_text(text) -> str:
    """
    Strips HTML <script> tags and executable content from untrusted feed text,
    preserving markdown formatting, quotes, and Unicode characters.
    Handles explicit None, non-string types, and stringified null literals.
    """
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)

    # Iteratively strip complete script blocks including inner script body
    prev = None
    cleaned = text
    while prev != cleaned:
        prev = cleaned
        cleaned = re.sub(
            r'<\s*script[^>]*>.*?<\s*/\s*script\s*>',
            '',
            cleaned,
            flags=re.IGNORECASE | re.DOTALL
        )

    # Strip any unclosed, dangling, or self-closing script tags
    cleaned = re.sub(r'<\s*/?\s*script[^>]*>', '', cleaned, flags=re.IGNORECASE)

    # Collapse multiple whitespace characters into single space
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)
    s = cleaned.strip()

    # Reject stringified null literals
    if s.lower() in ("none", "null", "undefined"):
        return ""
    return s


def _safe_link(art: dict) -> str:
    """
    Safely extracts and validates article URL. Prevents null propagation ('(None)'),
    falls back between 'link' and 'url', and blocks malicious protocols like 'javascript:'.
    """
    if not isinstance(art, dict):
        return '#'

    raw = art.get('link') or art.get('url') or '#'
    if not isinstance(raw, str):
        raw = str(raw)

    cleaned = _sanitize_text(raw)
    if not cleaned or cleaned.lower() in ('none', 'null', 'undefined', '#'):
        return '#'

    if cleaned.lower().startswith(('javascript:', 'data:', 'vbscript:')):
        return '#'

    if cleaned.startswith(('http://', 'https://', '#')):
        return cleaned

    return '#'


def _extract_what(art: dict) -> str:
    """Safely extracts the story summary with non-null and script-free guarantee."""
    raw_ann = art.get('annotation')
    annotation = raw_ann if isinstance(raw_ann, dict) else {}

    # 1. annotation['what']
    what_cand = _sanitize_text(annotation.get('what'))
    if what_cand:
        return what_cand

    # 2. String summary in annotation field
    if isinstance(raw_ann, str):
        ann_str_cand = _sanitize_text(raw_ann)
        if ann_str_cand:
            return ann_str_cand

    # 3. art['description']
    desc_cand = _sanitize_text(art.get('description'))
    if desc_cand:
        return desc_cand

    # 4. Fallback
    return 'Key development details reported.'


def _extract_why(art: dict) -> str:
    """Safely extracts the story impact with non-null and script-free guarantee."""
    raw_ann = art.get('annotation')
    annotation = raw_ann if isinstance(raw_ann, dict) else {}

    why_cand = _sanitize_text(annotation.get('why'))
    if why_cand:
        return why_cand

    return "Key global development with wide-ranging impact across policy, industry, and public interest."


def _safe_importance_score(article: dict) -> float:
    """Safely extracts importance_score as finite float, preventing sorting crashes."""
    if not isinstance(article, dict):
        return 0.0
    val = article.get('importance_score')
    if isinstance(val, bool):
        return 0.0
    try:
        f = float(val or 0)
        return f if math.isfinite(f) else 0.0
    except (ValueError, TypeError):
        return 0.0


def send_via_buttondown(subject, markdown_body):
    """Sends the daily digest to all subscribers via the Buttondown REST API."""
    api_key = os.environ.get('BUTTONDOWN_API_KEY', BUTTONDOWN_API_KEY).strip()
    if not api_key:
        print("[BUTTONDOWN] No API key configured. Skipping email delivery.")
        return False

    url = "https://api.buttondown.com/v1/emails"
    payload = json.dumps({
        "subject": subject,
        "body": markdown_body,
        "status": "about_to_send"
    }).encode('utf-8')

    headers = {
        "Authorization": f"Token {api_key}",
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


def generate_newsletter(send_email=True, news_file=None):
    if isinstance(send_email, str) and news_file is None:
        news_file = send_email
        send_email = True

    if news_file is None:
        news_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'news.json')

    if not os.path.exists(news_file):
        print(f"Error: {news_file} not found.")
        return ""

    with open(news_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get('articles') or []
    if not articles or not isinstance(articles, list):
        print("No articles found.")
        return ""

    # Filter out duplicate articles so duplicates are never featured in daily digest
    valid_articles = [
        a for a in articles
        if isinstance(a, dict) and not (
            a.get('is_duplicate') is True or str(a.get('is_duplicate', '')).lower() == 'true'
        )
    ]
    if not valid_articles:
        print("No valid non-duplicate articles found.")
        return ""

    # Sort articles by importance_score safely (highest first)
    top_articles = sorted(valid_articles, key=_safe_importance_score, reverse=True)[:5]

    today_str = datetime.now().strftime("%B %d, %Y")
    subject_title = f"🌐 News Colossal — Daily Executive Digest: {today_str}"

    md_output = f"# 🌐 News Colossal — Daily Executive Digest\n\n"
    md_output += f"**{today_str}** | *Top 5 Noise-Free Macro Intelligence Stories*\n\n"
    md_output += f"> ⚡ **Interactive Experience**: Explore 130+ real-time verified stories, hands-free voice briefings, and interactive 3D global mapping on the live command center at **[News Colossal](https://0001kashish-droid.github.io/Newsfeed/)**.\n\n"
    md_output += f"---\n\n"

    for idx, art in enumerate(top_articles, 1):
        title = _sanitize_text(art.get('title')) or 'Untitled Story'
        source = _sanitize_text(art.get('source')) or 'Unknown'
        category = _sanitize_text(art.get('category')) or 'General'
        region = _sanitize_text(art.get('region')) or 'Global'
        link = _safe_link(art)

        md_output += f"### {idx}. {title}\n"
        md_output += f"**Publisher:** {source} | **Category:** {category} | **Region:** {region}\n\n"

        what = _extract_what(art)
        why = _extract_why(art)

        md_output += f"**✦ What Happened:** {what}\n\n"
        md_output += f"**✦ Why It Matters:** {why}\n\n"

        md_output += f"🔗 [Read full report on {source}]({link}) • [View on News Colossal](https://0001kashish-droid.github.io/Newsfeed/)\n\n---\n\n"

    md_output += f"### 🚀 Explore News Colossal Overarching Features\n\n"
    md_output += f"- 🌐 **[Live 3D News Command Center](https://0001kashish-droid.github.io/Newsfeed/)** — Full real-time global briefing with interactive category filters and hands-free audio.\n"
    md_output += f"- ☕ **[Support on Ko-fi](https://ko-fi.com/kashishbhushan)** — Fuel ad-free independent news aggregation.\n"
    md_output += f"- 📰 **[Substack Web Archive](https://kashishbhushan.substack.com)** — Read past editions and share with colleagues.\n\n"
    md_output += f"---\n\n"
    md_output += f"*You are receiving this because you subscribed to News Colossal Daily Digest.*"

    # Save to newsletters folder
    newsletters_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'newsletters')
    os.makedirs(newsletters_dir, exist_ok=True)

    now = datetime.now()
    output_filename_legacy = f"daily_digest_{now.strftime('%Y_%m_%d')}.md"
    output_filename_iso = f"{now.strftime('%Y-%m-%d')}.md"
    output_path_legacy = os.path.join(newsletters_dir, output_filename_legacy)
    output_path_iso = os.path.join(newsletters_dir, output_filename_iso)

    with open(output_path_legacy, 'w', encoding='utf-8') as f:
        f.write(md_output)

    with open(output_path_iso, 'w', encoding='utf-8') as f:
        f.write(md_output)

    print(f"[SUCCESS] Newsletter generated: {output_path_iso}")

    # Dispatch email if requested
    if send_email:
        send_via_buttondown(subject_title, md_output)

    return md_output


if __name__ == '__main__':
    generate_newsletter(send_email=True)
