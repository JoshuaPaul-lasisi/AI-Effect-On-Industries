import requests, csv, re, time, os, argparse
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta

# -------------------------------
# Setup
# -------------------------------
def setup_directories():
    """Create necessary directories if they don't exist"""
    Path("../results/csv").mkdir(parents=True, exist_ok=True)
    Path("../results/csv/big_csv").mkdir(parents=True, exist_ok=True)

# -------------------------------
# AI category mapping (by keyword)
# -------------------------------
def get_ai_category_from_keyword(keyword):
    category_mapping = {
        "chatgpt": "Generative AI",
        "generative": "Generative AI", 
        "gpt-4": "Generative AI",
        "prompt-engineering": "Generative AI",
        "llm": "Generative AI",
        "machine-learning": "Machine Learning",
        "ml": "Machine Learning",
        "scikit-learn": "Machine Learning",
        "tensorflow": "Machine Learning",
        "xgboost": "Machine Learning",
        "deep-learning": "Machine Learning",
        "neural-networks": "Machine Learning",
        "reinforcement-learning": "Machine Learning",
        "data-mining": "Machine Learning",
        "nlp": "NLP",
        "bert": "NLP",
        "text-analytics": "NLP",
        "text-classification": "NLP",
        "natural-language-processing": "NLP",
        "computer-vision": "Computer Vision",
        "image-recognition": "Computer Vision",
        "opencv": "Computer Vision",
        "yolo": "Computer Vision",
        "vision-transformer": "Computer Vision",
        "robo": "Robotics/RPA",
        "robotics": "Robotics/RPA",
        "ros": "Robotics/RPA",
        "automation": "Robotics/RPA",
        "rpa": "Robotics/RPA",
        "responsible-ai": "AI Ethics/Policy",
        "ai-governance": "AI Ethics/Policy",
        "ai-regulation": "AI Ethics/Policy",
        "data-science": "Data Science",
        "big-data": "Data Science",
        "hadoop": "Data Science",
        "spark": "Data Science",
        "kubernetes": "DevOps",
        "docker": "DevOps"
    }
    return category_mapping.get(keyword, "Other AI")

# -------------------------------
# Sector mapping (from title/desc)
# -------------------------------
def get_sector_from_text(text):
    sector_keywords = {
        "Healthcare": ["health", "medical", "pharma", "biotech", "hospital", "patient", "clinical", "healthcare"],
        "Finance": ["finance", "bank", "investment", "insurance", "fintech", "financial", "trading", "wealth"],
        "Marketing & Media": ["marketing", "media", "advertising", "social media", "content", "brand", "digital marketing"],
        "Education": ["education", "edtech", "learning", "university", "school", "course", "training", "academic"],
        "Legal & Compliance": ["legal", "compliance", "regulation", "law", "governance", "policy", "regulatory"],
        "Technology & Software": ["tech", "software", "saas", "platform", "application", "system", "developer", "engineering"],
        "Manufacturing & Logistics": ["manufacturing", "logistics", "supply chain", "production", "factory", "shipping", "distribution"],
        "Government & Public Policy": ["government", "public", "policy", "federal", "state", "municipal", "public sector"]
    }
    text = text.lower()
    for sector, keywords in sector_keywords.items():
        if any(kw in text for kw in keywords):
            return sector
    return "Other AI"

# -------------------------------
# Parse relative date ("2d ago")
# -------------------------------
def parse_relative_date(relative_date):
    try:
        date_str = relative_date.replace('ago', '').strip()
        if 'd' in date_str:
            days = int(date_str.replace('d', '').strip())
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        elif 'h' in date_str:
            return datetime.now().strftime("%Y-%m-%d")
        else:
            return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

# -------------------------------
# Scrape job listings
# -------------------------------
def scrape_remoteok(keyword):
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        jobs = []
        for row in soup.select("tr.job"):
            title_elem = row.select_one("h2[itemprop='title']")
            company_elem = row.select_one("h3[itemprop='name']")
            desc_elem = row.select_one("td.description")
            link = row.get("data-url")
            location_elem = row.select_one("div.location.tooltip")
            time_elem = row.select_one("td.time")

            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            short_desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"
            job_url = f"https://remoteok.com{link}" if link else "N/A"
            location = location_elem.get_text(strip=True) if location_elem else "Remote"
            date_posted = parse_relative_date(time_elem.get_text(strip=True)) if time_elem else datetime.now().strftime("%Y-%m-%d")

            jobs.append({
                "Job Title": title,
                "Company Name": company,
                "AI Category": get_ai_category_from_keyword(keyword),
                "Sector": get_sector_from_text(title),
                "Skills Mentioned": "",  # will enrich later
                "Job Description": short_desc,
                "Date Posted": date_posted,
                "Location": location,
                "Source Website": "RemoteOK",
                "Link to Job Post": job_url
            })
        return jobs

    except Exception as e:
        print(f"❌ Error scraping {keyword}: {e}")
        return []

# -------------------------------
# Save jobs to CSV
# -------------------------------
def save_csv(jobs, keyword):
    if not jobs: return None
    filename = f"../results/csv/remoteok_{keyword}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
    print(f"✅ Saved {len(jobs)} jobs → {filename}")
    return filename

# -------------------------------
# Enrichment: fetch full job desc + skills
# -------------------------------
def extract_skills_from_description(description):
    skills_list = [
        "Python", "TensorFlow", "PyTorch", "SQL", "AWS", "GCP", "Azure", 
        "LangChain", "OpenCV", "RPA", "ChatGPT", "Generative AI", "LLM", 
        "GPT-4", "Prompt Engineering", "Scikit-learn", "XGBoost", "BERT", 
        "NLP", "Text Analytics", "Text Classification", "Image Recognition", 
        "YOLO", "Vision Transformer", "Automation", "Robotics", "ROS",
        "Responsible AI", "AI governance", "AI regulation", "Machine Learning",
        "Deep Learning", "Computer Vision", "Natural Language Processing",
        "Data Science", "ML", "AI", "Neural Networks", "Reinforcement Learning",
        "Data Mining", "Big Data", "Hadoop", "Spark", "Kubernetes", "Docker"
    ]
    found = [s for s in skills_list if re.search(rf"\b{re.escape(s)}\b", description, re.IGNORECASE)]
    return ", ".join(found)

def enrich_jobs(filename):
    enriched = []
    headers = {"User-Agent": "Mozilla/5.0"}
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            job_url = row["Link to Job Post"]
            if job_url and job_url != "N/A":
                try:
                    resp = requests.get(job_url, headers=headers, timeout=20)
                    soup = BeautifulSoup(resp.text, "html.parser")
                    desc_elem = soup.select_one("div[itemprop='description']") or soup.select_one(".description")
                    if desc_elem:
                        full_desc = desc_elem.get_text(strip=True)
                        row["Job Description"] = full_desc[:1000]
                        row["Skills Mentioned"] = extract_skills_from_description(full_desc)
                    time.sleep(5)  # polite delay
                except Exception as e:
                    print(f"⚠️ Could not fetch {job_url}: {e}")
            enriched.append(row)

    # overwrite enriched file
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=enriched[0].keys())
        writer.writeheader()
        writer.writerows(enriched)
    print(f"✨ Enriched {len(enriched)} jobs → {filename}")

# -------------------------------
# Main runner
# -------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["scrape", "enrich", "full"], help="Run mode")
    args = parser.parse_args()

    setup_directories()
    keywords = ["machine-learning", "nlp", "ai", "chatgpt", "gpt-4", "data-science", "docker"]

    if args.mode in ("scrape", "full"):
        for kw in keywords:
            print(f"🔍 Scraping {kw}...")
            jobs = scrape_remoteok(kw)
            save_csv(jobs, kw)
            time.sleep(2)

    if args.mode in ("enrich", "full"):
        for kw in keywords:
            filename = f"../results/csv/remoteok_{kw}.csv"
            if os.path.exists(filename):
                enrich_jobs(filename)

if __name__ == "__main__":
    main()