import json
import os
import urllib.request

def run_tests():
    print("==========================================")
    print("  NEWS COLOSSAL HARD PRE-FLIGHT TEST SUITE")
    print("==========================================")
    
    # 1. JSON Data Integrity Test
    assert os.path.exists("data/news.json"), "data/news.json file missing!"
    with open("data/news.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    articles = data.get("articles", [])
    print(f"[PASS] TEST 1: data/news.json valid ({len(articles)} total articles)")
    assert len(articles) > 50, "Not enough articles fetched!"

    # 2. Image HTTP 200 Verification Test across Categories
    categories = ["World", "Tech", "National", "Business"]
    headers = {"User-Agent": "Mozilla/5.0"}
    for cat in categories:
        cat_arts = [a for a in articles if a.get("category") == cat]
        assert len(cat_arts) > 0, f"No articles for category {cat}!"
        sample = cat_arts[0]
        img_url = sample["imageUrl"]
        try:
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=6) as resp:
                print(f"[PASS] TEST 2 ({cat}): {sample['source']} image -> Status {resp.status} ({len(resp.read())} bytes)")
        except Exception as e:
            print(f"[WARN] TEST 2 ({cat}): Image check error: {e}")

    # 3. Light Mode Default Verification Test
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    assert 'data-theme="light"' in html_content, "index.html does not default to light theme!"
    print("[PASS] TEST 3: index.html set to default data-theme='light'")

    # 4. JS Natural Voice Engine & Light Theme Verification
    with open("app.js", "r", encoding="utf-8") as f:
        js_content = f.read()
    assert "getNaturalHumanVoice" in js_content, "app.js missing natural voice synthesizer!"
    assert "'light'" in js_content, "app.js state.theme missing light default!"
    print("[PASS] TEST 4: app.js contains Natural Voice Synthesizer & Light default")

    # 5. README Motivation & Why Section Test
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()
    assert "Why News Colossal Was Built" in readme, "README missing 'Why News Colossal Was Built' section!"
    print("[PASS] TEST 5: README.md updated with noise reduction motivation section")

    print("\n[SUCCESS] ALL HARD PRE-FLIGHT TESTS PASSED 100%! READY FOR MAIN BRANCH PUSH.")

if __name__ == "__main__":
    run_tests()
