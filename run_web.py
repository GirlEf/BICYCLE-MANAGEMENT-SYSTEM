#!/usr/bin/env python3
"""
Simple script to run the Bicycle Rental Management System web application
"""

import os
import sys

def main():
    print("🚲 Bicycle Rental Management System")
    print("=" * 50)
    
    # Check if required files exist
    if not os.path.exists('app.py'):
        print("❌ Error: app.py not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    if not os.path.exists('templates'):
        print("❌ Error: templates directory not found!")
        print("Please make sure all template files are present.")
        return
    
    # Check if database directory exists
    if not os.path.exists('BicycleRentalManagementSystem'):
        print("❌ Error: BicycleRentalManagementSystem directory not found!")
        print("Please make sure all source files are present.")
        return
    
    print("✅ All required files found!")
    print("\n📋 Starting the web application...")
    print("🌐 The application will be available at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("\n" + "=" * 50)
    
    try:
        # Import and run the Flask app
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please install required dependencies:")
        print("pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("Please check the error message above and try again.")

if __name__ == "__main__":
    main() 