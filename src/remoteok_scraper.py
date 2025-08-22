import requests, csv, re, time, os
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta

# ---------- Setup ----------
def setup_directories():
    Path("../results/csv").mkdir(parents=True, exist_ok=True)
    Path("../results/csv/big_csv").mkdir(parents=True, exist_ok=True)

# ---------- AI Category ----------
def get_ai_category_from_keyword(keyword):
    category_mapping = {
        # Generative AI
        "chatgpt": "Generative AI", "generative": "Generative AI", "gpt-4": "Generative AI",
        "prompt-engineering": "Generative AI", "llm": "Generative AI",
        # Machine Learning
        "machine-learning": "Machine Learning", "ml": "Machine Learning", 
        "scikit-learn": "Machine Learning", "tensorflow": "Machine Learning",
        "xgboost": "Machine Learning", "deep-learning": "Machine Learning",
        "neural-networks": "Machine Learning", "reinforcement-learning": "Machine Learning",
        "data-mining": "Machine Learning",
        # NLP
        "nlp": "NLP", "bert": "NLP", "text-analytics": "NLP",
        "text-classification": "NLP", "natural-language-processing": "NLP",
        # Computer Vision
        "computer-vision": "Computer Vision", "image-recognition": "Computer Vision",
        "opencv": "Computer Vision", "yolo": "Computer Vision", "vision-transformer": "Computer Vision",
        # Robotics / RPA
        "robo": "Robotics/RPA", "robotics": "Robotics/RPA", "ros": "Robotics/RPA",
        "automation": "Robotics/RPA", "rpa": "Robotics/RPA",
        # AI Ethics/Policy
        "responsible-ai": "AI Ethics/Policy", "ai-governance": "AI Ethics/Policy", "ai-regulation": "AI Ethics/Policy",
        # Data Science
        "data-science": "Data Science", "big-data": "Data Science", "hadoop": "Data Science", "spark": "Data Science",
        # DevOps
        "kubernetes": "DevOps", "docker": "DevOps"
    }
    return category_mapping.get(keyword, "Other AI")

# ---------- Sector Detection ----------
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
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", text):
                return sector
    return "Other AI"

# ---------- Skills Extraction ----------
def extract_skills(description):
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
    found = [s for s in skills_list if re.search(rf"\b{s}\b", description, re.IGNORECASE)]
    return ", ".join(found)

# ---------- Date Parsing ----------
def parse_relative_date(relative_date):
    try:
        date_str = relative_date.replace("ago", "").strip()
        if "d" in date_str:
            days = int(date_str.replace("d", "").strip())
            return (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        elif "h" in date_str:
            return datetime.now().strftime("%Y-%m-%d")
        else:
            return datetime.now().strftime("%Y-%m-%d")
    except:
        return datetime.now().strftime("%Y-%m-%d")

# ---------- Scraper ----------
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
            time_elem = row.select_one("td.time")
            location_elem = row.select_one("div.location") or row.select_one("td.location")
            link = row.get("data-url")

            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"
            job_url = f"https://remoteok.com{link}" if link else "N/A"
            date_posted = parse_relative_date(time_elem.get_text(strip=True)) if time_elem else datetime.now().strftime("%Y-%m-%d")
            location = location_elem.get_text(strip=True) if location_elem else "N/A"

            ai_category = get_ai_category_from_keyword(keyword)
            sector = get_sector_from_text(title + " " + desc)
            skills = extract_skills(desc) if extract_skills(desc) else "None listed"

            jobs.append({
                "Job Title": title,
                "Company Name": company,
                "AI Category": ai_category,
                "Sector": sector,
                "Skills Mentioned": skills,
                "Job Description": desc[:200],
                "Date Posted": date_posted,
                "Location": location,
                "Source Website": "RemoteOK",
                "Link to Job Post": job_url
            })


        return jobs
    except Exception as e:
        print(f"❌ Error scraping {keyword}: {e}")
        return []

# ---------- Save CSV ----------
def save_individual_csv(jobs, keyword):
    if not jobs: return None
    filename = f"../results/csv/remoteok_{keyword}.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Job Title","Company Name","AI Category","Sector","Skills Mentioned","Job Description","Date Posted","Location","Source Website","Link to Job Post"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
    print(f"✅ Saved {len(jobs)} {keyword} jobs to {filename}")
    return filename

# ---------- Combine CSV ----------
def combine_all_csvs(keywords):
    all_jobs = []
    for keyword in keywords:
        filename = f"../results/csv/remoteok_{keyword}.csv"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                all_jobs.extend(reader)

    big_csv_filename = "../results/csv/big_csv/remoteok_all_jobs.csv"
    with open(big_csv_filename, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["Job Title","Company Name","AI Category","Sector","Skills Mentioned","Job Description","Date Posted","Source Website","Link to Job Post","Keyword"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_jobs)
    print(f"✅ Combined {len(all_jobs)} jobs into {big_csv_filename}")
    return big_csv_filename

# ---------- Main ----------
def main():
    setup_directories()
    keywords = ["chatgpt","machine-learning"]  # test small first
    total_jobs = 0

    for keyword in keywords:
        print(f"🔍 Scraping {keyword}...")
        jobs = scrape_remoteok(keyword)
        if jobs:
            save_individual_csv(jobs, keyword)
            total_jobs += len(jobs)
        time.sleep(2)

    if total_jobs > 0:
        combine_all_csvs(keywords)
        print(f"🎉 Total jobs scraped: {total_jobs}")
    else:
        print("❌ No jobs were scraped")

if __name__ == "__main__":
    main()
