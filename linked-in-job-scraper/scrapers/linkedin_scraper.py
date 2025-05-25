from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

class LinkedInScraper:
    def __init__(self):
        self.driver_path = r"C:\chromedriver-win64\chromedriver.exe"
    
    def setup_driver(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    
    def extract_skills(self, job_title, description):
        # Common tech skills to look for
        skills_list = [
            'Python', 'JavaScript', 'Java', 'React', 'Node.js', 'SQL', 'MongoDB',
            'AWS', 'Docker', 'Kubernetes', 'Git', 'HTML', 'CSS', 'Angular',
            'Vue.js', 'PHP', 'Laravel', 'Django', 'Flask', 'Machine Learning',
            'Data Science', 'AI', 'Blockchain', 'DevOps', 'Agile', 'Scrum'
        ]
        
        found_skills = []
        text = f"{job_title} {description}".lower()
        
        for skill in skills_list:
            if skill.lower() in text:
                found_skills.append(skill)
        
        return ', '.join(found_skills) if found_skills else 'General'
    
    def get_job_info(self, job_card):
        job = {}
        
        # Job title
        title = job_card.find('h3')
        job['title'] = title.text.strip() if title else 'N/A'
        
        # Company name
        company = job_card.find('h4')
        job['company'] = company.text.strip() if company else 'N/A'
        
        # Location
        location = job_card.find('span', class_='job-search-card__location')
        job['location'] = location.text.strip() if location else 'Pakistan'
        
        # Posted date
        date = job_card.find('time')
        job['date'] = date.text.strip() if date else 'Recently'
        
        # Description for skills extraction
        desc = job_card.find('p', class_='job-search-card__snippet')
        description = desc.text.strip() if desc else ''
        
        # Extract skills
        job['skills'] = self.extract_skills(job['title'], description)
        job['source'] = 'LinkedIn'
        
        return job
    
    def scrape_jobs(self, keyword="", location="Pakistan", max_jobs=50):
        print(f"Scraping LinkedIn for: {keyword} in {location}")
        
        driver = self.setup_driver()
        jobs_list = []
        
        try:
            for page in range(2):  # 2 pages = ~50 jobs
                start = page * 25
                url = f"https://www.linkedin.com/jobs/search?keywords={keyword}&location={location}&start={start}"
                
                driver.get(url)
                time.sleep(3)
                
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_cards = soup.find_all('div', class_='job-search-card')
                
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                
                for card in job_cards:
                    job_info = self.get_job_info(card)
                    if job_info['title'] != 'N/A':
                        jobs_list.append(job_info)
                
                if len(jobs_list) >= max_jobs:
                    break
        
        finally:
            driver.quit()
        
        return jobs_list[:max_jobs]
