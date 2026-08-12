import json
import os
from datetime import datetime

def generate_newsletter():
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
    
    md_output = f"# 🌐 News Colossal — Daily Executive Digest\n"
    md_output += f"**{today_str}** | *Top 5 Noise-Free Macro Stories*\n\n---\n\n"

    for idx, art in enumerate(top_articles, 1):
        md_output += f"### {idx}. {art.get('title', 'Untitled Story')}\n"
        md_output += f"**Publisher:** {art.get('source', 'Unknown')} | **Category:** {art.get('category', 'General')} | **Region:** {art.get('region', 'Global')}\n\n"
        
        annotation = art.get('annotation') or {}
        if annotation.get('what'):
            md_output += f"**✦ What Happened:** {annotation['what']}\n\n"
        if annotation.get('why'):
            md_output += f"**✦ Why It Matters:** {annotation['why']}\n\n"
            
        md_output += f"🔗 [Read full story on {art.get('source', 'Unknown')}]({art.get('link', '#')})\n\n---\n\n"

    md_output += f"*Generated automatically by News Colossal Intelligence Engine.*"

    newsletters_dir = os.path.join(os.path.dirname(__file__), 'newsletters')
    os.makedirs(newsletters_dir, exist_ok=True)
    output_filename = f"daily_digest_{datetime.now().strftime('%Y_%m_%d')}.md"
    output_path = os.path.join(newsletters_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_output)

    print(f"[SUCCESS] Newsletter generated: {output_path}")

if __name__ == '__main__':
    generate_newsletter()

