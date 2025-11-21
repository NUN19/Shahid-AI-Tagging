# AI Tag Recommendation System

An intelligent web application that helps agents select appropriate tags based on customer scenarios by analyzing a mind map Excel file and using AI reasoning.

## Features

- 🤖 **AI-Powered Analysis**: Uses Google Gemini AI with vision capabilities to analyze customer scenarios (FREE tier available)
- 📊 **Mind Map Integration**: Reads tag logic from Excel mind map files
- 📷 **Multi-Media Support**: Handles text descriptions, images, and videos
- 🎯 **Smart Tag Recommendations**: Provides tag suggestions with confidence levels and reasoning
- 💻 **Lightweight & Fast**: Optimized for low-spec PCs (Core i5 5th gen, 8GB RAM)
- 🎨 **User-Friendly Interface**: Clean, modern UI designed for agent productivity

## Requirements

- Python 3.8 or higher
- Windows PC (Core i5 5th gen, 8GB RAM minimum)
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
     AI_PROVIDER=gemini
     GEMINI_API_KEY=your_actual_api_key_here
     ```
   - Get your FREE API key from: https://makersuite.google.com/app/apikey

3. **Ensure your mind map Excel file is in the project directory:**
   - File should be named `Updated Mind Map.xlsx`
   - The app will automatically parse all sheets in the Excel file

4. **Verify setup (optional but recommended):**
   ```bash
   python check_setup.py
   ```
   This will check if everything is configured correctly.

## Usage

### Quick Start (Windows)
Double-click `start.bat` - it will automatically check dependencies and start the server.

### Manual Start

1. **Start the application:**
   ```bash
   python app.py
   ```

2. **Open your web browser:**
   - Navigate to `http://localhost:5000`
   - The application will be ready to use

3. **Using the application:**
   - Enter the customer scenario description in the text area
   - Optionally attach photos (JPEG, PNG, GIF, WebP) or videos (MP4, MOV, AVI, WebM)
   - Click "Analyze & Get Tag Recommendation"
   - Review the recommended tags, confidence level, and reasoning

**Note:** Video files are accepted but the AI will analyze them based on the filename and your description. For best results with videos, describe the key moments or issues visible in the video.

## How It Works

1. **Mind Map Parsing**: The app reads your Excel mind map and extracts all tags and their associated logic
2. **Scenario Analysis**: When an agent submits a scenario, the AI:
   - Analyzes the text description
   - Examines any attached images/videos
   - Compares the scenario against the mind map tag logic
3. **Tag Recommendation**: The AI provides:
   - Recommended tag(s) based on best match
   - Confidence level (High/Medium/Low)
   - Detailed reasoning for the selection
   - References to specific mind map entries

## File Structure

```
.
├── app.py                 # Main Flask application
├── mind_map_parser.py     # Excel mind map parser
├── ai_analyzer.py         # AI analysis engine
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── templates/
│   └── index.html         # Web interface
├── uploads/               # Temporary file storage (auto-created)
└── Updated Mind Map.xlsx  # Your mind map file
```

## Configuration

- **File Upload Size**: Maximum 50MB per file (configurable in `app.py`)
- **AI Model**: Uses Google Gemini models (gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro) with automatic fallback
- **Port**: Default port is 5000 (changeable in `app.py`)

## Troubleshooting

- **"GEMINI_API_KEY not found"**: Make sure you've created `.env` file with your Gemini API key
- **"Mind map file not found"**: Ensure `Updated Mind Map.xlsx` is in the project directory
- **Port already in use**: Change the port in `app.py` (line with `app.run()`)

## Notes

- The app uses Google Gemini's API (FREE tier available), which requires an internet connection
- Uploaded files are temporarily stored and automatically deleted after analysis
- For best performance, ensure stable internet connection for API calls
- Image analysis uses Gemini's vision capabilities
- Video files are noted in the analysis but detailed frame-by-frame analysis requires additional processing (currently uses filename and description)
- The app is optimized for low-spec PCs but requires internet for AI processing
- **Free tier limits**: 15 requests/minute, 1,500 requests/day

## Support

For issues or questions, check:
- Google Gemini API documentation: https://ai.google.dev/docs
- Python/Flask documentation for technical issues

