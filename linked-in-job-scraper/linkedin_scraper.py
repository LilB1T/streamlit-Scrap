import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

class LinkedInJobScraper:
    def __init__(self, headless=True):
        """Initialize the scraper with Chrome options"""
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = None
        self.jobs_data = []
    
    def start_driver(self):
        """Start the Chrome driver"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Chrome driver started successfully")
        except Exception as e:
            print(f"Error starting driver: {e}")
            return False
        return True
    
    def search_jobs(self, job_title, location="", num_pages=3):
        """Search for jobs on LinkedIn"""
        if not self.driver:
            print("Driver not initialized")
            return
        

        base_url = "https://www.linkedin.com/jobs/search"
        search_params = f"?keywords={job_title.replace(' ', '%20')}"
        if location:
            search_params += f"&location={location.replace(' ', '%20')}"
        
        search_url = base_url + search_params
        print(f"Searching for: {job_title} in {location if location else 'All locations'}")
        
        try:
            self.driver.get(search_url)
            time.sleep(3)
            

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-search__results-list"))
            )
            
            for page in range(num_pages):
                print(f"Scraping page {page + 1}...")
                self.scrape_current_page()
                

                if page < num_pages - 1:
                    if not self.go_to_next_page():
                        print("No more pages available")
                        break
                
                time.sleep(2)
                
        except TimeoutException:
            print("Timeout waiting for page to load")
        except Exception as e:
            print(f"Error during search: {e}")
    
    def scrape_current_page(self):
        """Scrape job listings from current page"""
        try:

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            

            job_cards = soup.find_all('div', {'class': re.compile(r'job-search-card|jobs-search-results__list-item')})
            
            if not job_cards:

                job_cards = soup.find_all('li', {'class': re.compile(r'jobs-search-results__list-item')})
            
            print(f"Found {len(job_cards)} job cards on this page")
            
            for card in job_cards:
                job_data = self.extract_job_data(card)
                if job_data:
                    self.jobs_data.append(job_data)
                    
        except Exception as e:
            print(f"Error scraping current page: {e}")
    
    def extract_job_data(self, job_card):
        """Extract job information from a job card"""
        try:
            job_data = {}
            
            # Job title
            title_elem = job_card.find('h3', {'class': re.compile(r'base-search-card__title')}) or \
                        job_card.find('a', {'class': re.compile(r'job-search-card__title-link')})
            job_data['title'] = title_elem.get_text(strip=True) if title_elem else 'N/A'
            
            # Company name
            company_elem = job_card.find('h4', {'class': re.compile(r'base-search-card__subtitle')}) or \
                          job_card.find('a', {'class': re.compile(r'job-search-card__subtitle-link')})
            job_data['company'] = company_elem.get_text(strip=True) if company_elem else 'N/A'
            
            # Location
            location_elem = job_card.find('span', {'class': re.compile(r'job-search-card__location')})
            job_data['location'] = location_elem.get_text(strip=True) if location_elem else 'N/A'
            
            # Job link
            link_elem = job_card.find('a', href=True)
            job_data['link'] = link_elem['href'] if link_elem else 'N/A'
            
            # Posted date
            date_elem = job_card.find('time') or job_card.find('span', {'class': re.compile(r'job-search-card__listdate')})
            job_data['posted_date'] = date_elem.get_text(strip=True) if date_elem else 'N/A'
            
            # Job description preview
            desc_elem = job_card.find('p', {'class': re.compile(r'job-search-card__snippet')})
            job_data['description_preview'] = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
            
            # Clean up the data
            for key, value in job_data.items():
                if isinstance(value, str):
                    job_data[key] = re.sub(r'\s+', ' ', value).strip()
            
            return job_data
            
        except Exception as e:
            print(f"Error extracting job data: {e}")
            return None
    
    def go_to_next_page(self):
        """Navigate to the next page of results"""
        try:
            # Look for next button
            next_button = self.driver.find_element(By.CSS_SELECTOR, 
                "button[aria-label*='next'], button[aria-label*='Next'], .artdeco-pagination__button--next")
            
            if next_button.is_enabled():
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
                return True
            else:
                return False
                
        except NoSuchElementException:
            print("Next button not found")
            return False
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False
    
    def save_to_csv(self, filename="linkedin_jobs.csv"):
        """Save scraped jobs to CSV file"""
        if not self.jobs_data:
            print("No job data to save")
            return
        
        try:

            df = pd.DataFrame(self.jobs_data)
            

            df = df.drop_duplicates(subset=['title', 'company'], keep='first')

            df.to_csv(filename, index=False, encoding='utf-8')
            print(f"Saved {len(df)} unique jobs to {filename}")
            

            print("\nScraping Summary:")
            print(f"Total jobs found: {len(df)}")
            print(f"Top companies:")
            print(df['company'].value_counts().head())
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            print("Driver closed")


def main():

    scraper = LinkedInJobScraper(headless=True)
    
    if not scraper.start_driver():
        return
    
    try:

        job_title = "Python Developer"
        location = "New York"
        num_pages = 2
        
        scraper.search_jobs(job_title, location, num_pages)
        

        scraper.save_to_csv("linkedin_python_jobs.csv")

        if scraper.jobs_data:
            print("\nSample job data:")
            for i, job in enumerate(scraper.jobs_data[:3]):
                print(f"\nJob {i+1}:")
                for key, value in job.items():
                    print(f"  {key}: {value}")
    
    finally:
        scraper.close_driver()


if __name__ == "__main__":
    main()
