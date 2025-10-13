"""
Test Google Gemini API Integration
"""

import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


def test_gemini_connection():
    """Test connection to Google Gemini API"""
    print("="*80)
    print("TESTING GOOGLE GEMINI API")
    print("="*80)
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("\n[ERROR] GEMINI_API_KEY not found in .env file")
        print("\nTo get a free API key:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Sign in with your Google account")
        print("3. Click 'Create API Key'")
        print("4. Add it to your .env file as: GEMINI_API_KEY=your_key_here")
        return False
    
    try:
        import google.generativeai as genai
        
        print(f"\n[OK] API Key found: {api_key[:10]}...{api_key[-4:]}")
        print("[OK] google-generativeai library installed")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        print("\n[INFO] Testing API connection...")
        
        # Test with a simple prompt
        test_prompt = """Analyze this hypothetical Truth Social post:

"Great news! American manufacturing is booming. Tesla and Ford are expanding production."

In 2-3 sentences, provide: sentiment, affected companies, and trading implication."""
        
        response = model.generate_content(test_prompt)
        
        print("\n[SUCCESS] Gemini API is working!\n")
        print("Sample Analysis:")
        print("-" * 80)
        print(response.text)
        print("-" * 80)
        
        return True
        
    except ImportError:
        print("\n[ERROR] google-generativeai library not installed")
        print("Run: pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"\n[ERROR] Error testing Gemini API: {e}")
        print("\nPossible issues:")
        print("- Invalid API key")
        print("- Network connection problem")
        print("- API quota exceeded")
        return False


def main():
    success = test_gemini_connection()
    
    print("\n" + "="*80)
    if success:
        print("[OK] Gemini API is ready to use!")
        print("\nYou can now run: python main.py")
    else:
        print("[FAIL] Setup incomplete. Please resolve the issues above.")
    print("="*80)


if __name__ == "__main__":
    main()

