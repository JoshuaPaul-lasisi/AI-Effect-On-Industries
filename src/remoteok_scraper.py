import requests, csv, re, time, os
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta

# --- Setup Directories ---
def setup_directories():
    Path("../results/csv").mkdir(parents=True, exist_ok=True)
    Path("../results/csv/big_csv").mkdir(parents=True, exist_ok=True)

# --- AI Category Mapping ---
def get_ai_category_from_keyword(keyword):
    category_mapping = {
        "chatgpt": "Generative AI",
        "generative": "Generative AI", "gpt-4": "Generative AI", "prompt-engineering": "Generative AI", "llm": "Generative AI",
        "machine-learning": "Machine Learning", "ml": "Machine Learning", "scikit-learn": "Machine Learning", 
        "tensorflow": "Machine Learning", "xgboost": "Machine Learning", "deep-learning": "Machine Learning",
        "neural-networks": "Machine Learning", "reinforcement-learning": "Machine Learning", "data-mining": "Machine Learning",
        "nlp": "NLP", "bert": "NLP", "text-analytics": "NLP", "text-classification": "NLP", "natural-language-processing": "NLP",
        "computer-vision": "Computer Vision", "image-recognition": "Computer Vision", "opencv": "Computer Vision",
        "yolo": "Computer Vision", "vision-transformer": "Computer Vision",
        "robo": "Robotics/RPA", "robotics": "Robotics/RPA", "ros": "Robotics/RPA", "automation": "Robotics/RPA", "rpa": "Robotics/RPA",
        "responsible-ai": "AI Ethics/Policy", "ai-governance": "AI Ethics/Policy", "ai-regulation": "AI Ethics/Policy",
        "data-science": "Data Science", "big-data": "Data Science", "hadoop": "Data Science", "spark": "Data Science",
        "kubernetes": "DevOps", "docker": "DevOps"
    }
    return category_mapping.get(keyword, "Other AI")

# --- Sector Classification ---
def get_sector_from_text(text):
    text = text.lower()
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
    for sector, keywords in sector_keywords.items():
        if any(kw in text for kw in keywords):
            return sector
    return "Other AI"

# --- Skill Extraction ---
def extract_skills(text):
    skills_list = [
        "Python","TensorFlow","PyTorch","SQL","AWS","GCP","Azure","LangChain","OpenCV","RPA",
        "ChatGPT","Generative AI","LLM","GPT-4","Prompt Engineering","Scikit-learn","XGBoost","BERT","NLP",
        "Text Analytics","Text Classification","Image Recognition","YOLO","Vision Transformer","Automation",
        "Robotics","ROS","Responsible AI","AI governance","AI regulation","Machine Learning","Deep Learning",
        "Computer Vision","Natural Language Processing","Data Science","ML","AI","Neural Networks",
        "Reinforcement Learning","Data Mining","Big Data","Hadoop","Spark","Kubernetes","Docker"
    ]
    found = [s for s in skills_list if re.search(rf"\b{s}\b", text, re.IGNORECASE)]
    return ", ".join(found)

# --- Parse Relative Date ---
def parse_relative_date(relative_date):
    try:
        relative_date = relative_date.lower().replace("ago", "").strip()
        if "d" in relative_date:
            days = int(relative_date.replace("d","").strip())
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        elif "h" in relative_date:
            return datetime.now().strftime("%Y-%m-%d")
        return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

# --- Full Job Page Extraction ---
def extract_full_description(job_url, headers):
    try:
        resp = requests.get(job_url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        selectors = ["div[itemprop='description']", ".description", ".job-description", "article"]
        for sel in selectors:
            block = soup.select_one(sel)
            if block:
                return block.get_text(" ", strip=True)
        return ""
    except:
        return ""

# --- Main Scraper ---
def scrape_remoteok(keyword):
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}
    jobs = []

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for row in soup.select("tr.job"):
            title = row.select_one("h2[itemprop='title']")
            company = row.select_one("h3[itemprop='name']")
            location = row.select_one("div.location")
            time_elem = row.select_one("td.time")
            link = row.get("data-url")

            title = title.get_text(strip=True) if title else "N/A"
            company = company.get_text(strip=True) if company else "N/A"
            location = location.get_text(strip=True) if location else "Remote"
            job_url = f"https://remoteok.com{link}" if link else "N/A"
            date_posted = parse_relative_date(time_elem.get_text(strip=True)) if time_elem else datetime.now().strftime("%Y-%m-%d")

            # --- Short description fallback ---
            desc_elem = row.select_one("td.description")
            short_desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"

            # --- Full description + skills ---
            full_desc = ""
            all_skills = extract_skills(short_desc)
            if job_url != "N/A":
                full_desc = extract_full_description(job_url, headers)
                if full_desc:
                    all_skills = extract_skills(full_desc)
                time.sleep(1)  # be polite per job

            sector = get_sector_from_text(full_desc or short_desc)
            ai_category = get_ai_category_from_keyword(keyword)

            jobs.append({
                "Job Title": title,
                "Company Name": company,
                "Job Description": full_desc[:1000] if full_desc else short_desc,
                "Skills Mentioned": all_skills,
                "Link to Job Post": job_url,
                "Location": location,
                "Sector": sector,
                "AI Category": ai_category,
                "Date Posted": date_posted,
                "Source Website": "RemoteOK"
            })

        return jobs
    except Exception as e:
        print(f"❌ Error scraping {keyword}: {e}")
        return []

# --- Save CSV ---
def save_individual_csv(jobs, keyword):
    filename = f"../results/csv/remoteok_{keyword}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=jobs[0].keys())
        writer.writeheader()
        writer.writerows(jobs)
    print(f"✅ Saved {len(jobs)} {keyword} jobs to {filename}")
    return filename

# --- Main ---
def main():
    setup_directories()
    keywords = ["chatgpt", "machine-learning"]  # test small first

    total = 0
    for kw in keywords:
        print(f"🔍 Scraping {kw}...")
        jobs = scrape_remoteok(kw)
        if jobs:
            save_individual_csv(jobs, kw)
            total += len(jobs)
        time.sleep(3)  # polite delay between keywords

    print(f"🎉 Total jobs scraped: {total}")

if __name__ == "__main__":
    main()