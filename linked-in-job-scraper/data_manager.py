import pandas as pd
import sqlite3
from datetime import datetime
import json

class DataManager:
    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                company TEXT,
                location TEXT,
                skills TEXT,
                date_posted TEXT,
                source TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_jobs(self, jobs_list):
        """Save jobs to database"""
        if not jobs_list:
            return
        
        conn = sqlite3.connect(self.db_path)
        
        for job in jobs_list:

            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM jobs 
                WHERE title = ? AND company = ? AND location = ?
            ''', (job['title'], job['company'], job['location']))
            
            if not cursor.fetchone(): 
                cursor.execute('''
                    INSERT INTO jobs (title, company, location, skills, date_posted, source)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    job['title'], job['company'], job['location'],
                    job['skills'], job['date'], job['source']
                ))
        
        conn.commit()
        conn.close()
        print(f"Saved {len(jobs_list)} jobs to database")
    
    def get_all_jobs(self):
        """Get all jobs from database"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
        conn.close()
        return df
    
    def get_filtered_jobs(self, keyword=""):
        """Get filtered jobs based on keyword"""
        conn = sqlite3.connect(self.db_path)
        
        if keyword:
            query = """
                SELECT * FROM jobs 
                WHERE title LIKE ? OR skills LIKE ?
            """
            df = pd.read_sql_query(query, conn, params=[f'%{keyword}%', f'%{keyword}%'])
        else:
            df = pd.read_sql_query("SELECT * FROM jobs", conn)
        
        conn.close()
        return df
    
    def export_to_csv(self, filename="all_jobs.csv"):
        """Export jobs to CSV"""
        df = self.get_all_jobs()
        df.to_csv(filename, index=False)
        return filename
    
    def export_to_json(self, filename="all_jobs.json"):
        """Export jobs to JSON"""
        df = self.get_all_jobs()
        df.to_json(filename, orient='records', indent=2)
        return filename
    
    def get_analytics_data(self, keyword=""):
        """Get data for analytics"""
        df = self.get_filtered_jobs(keyword)
        
        if df.empty:
            return {
                'total_jobs': 0,
                'top_titles': [],
                'top_companies': [],
                'top_locations': [],
                'top_skills': [],
                'source_distribution': []
            }
        

        top_titles = df['title'].value_counts().head(5).to_dict()
        

        top_companies = df['company'].value_counts().head(5).to_dict()
        

        top_locations = df['location'].value_counts().head(5).to_dict()
        

        all_skills = []
        for skills_str in df['skills'].dropna():
            if skills_str != 'General':
                skills = [skill.strip() for skill in skills_str.split(',')]
                all_skills.extend(skills)
        
        skills_series = pd.Series(all_skills)
        top_skills = skills_series.value_counts().head(10).to_dict()
        

        source_dist = df['source'].value_counts().to_dict()
        
        return {
            'total_jobs': len(df),
            'top_titles': top_titles,
            'top_companies': top_companies,
            'top_locations': top_locations,
            'top_skills': top_skills,
            'source_distribution': source_dist
        }
