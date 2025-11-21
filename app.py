"""
AI Tag Recommendation App
Helps agents select appropriate tags based on customer scenarios using mind map logic
"""

from flask import Flask, render_template, request, jsonify, session
import os
import secrets
import json
from dotenv import load_dotenv
from mind_map_parser import MindMapParser
from ai_analyzer import AIAnalyzer
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Session configuration for secure client-side processing
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
# Secure cookies: True for production (HTTPS), False for local development
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production' or os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global components (will be session-based)
mind_map_parser = None
ai_analyzer = None

def get_mind_map_parser():
    """Get or create mind map parser for current session"""
    global mind_map_parser
    
    if 'mind_map_data' in session:
        # Load from session (client-side processed data)
        try:
            data_dict = session['mind_map_data']
            # Convert JSON data back to DataFrames
            parsed_data = {}
            for sheet_name, sheet_data in data_dict.items():
                # sheet_data is a list of dictionaries (rows)
                parsed_data[sheet_name] = pd.DataFrame(sheet_data)
            
            mind_map_parser = MindMapParser(data_dict=parsed_data)
            return mind_map_parser
        except Exception as e:
            print(f"Error loading mind map from session: {e}")
            return None
    else:
        # Try to load from file (backward compatibility)
        if os.path.exists('Updated Mind Map.xlsx'):
            try:
                mind_map_parser = MindMapParser('Updated Mind Map.xlsx')
                return mind_map_parser
            except Exception as e:
                print(f"Error loading mind map from file: {e}")
                return None
    return None

def get_ai_analyzer():
    """Get or create AI analyzer for current session"""
    global ai_analyzer
    parser = get_mind_map_parser()
    if parser:
        ai_analyzer = AIAnalyzer(parser)
        return ai_analyzer
    return None

@app.route('/')
def index():
    """Main page - redirect to setup if no mind map loaded"""
    # Check if mind map is loaded
    parser = get_mind_map_parser()
    if not parser:
        return render_template('setup.html')
    return render_template('index.html')

@app.route('/api/upload-mindmap', methods=['POST'])
def upload_mindmap():
    """Receive mind map summary from client (Excel processed client-side)"""
    try:
        data = request.get_json()
        
        if not data or 'mind_map_data' not in data:
            return jsonify({'error': 'No mind map data provided'}), 400
        
        # Store mind map data in session (already processed client-side)
        # Data structure: {sheet_name: [{col1: val1, col2: val2, ...}, ...]}
        session['mind_map_data'] = data['mind_map_data']
        session['mind_map_filename'] = data.get('filename', 'uploaded_mind_map.xlsx')
        session.permanent = True
        
        # Verify it can be parsed
        parser = get_mind_map_parser()
        if not parser:
            return jsonify({'error': 'Failed to parse mind map data'}), 400
        
        # Get summary info
        sheets_count = len(parser.data)
        total_tags = len(parser.get_all_tags())
        
        return jsonify({
            'success': True,
            'filename': session['mind_map_filename'],
            'sheets': sheets_count,
            'tags': total_tags
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-mindmap', methods=['GET'])
def check_mindmap():
    """Check if mind map is loaded for current session"""
    parser = get_mind_map_parser()
    if parser:
        tags = parser.get_all_tags()
        return jsonify({
            'loaded': True,
            'filename': session.get('mind_map_filename', 'Mind Map'),
            'tags_count': len(tags)
        })
    return jsonify({'loaded': False})

@app.route('/api/analyze', methods=['POST'])
def analyze_scenario():
    """Analyze customer scenario and suggest tags"""
    try:
        # Check if mind map is loaded
        analyzer = get_ai_analyzer()
        if not analyzer:
            return jsonify({'error': 'Please upload a mind map first'}), 400
        
        data = request.form
        scenario = data.get('scenario', '')
        language = data.get('language', 'en')  # Get language preference
        
        # Handle file uploads (scenario images/videos)
        files = request.files.getlist('files')
        file_paths = []
        
        for file in files:
            if file.filename:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(file_path)
                file_paths.append(file_path)
        
        # Analyze with AI (pass language parameter)
        result = analyzer.analyze_scenario(scenario, file_paths, language=language)
        
        # Clean up uploaded files
        for file_path in file_paths:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tags', methods=['GET'])
def get_tags():
    """Get all available tags from mind map"""
    try:
        parser = get_mind_map_parser()
        if not parser:
            return jsonify({'error': 'No mind map loaded'}), 400
        tags = parser.get_all_tags()
        return jsonify({'tags': tags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/setup')
def setup():
    """Setup page for mind map upload"""
    return render_template('setup.html')

if __name__ == '__main__':
    # Get host and port from environment variables, with defaults
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Default to localhost only
    port = int(os.getenv('FLASK_PORT', 5000))     # Default port 5000
    app.run(debug=True, host=host, port=port)

