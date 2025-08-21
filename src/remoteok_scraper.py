import requests, csv, re, time, os
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

def setup_directories():
    """Create necessary directories if they don't exist"""
    Path("../results/csv").mkdir(parents=True, exist_ok=True)
    Path("../results/csv/big_csv").mkdir(parents=True, exist_ok=True)

def get_ai_category(title, description):
    """Determine AI category based on keywords in title and description"""
    text = f"{title} {description}".lower()
    
    categories = {
        "Machine Learning": ["machine learning", "ml", "neural network", "deep learning"],
        "NLP": ["nlp", "natural language", "text processing", "bert", "gpt", "chatgpt"],
        "Computer Vision": ["computer vision", "image recognition", "opencv", "yolo", "vision transformer"],
        "Generative AI": ["generative ai", "gpt-4", "llm", "large language model", "prompt engineering"],
        "Robotics": ["robotics", "ros", "robot", "automation"],
        "Data Science": ["data science", "data mining", "big data", "hadoop", "spark"],
        "AI Ethics": ["responsible ai", "ai governance", "ai regulation", "ethical ai"]
    }
    
    found_categories = []
    for category, keywords in categories.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
                found_categories.append(category)
                break
    
    return ", ".join(found_categories) if found_categories else "Other AI"

def get_sector(company_name, description):
    """Assign sector based on company name or job description"""
    text = f"{company_name} {description}".lower()
    
    sectors = {
        "Technology": ["tech", "software", "ai", "machine learning", "data", "cloud"],
        "Healthcare": ["health", "medical", "pharma", "biotech", "hospital"],
        "Finance": ["finance", "bank", "investment", "insurance", "fintech"],
        "E-commerce": ["ecommerce", "e-commerce", "retail", "shop", "marketplace"],
        "Education": ["education", "edtech", "learning", "university", "school"],
        "Manufacturing": ["manufacturing", "factory", "production", "industrial"],
        "Consulting": ["consulting", "consultancy", "advisory"],
        "Media": ["media", "entertainment", "publishing", "content"],
        "Transportation": ["transport", "logistics", "shipping", "delivery"]
    }
    
    for sector, keywords in sectors.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
                return sector
    
    return "Other"

def extract_skills(description):
    """Extract skills from job description"""
    skills_list = [
        "Python", "TensorFlow", "PyTorch", "SQL", "AWS", "GCP", "Azure", 
        "LangChain", "OpenCV", "RPA", "ChatGPT", "Generative AI", "LLM", 
        "GPT-4", "Prompt Engineering", "Scikit-learn", "XGBoost", "BERT", 
        "NLP", "Text Analytics", "Text Classification", "Image Recognition", 
        "YOLO", "Vision Transformer", "Automation", "Robotics", "ROS",
        "Responsible AI", "AI governance", "AI regulation", "Machine Learning",
        "Deep Learning", "Computer Vision", "Natural Language Processing",
        "Data Science", "ML", "AI", "Neural Networks", "Reinforcement Learning",
        "Data Mining", "Big Data", "Hadoop", "Spark", "Kubernetes", "Docker",
        "JavaScript", "React", "Node.js", "Java", "C++", "Git", "Linux",
        "MLflow", "Kubeflow", "Airflow", "Tableau", "Power BI", "Matplotlib",
        "Seaborn", "Pandas", "NumPy", "Spark", "Hadoop", "Kafka", "Redis"
    ]
    
    found_skills = [s for s in skills_list if re.search(rf"\b{s}\b", description, re.IGNORECASE)]
    return ", ".join(found_skills)

def get_location(row):
    """Extract location information if available"""
    location_elem = row.select_one(".location")
    if location_elem:
        return location_elem.get_text(strip=True)
    return "Remote"

def get_date_posted(row):
    """Extract date posted information"""
    time_elem = row.select_one("time")
    if time_elem and time_elem.get('datetime'):
        return time_elem['datetime']
    
    # Fallback: current date
    return datetime.now().strftime("%Y-%m-%d")

def scrape_remoteok(keyword):
    """
    Scrapes RemoteOK for jobs matching a keyword.
    """
    url = f"https://remoteok.com/remote-{keyword}-jobs"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        jobs = []
        for row in soup.select("tr.job"):
            # Extract basic information
            title_elem = row.select_one("h2[itemprop='title']")
            company_elem = row.select_one("h3[itemprop='name']")
            desc_elem = row.select_one("td.description")
            link = row.get("data-url")
            
            # Get text content
            title = title_elem.get_text(strip=True) if title_elem else "N/A"
            company = company_elem.get_text(strip=True) if company_elem else "N/A"
            description = desc_elem.get_text(strip=True) if desc_elem else "N/A"
            job_url = f"https://remoteok.com{link}" if link else "N/A"
            
            # Get additional information
            location = get_location(row)
            date_posted = get_date_posted(row)
            
            # Extract derived information
            ai_category = get_ai_category(title, description)
            sector = get_sector(company, description)
            skills = extract_skills(description)

            jobs.append({
                "Job Title": title,
                "Company Name": company,
                "AI Category": ai_category,
                "Sector": sector,
                "Skills Mentioned": skills,
                "Job Description": description,
                "Date Posted": date_posted,
                "Location": location,
                "Source Website": "RemoteOK",
                "Link to Job Post": job_url,
                "Keyword": keyword
            })

        return jobs
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping {keyword}: {e}")
        return []
    except Exception as e:
        print(f"❌ Unexpected error scraping {keyword}: {e}")
        return []

def save_individual_csv(jobs, keyword):
    """Save jobs to individual CSV file"""
    if not jobs:
        return None
        
    filename = f"../results/csv/remoteok_{keyword}.csv"
    
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "Job Title", "Company Name", "AI Category", "Sector", 
                "Skills Mentioned", "Job Description", "Date Posted", 
                "Location", "Source Website", "Link to Job Post", "Keyword"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(jobs)
        
        print(f"✅ Saved {len(jobs)} {keyword} jobs to {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving CSV for {keyword}: {e}")
        return None

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
                print(f"📊 Added jobs from {filename}")
            except Exception as e:
                print(f"❌ Error reading {filename}: {e}")
    
    if all_jobs:
        big_csv_filename = "../results/csv/big_csv/remoteok_all_jobs.csv"
        try:
            with open(big_csv_filename, "w", newline="", encoding="utf-8") as f:
                fieldnames = [
                    "Job Title", "Company Name", "AI Category", "Sector", 
                    "Skills Mentioned", "Job Description", "Date Posted", 
                    "Location", "Source Website", "Link to Job Post", "Keyword"
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_jobs)
            
            print(f"✅ Combined {len(all_jobs)} jobs into {big_csv_filename}")
            return big_csv_filename
        except Exception as e:
            print(f"❌ Error saving combined CSV: {e}")
            return None
    else:
        print("❌ No jobs to combine")
        return None

def main():
    """Main function to run the scraping process"""
    setup_directories()
    
    # List of keywords to scrape
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
    
    print("🚀 Starting RemoteOK Scraping")
    print("=" * 50)
    
    # Scrape each keyword and save individual CSV files
    for i, keyword in enumerate(keywords):
        print(f"🔍 [{i+1}/{len(keywords)}] Scraping {keyword} jobs...")
        jobs = scrape_remoteok(keyword)
        
        if jobs:
            save_individual_csv(jobs, keyword)
            total_jobs += len(jobs)
            print(f"   Found {len(jobs)} jobs for {keyword}")
        else:
            print(f"   No jobs found for {keyword}")
        
        # Add delay to be respectful to the server
        time.sleep(3)
    
    # Combine all CSV files into one big CSV
    if total_jobs > 0:
        combine_all_csvs(keywords)
        print(f"\n🎉 Total jobs scraped: {total_jobs}")
        print("📁 Files saved in:")
        print("   - Individual: ../results/csv/remoteok_*.csv")
        print("   - Combined: ../results/csv/big_csv/remoteok_all_jobs.csv")
    else:
        print("\n❌ No jobs were scraped from any keyword")

if __name__ == "__main__":
    main()