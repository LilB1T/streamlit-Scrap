import requests
from bs4 import BeautifulSoup
import time
import re

class IndeedScraper:
    def __init__(self):
        self.base_url = "https://pk.indeed.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def extract_skills(self, job_title, description):
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
        
        try:
            # Job title
            title_elem = job_card.find('h2', class_='jobTitle')
            if title_elem:
                title_link = title_elem.find('a')
                job['title'] = title_link.text.strip() if title_link else 'N/A'
            else:
                job['title'] = 'N/A'
            
            # Company name
            company_elem = job_card.find('span', class_='companyName')
            job['company'] = company_elem.text.strip() if company_elem else 'N/A'
            
            # Location
            location_elem = job_card.find('div', class_='companyLocation')
            job['location'] = location_elem.text.strip() if location_elem else 'Pakistan'
            
            # Posted date
            date_elem = job_card.find('span', class_='date')
            job['date'] = date_elem.text.strip() if date_elem else 'Recently'
            
            # Description for skills
            desc_elem = job_card.find('div', class_='job-snippet')
            description = desc_elem.text.strip() if desc_elem else ''
            
            # Extract skills
            job['skills'] = self.extract_skills(job['title'], description)
            job['source'] = 'Indeed'
            
            return job
            
        except Exception as e:
            return None
    
    def scrape_jobs(self, keyword="", location="Pakistan", max_jobs=50):
        print(f"Scraping Indeed for: {keyword} in {location}")
        
        jobs_list = []
        
        try:
            for start in range(0, max_jobs, 10):  # Indeed shows 10 jobs per page
                url = f"{self.base_url}/jobs?q={keyword}&l={location}&start={start}"
                
                response = requests.get(url, headers=self.headers)
                time.sleep(2)  # Be polite
                
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job_seen_beacon')
                
                if not job_cards:
                    job_cards = soup.find_all('div', class_='jobsearch-SerpJobCard')
                
                for card in job_cards:
                    job_info = self.get_job_info(card)
                    if job_info and job_info['title'] != 'N/A':
                        jobs_list.append(job_info)
                
                if len(jobs_list) >= max_jobs:
                    break
        
        except Exception as e:
            print(f"Error scraping Indeed: {e}")
        
        return jobs_list[:max_jobs]
