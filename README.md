Perfect 👌 Here’s a clean **README.md** you can drop into your project:

---

# 🧑‍💻 AI Job Scraper (RemoteOK)

This project scrapes **AI/ML-related remote job postings** from [RemoteOK](https://remoteok.com) and saves them into structured CSV files.

It has two phases:

1. **Scrape** – Collects job titles, companies, short descriptions, posting dates, locations, and job links.
2. **Enrich** – Visits each job link to extract the **full job description** and automatically detects **skills mentioned**.

---

## 📂 Project Structure

```
AI-Effect-On-Industries/
│
├── src/
│   └── remoteok_scraper.py   # Main script
│
├── results/
│   └── csv/
│       ├── remoteok_{keyword}.csv   # Jobs per keyword
│       └── big_csv/                 # (Optional) combined results
│
└── README.md
```

---

## ⚡ Features

* Scrapes jobs by AI-related **keywords** (e.g., `machine-learning`, `chatgpt`, `docker`).
* Automatically maps:

  * **AI Category** (e.g., NLP, Generative AI, Robotics, etc.)
  * **Sector** (e.g., Healthcare, Finance, Education, etc.)
* Extracts:

  * Job title
  * Company name
  * Location (Remote/Region)
  * Short job description
  * Date posted (parsed from relative dates like `2d ago`)
  * Source website (RemoteOK)
  * Link to job post
* **Enrichment step**: fetches full job descriptions + scans for skills (e.g., Python, SQL, TensorFlow, Docker).
* Saves results into **CSV files** for easy analysis.

---

## 🔧 Requirements

* Python **3.12+**
* Libraries:

  ```bash
  pip install requests beautifulsoup4
  ```

---

## ▶️ How to Run

Navigate to the `src/` directory and run:

### 1. Scrape jobs

```bash
python remoteok_scraper.py scrape
```

* Collects job data for all keywords.
* Saves one CSV per keyword inside `../results/csv/`.

---

### 2. Enrich jobs

```bash
python remoteok_scraper.py enrich
```

* Reads each CSV.
* Visits each job link.
* Extracts full job descriptions.
* Detects and fills in "Skills Mentioned".
* Updates the CSVs with enriched data.

*(⚠️ Slower – includes polite delays between requests to avoid blocking.)*

---

### 3. Do both (scrape + enrich)

```bash
python remoteok_scraper.py full
```

---

## 📊 Example CSV Output

| Job Title                 | Company Name | AI Category      | Sector                | Skills Mentioned        | Job Description (truncated)          | Date Posted | Location | Source Website | Link to Job Post                                  |
| ------------------------- | ------------ | ---------------- | --------------------- | ----------------------- | ------------------------------------ | ----------- | -------- | -------------- | ------------------------------------------------- |
| Machine Learning Engineer | OpenAI       | Machine Learning | Technology & Software | Python, TensorFlow, SQL | We are looking for an ML engineer... | 2025-08-18  | Remote   | RemoteOK       | [https://remoteok.com/](https://remoteok.com/)... |

---

## 🚦 Notes

* RemoteOK enforces **rate limits**.

  * Use `scrape` with **short delays** (fast).
  * Use `enrich` with **longer delays** (safe).
* If a job doesn’t match any **sector keywords**, it is labeled as **“Other AI”**.
* If skills aren’t found, the **Skills Mentioned** column remains blank.

---

## 📌 Next Steps

* Add **CSV merger** to combine all results into one big dataset.
* Enhance skill extraction using **NLP** (instead of static keywords).
* Add support for scraping other job boards.