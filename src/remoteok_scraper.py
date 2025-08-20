import requests, csv, re, time, os
from bs4 import BeautifulSoup
from pathlib import Path

def setup_directories():
    """Create necessary directories if they don't exist"""
    Path("../results/csv").mkdir(parents=True, exist_ok=True)
    Path("../results/csv/big_csv").mkdir(parents=True, exist_ok=True)

def scrape_remoteok(keyword):
    """
    Scrapes RemoteOK for jobs matching a keyword.
    Example keyword: 'machine-learning'
    """
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        jobs = []
        for row in soup.select("tr.job"):
            title = row.select_one("h2[itemprop='title']")
            company = row.select_one("h3[itemprop='name']")
            desc = row.select_one("td.description")  # may be short preview
            link = row.get("data-url")

            # extract clean text
            title = title.get_text(strip=True) if title else "N/A"
            company = company.get_text(strip=True) if company else "N/A"
            desc = desc.get_text(strip=True) if desc else "N/A"
            job_url = f"https://remoteok.com{link}" if link else "N/A"

            # Expanded skills list based on the image
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
            found_skills = [s for s in skills_list if re.search(rf"\b{s}\b", desc, re.IGNORECASE)]

            jobs.append({
                "title": title,
                "company": company,
                "url": job_url,
                "description": desc[:200],  # keep first 200 chars
                "skills": ", ".join(found_skills),
                "keyword": keyword  # Add keyword for tracking
            })

        return jobs
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping {keyword}: {e}")
        return []

def save_individual_csv(jobs, keyword):
    """Save jobs to individual CSV file"""
    filename = f"../results/csv/remoteok_{keyword}.csv"
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title","company","url","description","skills","keyword"])
        writer.writeheader()
        writer.writerows(jobs)
    
    print(f"✅ Saved {len(jobs)} {keyword} jobs to {filename}")
    return filename

def combine_all_csvs(keywords):
    """Combine all individual CSV files into one big CSV"""
    all_jobs = []
    
    for keyword in keywords:
        filename = f"../results/csv/remoteok_{keyword}.csv"
        
        if os.path.exists(filename):
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_jobs.append(row)
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    
    # Save combined CSV
    big_csv_filename = "../results/csv/big_csv/remoteok_all_jobs.csv"
    with open(big_csv_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title","company","url","description","skills","keyword"])
        writer.writeheader()
        writer.writerows(all_jobs)
    
    print(f"✅ Combined {len(all_jobs)} jobs from all keywords into {big_csv_filename}")
    return big_csv_filename

def main():
    """Main function to run the scraping process"""
    setup_directories()
    
    # Expanded list of keywords based on the image
    keywords = [
        "machine-learning", "nlp", "ai", "robo", "generative", "ml", "automation",
        "chatgpt", "gpt-4", "prompt-engineering", "scikit-learn", "xgboost", "bert",
        "text-analytics", "text-classification", "image-recognition", "opencv", "yolo",
        "vision-transformer", "robotics", "ros", "responsible-ai", "ai-governance",
        "ai-regulation", "deep-learning", "computer-vision", "natural-language-processing",
        "data-science", "neural-networks", "reinforcement-learning", "data-mining",
        "big-data", "hadoop", "spark", "kubernetes", "docker"
    ]
    
    total_jobs = 0
    all_files = []
    
    # Scrape each keyword and save individual CSV files
    for i, keyword in enumerate(keywords):
        print(f"🔍 Scraping {keyword} jobs ({i+1}/{len(keywords)})...")
        jobs = scrape_remoteok(keyword)
        
        if jobs:
            filename = save_individual_csv(jobs, keyword)
            all_files.append(filename)
            total_jobs += len(jobs)
            
        # Add delay to be respectful to the server
        time.sleep(2)
    
    # Combine all CSV files into one big CSV
    if total_jobs > 0:
        combine_all_csvs(keywords)
        print(f"🎉 Total jobs scraped across all keywords: {total_jobs}")
    else:
        print("❌ No jobs were scraped from any keyword")

if __name__ == "__main__":
    main()