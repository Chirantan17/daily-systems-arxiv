import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

QUERY = "cat:cs.DC+OR+cat:cs.CR+OR+cat:cs.OS"
URL = f"https://export.arxiv.org/api/query?search_query={QUERY}&sortBy=submittedDate&sortOrder=descending&max_results=5"

def fetch_arxiv_papers(retries=3, delay=5):
    req = urllib.request.Request(URL, headers={"User-Agent": "DailyDigestBot/1.0"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read()
            root = ET.fromstring(content)
            namespace = {"atom": "http://www.w3.org/2005/Atom"}
            papers = []

            for entry in root.findall("atom:entry", namespace):
                title = entry.find("atom:title", namespace).text.strip().replace("\n", " ")
                paper_id = entry.find("atom:id", namespace).text.strip()
                summary = entry.find("atom:summary", namespace).text.strip().replace("\n", " ")
                short_summary = (summary[:130] + "...") if len(summary) > 130 else summary

                category_elem = entry.find("atom:category", namespace)
                category = category_elem.attrib.get("term", "cs") if category_elem is not None else "cs"

                papers.append({
                    "title": title,
                    "url": paper_id,
                    "category": category,
                    "summary": short_summary
                })
            return papers
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
    return []

def update_readme(papers):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    if not papers:
        try:
            with open("README.md", "r", encoding="utf-8") as f:
                existing = f.read()
        except FileNotFoundError:
            existing = "# Daily Distributed Systems & Security Papers\n"
        updated = existing.split("\n*Last checked:")[0].rstrip() + f"\n\n*Last checked: `{today}` (No new announcements or API busy)*\n"
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(updated)
        return

    header = (
        "# 📚 Daily Distributed Systems & Security Papers\n\n"
        "> Automated daily tracker powered by GitHub Actions and the ArXiv API.\n\n"
        f"### Latest Update: `{today}`\n\n"
        "| Category | Paper Title | Summary |\n"
        "| :--- | :--- | :--- |\n"
    )

    rows = [f"| `{p['category']}` | [{p['title']}]({p['url']}) | {p['summary']} |" for p in papers]
    content = header + "\n".join(rows) + f"\n\n---\n*Updated automatically via GitHub Actions.*\n\n*Last checked: `{today}`*\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    latest_papers = fetch_arxiv_papers()
    update_readme(latest_papers)
