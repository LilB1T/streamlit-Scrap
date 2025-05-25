from scrapers.linkedin_scraper import LinkedInScraper
from scrapers.indeed_scraper import IndeedScraper
from data_manager import DataManager
import time

class JobTrendAnalyzer:
    def __init__(self):
        self.linkedin_scraper = LinkedInScraper()
        self.indeed_scraper = IndeedScraper()
        self.data_manager = DataManager()
    
    def scrape_all_sources(self, keyword="", location="Pakistan"):
        """Scrape jobs from all sources"""
        print("Starting job scraping from multiple sources...")
        
        all_jobs = []
        

        try:
            linkedin_jobs = self.linkedin_scraper.scrape_jobs(keyword, location, 50)
            all_jobs.extend(linkedin_jobs)
            print(f"LinkedIn: {len(linkedin_jobs)} jobs")
        except Exception as e:
            print(f"LinkedIn scraping failed: {e}")
        

        try:
            indeed_jobs = self.indeed_scraper.scrape_jobs(keyword, location, 50)
            all_jobs.extend(indeed_jobs)
            print(f"Indeed: {len(indeed_jobs)} jobs")
        except Exception as e:
            print(f"Indeed scraping failed: {e}")
        

        if all_jobs:
            self.data_manager.save_jobs(all_jobs)
            print(f"Total jobs scraped: {len(all_jobs)}")
        
        return all_jobs
    
    def get_analytics(self, keyword=""):
        """Get analytics data"""
        return self.data_manager.get_analytics_data(keyword)
    
    def export_data(self, format="csv"):
        """Export data in specified format"""
        if format == "csv":
            return self.data_manager.export_to_csv()
        elif format == "json":
            return self.data_manager.export_to_json()


if __name__ == "__main__":
    analyzer = JobTrendAnalyzer()
    

    keyword = input("Enter keyword to search (or press Enter for all): ")
    jobs = analyzer.scrape_all_sources(keyword)
    

    analytics = analyzer.get_analytics(keyword)
    print("\n=== JOB ANALYTICS ===")
    print(f"Total jobs: {analytics['total_jobs']}")
    print(f"Top job titles: {list(analytics['top_titles'].keys())[:3]}")
    print(f"Top skills: {list(analytics['top_skills'].keys())[:5]}")
