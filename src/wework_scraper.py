from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_wework():
    data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # set False if you want to see browser
        page = browser.new_page()
        
        # Go to WeWork locations page
        page.goto("https://www.wework.com/l/find-us")

        # Wait for location elements to load
        page.wait_for_selector("a.LocationCard__StyledLocationCard-sc")

        # Extract locations
        locations = page.query_selector_all("a.LocationCard__StyledLocationCard-sc")
        for loc in locations:
            name = loc.inner_text()
            link = loc.get_attribute("href")
            data.append({"Name": name, "Link": f"https://www.wework.com{link}"})

        browser.close()

    # Save to CSV
    df = pd.DataFrame(data)
    df.to_csv("wework_locations.csv", index=False)
    print("✅ Data saved to wework_locations.csv")

if __name__ == "__main__":
    scrape_wework()