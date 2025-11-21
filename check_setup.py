"""
Setup verification script
Checks if all requirements are met before running the app
"""

import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'pandas',
        'openpyxl',
        'google.generativeai',
        'PIL',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'PIL':
                __import__('PIL')
            elif package == 'dotenv':
                __import__('dotenv')
            elif package == 'google.generativeai':
                import google.generativeai
            else:
                __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    return True

def check_env_file():
    """Check if .env file exists and has Gemini API key"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("   Create .env file and add your Gemini API key")
        print("   Get a free key at: https://makersuite.google.com/app/apikey")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("❌ GEMINI_API_KEY not set in .env file")
        print("   Add your Gemini API key to the .env file")
        print("   Get a free key at: https://makersuite.google.com/app/apikey")
        return False
    
    print("✅ .env file found with Gemini API key")
    return True

def check_mind_map():
    """Check if mind map Excel file exists"""
    mind_map_file = 'Updated Mind Map.xlsx'
    if not os.path.exists(mind_map_file):
        print(f"❌ Mind map file not found: {mind_map_file}")
        return False
    
    try:
        from mind_map_parser import MindMapParser
        parser = MindMapParser(mind_map_file)
        sheets = list(parser.data.keys())
        print(f"✅ Mind map file found with {len(sheets)} sheet(s): {', '.join(sheets)}")
        return True
    except Exception as e:
        print(f"❌ Error reading mind map file: {str(e)}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("AI Tag Recommendation System - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment File", check_env_file),
        ("Mind Map File", check_mind_map)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\nChecking {name}...")
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All checks passed! You can run the app with: python app.py")
    else:
        print("⚠️  Some checks failed. Please fix the issues above before running the app.")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())

