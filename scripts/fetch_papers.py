import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

# CS categories: Distributed/Cluster/Grid (cs.DC), Cryptography & Security (cs.CR), OS (cs.OS)
QUERY = "cat:cs.DC+OR+cat:cs.CR+OR+cat:cs.OS"
URL = f"http://export.arxiv.org/api/query?search_query={QUERY}&sortBy=submittedDate&sortOrder=descending&max_results=5"

def fetch_arxiv_papers():
    req = urllib.request.Request(URL, headers={"User-Agent": "DailyDigestBot/1.0"})
    with urllib.request.urlopen(req) as response:
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

def update_readme(papers):
    today = datetime.utcnow().strftime("%Y-%m-%d")

    header = (
        "# 📚 Daily Distributed Systems & Security Papers\n\n"
        "> Automated daily tracker powered by GitHub Actions and the ArXiv API.\n\n"
        f"### Latest Update: `{today}`\n\n"
        "| Category | Paper Title | Summary |\n"
        "| :--- | :--- | :--- |\n"
    )

    rows = []
    for p in papers:
        title_link = f"[{p['title']}]({p['url']})"
        rows.append(f"| `{p['category']}` | {title_link} | {p['summary']} |")

    content = header + "\n".join(rows) + "\n\n---\n*Updated automatically via GitHub Actions.*\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    latest_papers = fetch_arxiv_papers()
    if latest_papers:
        update_readme(latest_papers)
