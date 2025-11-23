"""
AI Tag Recommendation App
Helps agents select appropriate tags based on customer scenarios using mind map logic
"""

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
import secrets
import json
import time
from dotenv import load_dotenv
from mind_map_parser import MindMapParser
from ai_analyzer import AIAnalyzer
import pandas as pd

load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SESSION_FOLDER'] = 'sessions'

# Session configuration - use server-side storage to avoid cookie size limits
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on server, not in cookies
app.config['SESSION_FILE_DIR'] = app.config['SESSION_FOLDER']
app.config['SESSION_FILE_THRESHOLD'] = 500
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
# Secure cookies: True for production (HTTPS), False for local development
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production' or os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'

# Initialize Flask-Session
Session(app)

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SESSION_FOLDER'], exist_ok=True)

# Server-side storage folder for mind map data (keyed by session ID)
# This avoids cookie size limits and persists across workers
MIND_MAP_STORAGE_DIR = 'mind_map_storage'
os.makedirs(MIND_MAP_STORAGE_DIR, exist_ok=True)

# Global components (will be session-based)
mind_map_parser = None
ai_analyzer = None

def get_mind_map_parser():
    """Get or create mind map parser for current session"""
    global mind_map_parser
    
    # Get session ID
    session_id = session.get('_id', session.sid if hasattr(session, 'sid') else None)
    if not session_id:
        # Generate session ID if not exists
        session_id = secrets.token_hex(16)
        session['_id'] = session_id
        session.permanent = True
        session.modified = True
        print(f"[Parser] Generated new session ID: {session_id}")
    else:
        print(f"[Parser] Using existing session ID: {session_id}")
    
    # Check file-based storage (persists across workers)
    storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
    print(f"[Parser] Checking storage file: {storage_file} (exists: {os.path.exists(storage_file)})")
    if os.path.exists(storage_file):
        try:
            # Load from file
            with open(storage_file, 'r', encoding='utf-8') as f:
                storage_data = json.load(f)
            data_dict = storage_data.get('data', {})
            
            # Validate data structure
            if not isinstance(data_dict, dict):
                print("Error: mind_map_data is not a dictionary")
                return None
            
            if len(data_dict) == 0:
                print("Error: mind_map_data is empty")
                return None
            
            # Convert JSON data back to DataFrames
            parsed_data = {}
            for sheet_name, sheet_data in data_dict.items():
                # sheet_data is a list of dictionaries (rows)
                if not isinstance(sheet_data, list):
                    print(f"Warning: Sheet '{sheet_name}' data is not a list, skipping...")
                    continue
                
                if len(sheet_data) == 0:
                    print(f"Info: Sheet '{sheet_name}' is empty, skipping...")
                    # Skip empty sheets instead of creating empty DataFrames
                    continue
                
                try:
                    # Convert to DataFrame
                    df = pd.DataFrame(sheet_data)
                    # Only add if DataFrame has at least one column
                    if len(df.columns) > 0:
                        parsed_data[sheet_name] = df
                    else:
                        print(f"Info: Sheet '{sheet_name}' has no columns, skipping...")
                except Exception as df_error:
                    print(f"Warning: Failed to convert sheet '{sheet_name}' to DataFrame: {df_error}, skipping...")
                    continue
            
            if len(parsed_data) == 0:
                print("Error: No valid sheets found in mind map data")
                # Don't return None immediately - check if we have any data at all
                # This handles the case where all sheets are empty but data was uploaded
                if len(data_dict) > 0:
                    print(f"Warning: {len(data_dict)} sheets in data but all are empty or invalid")
                return None
            
            # Create parser and cache it globally
            # Note: In multi-worker setup, each worker has its own cache, but storage is shared
            try:
                mind_map_parser = MindMapParser(data_dict=parsed_data)
                print(f"[Parser] Successfully created parser with {len(parsed_data)} sheets for session {session_id}")
                return mind_map_parser
            except Exception as parse_error:
                print(f"Error creating MindMapParser: {parse_error}")
                import traceback
                traceback.print_exc()
                return None
        except Exception as e:
            print(f"Error loading mind map from storage: {e}")
            import traceback
            traceback.print_exc()
            return None
    else:
        # Try to load from file (backward compatibility)
        # Priority: New organized file first, then old file
        new_file = 'List of tags 2025.xlsx'
        old_file = 'Updated Mind Map.xlsx'
        
        if os.path.exists(new_file):
            try:
                print(f"[Parser] Loading new organized file: {new_file}")
                mind_map_parser = MindMapParser(new_file)
                return mind_map_parser
            except Exception as e:
                print(f"Error loading new mind map file: {e}")
                # Fallback to old file if new file fails
                if os.path.exists(old_file):
                    try:
                        print(f"[Parser] Falling back to old file: {old_file}")
                        mind_map_parser = MindMapParser(old_file)
                        return mind_map_parser
                    except Exception as e2:
                        print(f"Error loading old mind map file: {e2}")
                        return None
                return None
        elif os.path.exists(old_file):
            try:
                print(f"[Parser] Loading old file: {old_file}")
                mind_map_parser = MindMapParser(old_file)
                return mind_map_parser
            except Exception as e:
                print(f"Error loading mind map from file: {e}")
                return None
    return None

def get_ai_analyzer():
    """Get or create AI analyzer for current session"""
    global ai_analyzer
    # Check if we already have an analyzer for this session
    # Use session ID to ensure consistency
    session_id = session.get('_id', None)
    
    parser = get_mind_map_parser()
    if parser:
        # Only create new analyzer if we don't have one or if parser changed
        # This ensures safety settings are initialized once and reused
        if ai_analyzer is None or not hasattr(ai_analyzer, 'mind_map_parser') or ai_analyzer.mind_map_parser != parser:
            print(f"[APP] Creating new AIAnalyzer for session {session_id}")
            ai_analyzer = AIAnalyzer(parser)
        else:
            print(f"[APP] Reusing existing AIAnalyzer for session {session_id}")
        return ai_analyzer
    return None

@app.route('/')
def index():
    """Main page - redirect to setup if no mind map loaded"""
    # Ensure session is initialized
    if '_id' not in session:
        session_id = secrets.token_hex(16)
        session['_id'] = session_id
        session.permanent = True
        session.modified = True
        print(f"[Index] Generated new session ID: {session_id}")
    else:
        print(f"[Index] Using existing session ID: {session.get('_id')}")
    
    # Check if mind map is loaded
    parser = get_mind_map_parser()
    if not parser:
        # Clear any cached parser
        global mind_map_parser
        mind_map_parser = None
        print(f"[Index] No parser found, redirecting to setup")
        return render_template('setup.html')
    print(f"[Index] Parser found, rendering index page")
    return render_template('index.html')

@app.route('/api/upload-mindmap', methods=['POST'])
def upload_mindmap():
    """Receive mind map summary from client (Excel processed client-side)"""
    try:
        # Check content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided. Please ensure the request contains JSON data.'}), 400
        
        if 'mind_map_data' not in data:
            return jsonify({'error': 'No mind map data provided. The request must include mind_map_data.'}), 400
        
        # Validate mind_map_data structure
        mind_map_data = data['mind_map_data']
        if not isinstance(mind_map_data, dict):
            return jsonify({'error': 'Invalid mind map data format. Expected a dictionary of sheets.'}), 400
        
        if len(mind_map_data) == 0:
            return jsonify({'error': 'Mind map data is empty. Please ensure the Excel file has data.'}), 400
        
        # PRE-VALIDATE: Check if we have at least one non-empty sheet before storing
        has_valid_sheet = False
        for sheet_name, sheet_data in mind_map_data.items():
            if isinstance(sheet_data, list) and len(sheet_data) > 0:
                # Check if sheet has at least one row with data
                for row in sheet_data:
                    if isinstance(row, dict) and len(row) > 0:
                        # Check if row has at least one non-empty value
                        if any(str(v).strip() and str(v).lower() not in ['nan', 'none', ''] for v in row.values()):
                            has_valid_sheet = True
                            break
                    if has_valid_sheet:
                        break
            if has_valid_sheet:
                break
        
        if not has_valid_sheet:
            return jsonify({
                'error': 'No valid data found',
                'details': 'The Excel file was processed but all sheets are empty or contain no valid data.',
                'solution': 'Please ensure your Excel file has at least one sheet with data rows containing information.'
            }), 400
        
        # Store mind map data server-side (not in cookie to avoid size limits)
        # Get or create session ID
        session_id = session.get('_id')
        if not session_id:
            session_id = secrets.token_hex(16)
            session['_id'] = session_id
        session.permanent = True
        session.modified = True  # Mark session as modified to ensure it's saved
        
        # Store in file-based storage (persists across workers, avoids cookie size limit)
        storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
        storage_data = {
            'data': mind_map_data,
            'filename': data.get('filename', 'uploaded_mind_map.xlsx'),
            'timestamp': time.time()
        }
        with open(storage_file, 'w', encoding='utf-8') as f:
            json.dump(storage_data, f, ensure_ascii=False)
        print(f"[Upload] Stored mind map data to {storage_file} for session {session_id}")
        print(f"[Upload] Storage file exists: {os.path.exists(storage_file)}")
        
        # Only store filename in session cookie (small)
        session['mind_map_filename'] = data.get('filename', 'uploaded_mind_map.xlsx')
        
        # Clear cached parser to force fresh load
        global mind_map_parser
        mind_map_parser = None
        
        # Verify it can be parsed
        try:
            # Force session to be saved before parsing
            session.permanent = True
            session.modified = True
            
            parser = get_mind_map_parser()
            if not parser:
                # Clean up storage if parsing failed
                session_id = session.get('_id')
                if session_id:
                    storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
                    if os.path.exists(storage_file):
                        os.remove(storage_file)
                session.pop('mind_map_filename', None)
                return jsonify({
                    'error': 'Failed to parse mind map data',
                    'details': 'The uploaded Excel file could not be processed. Please check the file format. Ensure at least one sheet has data.',
                    'solution': 'Make sure your Excel file has at least one sheet with data rows.'
                }), 400
            
            # Get summary info
            sheets_count = len(parser.data) if parser.data else 0
            total_tags = len(parser.get_all_tags()) if parser else 0
            
            # Validate we have at least some data
            if sheets_count == 0 or total_tags == 0:
                # Clean up storage if no valid data
                session_id = session.get('_id')
                if session_id:
                    storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
                    if os.path.exists(storage_file):
                        os.remove(storage_file)
                session.pop('mind_map_filename', None)
                # Clear cached parser
                mind_map_parser = None
                return jsonify({
                    'error': 'No valid data found',
                    'details': 'The Excel file was processed but contains no valid data. All sheets appear to be empty or have no extractable tags.',
                    'solution': 'Please ensure your Excel file has at least one sheet with data rows containing tag information.'
                }), 400
            
            # Ensure session is saved and parser is cached
            session.permanent = True
            session.modified = True
            
            return jsonify({
                'success': True,
                'filename': session.get('mind_map_filename', 'uploaded_mind_map.xlsx'),
                'sheets': sheets_count,
                'tags': total_tags,
                'session_id': session.get('_id')  # Return session ID for debugging
            })
        except Exception as parse_error:
            # Clean up storage if parsing failed
            session_id = session.get('_id')
            if session_id:
                storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
                if os.path.exists(storage_file):
                    os.remove(storage_file)
            session.pop('mind_map_filename', None)
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error parsing mind map: {error_trace}")
            return jsonify({
                'error': 'Failed to parse mind map data',
                'details': str(parse_error),
                'solution': 'Please ensure your Excel file is valid and contains data in the expected format. Check that sheets are not completely empty.'
            }), 400
    
    except Exception as e:
        # Always return JSON, never HTML
        error_msg = str(e)
        # Clean up storage on error
        session_id = session.get('_id')
        if session_id:
            storage_file = os.path.join(MIND_MAP_STORAGE_DIR, f"{session_id}.json")
            if os.path.exists(storage_file):
                try:
                    os.remove(storage_file)
                except:
                    pass
        session.pop('mind_map_filename', None)
        return jsonify({
            'error': 'Upload failed',
            'details': error_msg,
            'solution': 'Please try again. If the problem persists, check that your Excel file is valid.'
        }), 500

@app.route('/api/check-mindmap', methods=['GET'])
def check_mindmap():
    """Check if mind map is loaded for current session"""
    # Ensure session is initialized
    if '_id' not in session:
        session_id = secrets.token_hex(16)
        session['_id'] = session_id
        session.permanent = True
        session.modified = True
    
    parser = get_mind_map_parser()
    if parser:
        tags = parser.get_all_tags()
        return jsonify({
            'loaded': True,
            'filename': session.get('mind_map_filename', 'Mind Map'),
            'tags_count': len(tags),
            'session_id': session.get('_id')  # For debugging
        })
    return jsonify({
        'loaded': False,
        'session_id': session.get('_id')  # For debugging
    })

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
        
        if not scenario.strip():
            error_msg = 'Please provide a customer scenario' if language == 'en' else 'الرجاء إدخال سيناريو العميل'
            return jsonify({'error': error_msg}), 400
        
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
                try:
                    os.remove(file_path)
                except:
                    pass  # Ignore cleanup errors
        
        # Always return JSON, even if result has error
        return jsonify(result)
    
    except Exception as e:
        # Always return JSON error response
        error_msg = str(e)
        error_response = {
            'error': 'AI Analysis Failed',
            'details': error_msg
        }
        
        # Add helpful messages for common errors
        # IMPORTANT: Check for SAFETY_FILTER_BLOCKED first to avoid misclassifying as API key error
        if 'SAFETY_FILTER_BLOCKED' in error_msg or ('safety' in error_msg.lower() and 'blocked' in error_msg.lower()):
            error_response['solution'] = 'The content was blocked by safety filters. This is an intermittent issue. The system will retry automatically. If this persists, try rephrasing your scenario.'
        elif ('API key' in error_msg.lower() and 'invalid' in error_msg.lower()) or ('403' in error_msg and 'permission' in error_msg.lower() and 'API key' in error_msg.lower()):
            # Only show API key error for actual API key issues, not safety filter blocks
            error_response['solution'] = 'Please check your GEMINI_API_KEY in environment variables.'
        elif 'rate limit' in error_msg.lower() or '429' in error_msg or 'quota' in error_msg.lower():
            error_response['solution'] = 'API rate limit exceeded. Please wait 2-3 minutes and try again.'
        
        return jsonify(error_response), 500

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

# Cleanup old session data periodically (older than 24 hours)
def cleanup_old_sessions():
    """Remove old session data from file-based storage"""
    if not os.path.exists(MIND_MAP_STORAGE_DIR):
        return
    
    current_time = time.time()
    expired_files = []
    
    # Check all storage files
    for filename in os.listdir(MIND_MAP_STORAGE_DIR):
        if filename.endswith('.json'):
            storage_file = os.path.join(MIND_MAP_STORAGE_DIR, filename)
            try:
                with open(storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    timestamp = data.get('timestamp', 0)
                    if current_time - timestamp > 86400:  # 24 hours
                        expired_files.append(storage_file)
            except Exception as e:
                print(f"Error reading storage file {filename}: {e}")
                # Remove corrupted files
                expired_files.append(storage_file)
    
    # Remove expired files
    for storage_file in expired_files:
        try:
            os.remove(storage_file)
            print(f"Cleaned up expired storage file: {storage_file}")
        except Exception as e:
            print(f"Error removing storage file {storage_file}: {e}")

# Cleanup on startup
cleanup_old_sessions()

if __name__ == '__main__':
    # Get host and port from environment variables, with defaults
    # For Fly.io and cloud deployment, use PORT environment variable
    port = int(os.getenv('PORT', os.getenv('FLASK_PORT', 5000)))
    host = os.getenv('FLASK_HOST', '0.0.0.0')  # Use 0.0.0.0 for cloud, 127.0.0.1 for local
    debug = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug, host=host, port=port)

