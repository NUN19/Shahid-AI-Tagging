# AI Tag Recommendation System

An intelligent web application that helps agents select appropriate tags based on customer scenarios by analyzing a mind map Excel file and using AI reasoning.

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini AI with vision capabilities to analyze customer scenarios (FREE tier available)
- 📊 **Mind Map Integration**: Users upload their own Excel mind map files (processed securely client-side)
- 📷 **Multi-Media Support**: Handles text descriptions, images, and videos
- 🎯 **Smart Tag Recommendations**: Provides tag suggestions with confidence levels and reasoning
- 🔒 **Secure**: Excel files processed entirely in browser - never leave user's device
- 🌐 **Bilingual**: English and Arabic interface support
- 💻 **Lightweight & Fast**: Optimized for low-spec PCs
- 🎨 **User-Friendly Interface**: Clean, modern UI designed for agent productivity

## Requirements

- Python 3.8 or higher
- Google Gemini API key (get a FREE one at https://makersuite.google.com/app/apikey)

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file in the project directory
   - Add your Gemini API key to `.env`:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```
   - Get your FREE API key from: https://makersuite.google.com/app/apikey

3. **Verify setup (optional):**
   ```bash
   python check_setup.py
   ```

## Usage

### Local Development

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your web browser:**
   - Navigate to `http://localhost:5000`
   - You'll be redirected to upload your mind map Excel file
   - Upload your Excel file (processed securely in browser)
   - Start analyzing scenarios!

### Quick Start (Windows)
Double-click `start.bat` - it will automatically check dependencies and start the server.

## How It Works

1. **Upload Mind Map**: User uploads Excel mind map file (processed entirely in browser - secure!)
2. **Scenario Analysis**: When an agent submits a scenario, the AI:
   - Analyzes the text description
   - Examines any attached images/videos
   - Compares the scenario against the mind map tag logic
3. **Tag Recommendation**: The AI provides:
   - Recommended tag(s) based on best match
   - Confidence level (High/Medium/Low)
   - Detailed reasoning for the selection
   - References to specific mind map entries

## Deployment

### Deploy to Railway (Recommended - Fast & Free)

1. Push code to GitHub
2. Go to https://railway.app
3. Sign up with GitHub
4. New Project → Deploy from GitHub
5. Select your repository
6. Add environment variables:
   - `GEMINI_API_KEY` = your API key
   - `SESSION_COOKIE_SECURE` = `true`
7. Get your shareable link!

### Deploy to Render

1. Push code to GitHub
2. Go to https://render.com
3. New Web Service → Connect GitHub
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
5. Add environment variables (same as Railway)
6. Deploy!

## Security

- ✅ **Excel files processed client-side** - Never leave user's device
- ✅ **Only tag structure sent to server** - No sensitive data transmitted
- ✅ **Session-based storage** - No files stored on server
- ✅ **HTTPS encryption** - All traffic encrypted

## File Structure

```
.
├── app.py                 # Main Flask application
├── mind_map_parser.py     # Excel mind map parser
├── ai_analyzer.py         # AI analysis engine
├── check_setup.py         # Setup verification script
├── requirements.txt       # Python dependencies
├── Procfile              # For cloud deployment (Render/Heroku)
├── railway.json          # For Railway deployment
├── fly.toml              # For Fly.io deployment
├── start.bat             # Quick start script (Windows)
├── templates/
│   ├── index.html        # Main application interface
│   └── setup.html        # Mind map upload page
└── .env                  # Environment variables (create this)
```

## Configuration

- **File Upload Size**: Maximum 50MB per file
- **AI Model**: Uses Google Gemini 2.5 Flash
- **Port**: Default port is 5000 (configurable via `FLASK_PORT` env var)
- **Session Timeout**: 24 hours

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Create `.env` file with your Gemini API key
- **"Please upload a mind map first"**: Upload your Excel file at the setup page
- **"Content blocked by safety filters"**: Try rephrasing your scenario
- **Port already in use**: Change port in `app.py` or set `FLASK_PORT` env var

## Notes

- The app uses Google Gemini's API (FREE tier: 15 requests/minute, 1,500 requests/day)
- Excel files are processed entirely in the browser (maximum security)
- Uploaded scenario files (images/videos) are temporarily stored and automatically deleted
- Requires internet connection for AI processing

## Support

For issues or questions:
- Google Gemini API: https://ai.google.dev/docs
- Python/Flask documentation for technical issues
