# Free API Setup Guide

This app now supports **FREE AI APIs**! You don't need to pay for OpenAI.

## 🆓 Best Free Option: Google Gemini

**Google Gemini** offers a generous free tier that's perfect for this app!

### Setup Steps:

1. **Get a FREE Gemini API Key:**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with your Google account (free)
   - Click "Create API Key"
   - Copy your API key

2. **Update your `.env` file:**
   ```
   AI_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Install the Gemini package:**
   ```bash
   pip install google-generativeai
   ```

4. **Restart the app:**
   ```bash
   python app.py
   ```

That's it! The app will now use Gemini's free API.

## 📊 Free Tier Limits:

- **Gemini**: 15 requests per minute, 1,500 requests per day (FREE)
- **Hugging Face**: Varies by model, many are completely free
- **OpenAI**: Requires paid account

## 🔄 Switching Between Providers:

Just change `AI_PROVIDER` in your `.env` file:
- `AI_PROVIDER=gemini` - Free Google Gemini (recommended)
- `AI_PROVIDER=openai` - Paid OpenAI
- `AI_PROVIDER=huggingface` - Free Hugging Face models

## 💡 Why Gemini?

- ✅ **Completely FREE** (generous limits)
- ✅ Supports images (vision capabilities)
- ✅ Fast and reliable
- ✅ No credit card required
- ✅ Easy to set up

## 🚀 Quick Start with Gemini:

1. Get API key: https://makersuite.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your_key` and `AI_PROVIDER=gemini`
3. Install: `pip install google-generativeai`
4. Run: `python app.py`

Enjoy your free AI tag recommendation system! 🎉

