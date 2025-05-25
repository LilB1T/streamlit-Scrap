import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from job_scraper import JobTrendAnalyzer
import pandas as pd
import time
from datetime import datetime


st.set_page_config(
    page_title="Job Trend Analyzer",
    page_icon="📊",
    layout="wide"
)


@st.cache_resource
def get_analyzer():
    return JobTrendAnalyzer()

analyzer = get_analyzer()


st.title("📊 Real-Time Job Trend Analyzer")
st.markdown("Analyze job trends from LinkedIn and Indeed in real-time")


st.sidebar.header("🔍 Search Options")
keyword = st.sidebar.text_input("Enter keyword (e.g., Python, Data Analyst)", "")
location = st.sidebar.selectbox("Select Location", ["Pakistan", "Karachi", "Lahore", "Islamabad"])


st.sidebar.header("🤖 Scraping Controls")
if st.sidebar.button("🚀 Start Scraping", type="primary"):
    with st.spinner("Scraping jobs from multiple sources..."):
        jobs = analyzer.scrape_all_sources(keyword, location)
        st.sidebar.success(f"Scraped {len(jobs)} jobs!")
        st.rerun()


auto_refresh = st.sidebar.checkbox("Auto-refresh every 5 minutes")
if auto_refresh:
    time.sleep(300)  
    st.rerun()


analytics = analyzer.get_analytics(keyword)


if analytics['total_jobs'] > 0:

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", analytics['total_jobs'])
    
    with col2:
        st.metric("Unique Companies", len(analytics['top_companies']))
    
    with col3:
        st.metric("Unique Locations", len(analytics['top_locations']))
    
    with col4:
        st.metric("Skills Identified", len(analytics['top_skills']))
    

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Job Titles")
        if analytics['top_titles']:
            titles_df = pd.DataFrame(list(analytics['top_titles'].items()), 
                                   columns=['Job Title', 'Count'])
            fig = px.bar(titles_df, x='Count', y='Job Title', orientation='h',
                        color='Count', color_continuous_scale='Blues')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏢 Top Hiring Companies")
        if analytics['top_companies']:
            companies_df = pd.DataFrame(list(analytics['top_companies'].items()), 
                                      columns=['Company', 'Count'])
            fig = px.pie(companies_df, values='Count', names='Company',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📍 Top Locations")
        if analytics['top_locations']:
            locations_df = pd.DataFrame(list(analytics['top_locations'].items()), 
                                      columns=['Location', 'Count'])
            fig = px.bar(locations_df, x='Location', y='Count',
                        color='Count', color_continuous_scale='Greens')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🛠️ Most In-Demand Skills")
        if analytics['top_skills']:
            skills_df = pd.DataFrame(list(analytics['top_skills'].items()), 
                                   columns=['Skill', 'Count'])
            fig = px.bar(skills_df.head(10), x='Count', y='Skill', orientation='h',
                        color='Count', color_continuous_scale='Reds')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    

    st.subheader("📊 Data Sources")
    if analytics['source_distribution']:
        source_df = pd.DataFrame(list(analytics['source_distribution'].items()), 
                               columns=['Source', 'Jobs'])
        fig = px.pie(source_df, values='Jobs', names='Source',
                    color_discrete_sequence=['#FF6B6B', '#4ECDC4'])
        st.plotly_chart(fig, use_container_width=True)
    

    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download CSV"):
            csv_file = analyzer.export_data("csv")
            st.success(f"Data exported to {csv_file}")
    
    with col2:
        if st.button("Download JSON"):
            json_file = analyzer.export_data("json")
            st.success(f"Data exported to {json_file}")

else:
    st.info("👆 Click 'Start Scraping' to begin analyzing job trends!")
    st.markdown("""
    ### How to use:
    1. **Enter a keyword** (optional) - e.g., "Python", "Data Analyst", "Marketing"
    2. **Select location** - Choose from major Pakistani cities
    3. **Click 'Start Scraping'** - The tool will fetch jobs from LinkedIn and Indeed
    4. **View analytics** - See trends, top skills, companies, and locations
    5. **Export data** - Download results as CSV or JSON
    
    ### Features:
    - ✅ Real-time scraping from LinkedIn and Indeed
    - ✅ Interactive charts and visualizations
    - ✅ Skill extraction and analysis
    - ✅ Export functionality
    - ✅ Keyword filtering
    """)


st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, Selenium, and BeautifulSoup")
