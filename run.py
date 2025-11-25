"""
Quick start script for Autonomous QA Agent
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit application"""
    print("🚀 Starting Autonomous QA Agent...")
    print("📱 Opening Streamlit UI...")
    print("🌐 Application will open at http://localhost:8501")
    print("=" * 50)
    
    # Get the frontend app path
    app_path = os.path.join(os.path.dirname(__file__), "frontend", "app.py")
    
    # Run streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try running manually: streamlit run frontend/app.py")

if __name__ == "__main__":
    main()

