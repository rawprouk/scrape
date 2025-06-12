import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

BASE_URL = 'https://www.charitycomms.org.uk'
LISTING_BASE = f'{BASE_URL}/article-type/case-studies'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; CharityCommsScraper/1.0; +https://yourdomain.com)'
}

def get_soup(url):
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def parse_case_study_detail(url):
    soup = get_soup(url)
    content_div = soup.find('div', class_='entry-content')
    full_text = content_div.get_text(separator='\n', strip=True) if content_div else ''
    return full_text

def scrape_listing_page(url):
    soup = get_soup(url)
    case_studies = []
    articles = soup.select('article')

    for article in articles:
        title_el = article.find('h2')
        link_el = title_el.find('a') if title_el else None
        summary_el = article.find('div', class_='entry-summary')

        title = title_el.get_text(strip=True) if title_el else None
        summary = summary_el.get_text(strip=True) if summary_el else None
        link = BASE_URL + link_el['href'] if link_el else None

        full_text = parse_case_study_detail(link) if link else ''

        case_studies.append({
            'Title': title,
            'Summary': summary,
            'URL': link,
            'Full Text': full_text
        })

        time.sleep(1)  # polite delay

    return case_studies

def get_all_case_studies(max_pages=3):
    all_case_studies = []
    page = 1

    while page <= max_pages:
        url = f'{LISTING_BASE}/page/{page}/' if page > 1 else LISTING_BASE
        st.info(f"Scraping page {page}... {url}")
        case_studies = scrape_listing_page(url)
        if not case_studies:
            st.warning("No more case studies found.")
            break
        all_case_studies.extend(case_studies)
        page += 1
        time.sleep(2)
    return all_case_studies

def main():
    st.title("CharityComms Case Studies Scraper")
    st.write("This app scrapes charity marketing case studies from charitycomms.org.uk")

    max_pages = st.slider("Number of pages to scrape", min_value=1, max_value=10, value=3)

    if st.button("Start Scraping"):
        with st.spinner("Scraping case studies..."):
            data = get_all_case_studies(max_pages=max_pages)
            if data:
                df = pd.DataFrame(data)
                st.success(f"Scraped {len(data)} case studies!")
                st.dataframe(df)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Download CSV", csv, "charitycomms_case_studies.csv", "text/csv")
            else:
                st.error("No data scraped.")

if __name__ == "__main__":
    main()
