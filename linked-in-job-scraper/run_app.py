import subprocess
import sys

def install_requirements():
    """Install required packages"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Error installing requirements")

def run_streamlit():
    """Run the Streamlit app"""
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")

if __name__ == "__main__":
    print("🚀 Starting Job Trend Analyzer...")
    

    install_requirements()
    
 
    print("🌐 Starting web interface...")
    run_streamlit()
