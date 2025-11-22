"""
AI Analyzer
Uses AI to analyze customer scenarios and suggest appropriate tags
Uses Google Gemini API (free tier available)
"""

import os
import json
import time
from collections import deque

class AIAnalyzer:
    def __init__(self, mind_map_parser):
        """Initialize AI analyzer with mind map parser"""
        self.mind_map_parser = mind_map_parser
        
        # Request throttling: track request times to avoid rate limits
        # Free tier: 15 requests/minute = 1 request per 4 seconds
        # Using very conservative 20 seconds to be extra safe
        self.request_times = deque(maxlen=15)  # Keep last 15 request times
        self.min_request_interval = 20.0  # Minimum 20 seconds between requests (very conservative)
        
        # Use Gemini API (default and only provider)
        self.provider = os.getenv('AI_PROVIDER', 'gemini').lower()
        
        if self.provider == 'gemini':
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found. Get a free key at: https://makersuite.google.com/app/apikey")
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.genai = genai
            except ImportError:
                raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
        
        else:
            raise ValueError(f"Unknown AI provider: {self.provider}. Use 'gemini' (default)")
    
    def _throttle_request(self):
        """Throttle requests to avoid hitting rate limits"""
        current_time = time.time()
        
        # Remove requests older than 1 minute
        while self.request_times and current_time - self.request_times[0] > 60:
            self.request_times.popleft()
        
        # If we have 15 requests in the last minute, wait longer
        if len(self.request_times) >= 15:
            # Wait until the oldest request is more than 1 minute old, plus extra buffer
            wait_time = 60 - (current_time - self.request_times[0]) + 2
            if wait_time > 0:
                time.sleep(wait_time)
                current_time = time.time()
        
        # Ensure minimum interval between requests (very conservative 20 seconds)
        if self.request_times:
            time_since_last = current_time - self.request_times[-1]
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                print(f"[Throttle] Waiting {wait_time:.1f} seconds before next request...")
                time.sleep(wait_time)
                current_time = time.time()
        else:
            # First request - add a longer delay to avoid immediate rate limit
            print("[Throttle] First request - waiting 5 seconds...")
            time.sleep(5)
            current_time = time.time()
        
        # Record this request
        self.request_times.append(current_time)
    
    def analyze_scenario(self, scenario_text, file_paths=None, language='en'):
        """Analyze customer scenario and suggest tags"""
        if not scenario_text.strip():
            error_msg = 'Please provide a customer scenario' if language == 'en' else 'الرجاء إدخال سيناريو العميل'
            return {'error': error_msg}
        
        # Prepare optimized mind map context (summary to reduce token usage)
        # Use summary instead of full data to reduce API costs and rate limit issues
        mind_map_context = self.mind_map_parser.get_mind_map_summary()
        
        # If summary is still too large, truncate it
        if len(mind_map_context) > 5000:  # Limit to ~5000 characters
            mind_map_context = mind_map_context[:5000] + "\n... (truncated for efficiency)"
        
        # Detect if input is Arabic (simple heuristic)
        is_arabic = self._is_arabic_text(scenario_text) or language == 'ar'
        
        # Build optimized, shorter system prompt to reduce token usage
        if is_arabic:
            system_prompt = f"""Analyze customer scenarios and recommend tags from the mind map.

MIND MAP:
{mind_map_context}

TASK: Match scenario to mind map tags. Output in English only.

FORMAT:
- Recommended Tag(s): [exact tag names from mind map]
- Confidence: [High/Medium/Low]
- Reasoning: [brief explanation in English]
- Mind Map Reference: [sheet/row reference]"""
        else:
            system_prompt = f"""Analyze customer scenarios and recommend tags from the mind map.

MIND MAP:
{mind_map_context}

TASK: Match scenario to mind map tags.

FORMAT:
- Recommended Tag(s): [exact tag names from mind map]
- Confidence: [High/Medium/Low]
- Reasoning: [brief explanation]
- Mind Map Reference: [sheet/row reference]"""
        
        # Build messages for AI
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add user scenario (optimized, shorter prompt)
        user_content = f"SCENARIO:\n{scenario_text}\n\nAnalyze and recommend tags. Output in English."
        
        # Handle file attachments (images/videos)
        if file_paths:
            user_content += "\n\nATTACHED FILES:"
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_ext = os.path.splitext(file_path)[1].lower()
                    
                    # Check if it's an image (Gemini handles images directly, no need for base64 encoding here)
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        # Images will be handled in _call_gemini method
                        pass
                    elif file_ext in ['.mp4', '.mov', '.avi', '.webm']:
                        # For videos, we'll note them but Gemini API doesn't support video directly
                        # We could extract frames or use a different approach
                        user_content += f"\n- Video file: {os.path.basename(file_path)} (Note: Video content will be described by the user)"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        try:
            # Call Gemini API
            if self.provider == 'gemini':
                ai_response = self._call_gemini(messages, file_paths, scenario_text)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}. Only 'gemini' is supported.")
            
            # Parse response to extract structured information
            result = self._parse_ai_response(ai_response)
            result['full_response'] = ai_response
            
            return result
            
        except Exception as e:
            error_str = str(e)
            # Provide user-friendly error messages for Gemini
            if 'API key' in error_str or 'permission' in error_str.lower() or '403' in error_str:
                return {
                    'error': 'Invalid Gemini API Key',
                    'details': 'The Gemini API key is invalid or has insufficient permissions.',
                    'solution': 'Please check your GEMINI_API_KEY in the .env file. Get a free key at: https://makersuite.google.com/app/apikey',
                    'full_error': error_str
                }
            elif 'rate limit' in error_str.lower() or 'quota' in error_str.lower() or '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                # Calculate suggested wait time
                wait_minutes = 2
                if 'minute' in error_str.lower():
                    wait_minutes = 2
                elif 'hour' in error_str.lower() or 'day' in error_str.lower():
                    wait_minutes = 60
                
                return {
                    'error': 'Gemini API Rate Limit Exceeded',
                    'details': f'Your API key has exceeded the rate limit. This can happen if the key was used recently or shared with others.',
                    'solution': f'Please wait {wait_minutes} minutes before trying again. Free tier limits: 15 requests/minute, 1,500 requests/day. If this persists, consider getting a new API key from https://makersuite.google.com/app/apikey',
                    'full_error': error_str
                }
            elif 'safety' in error_str.lower() or 'blocked' in error_str.lower():
                return {
                    'error': 'Content Blocked by Safety Filters',
                    'details': 'The content was blocked by Gemini safety filters.',
                    'solution': 'Please try rephrasing your scenario description.',
                    'full_error': error_str
                }
            elif 'model not available' in error_str.lower() or '404' in error_str:
                return {
                    'error': 'Gemini Model Not Available',
                    'details': 'The requested Gemini model is not available.',
                    'solution': 'The app will try to use an alternative model automatically.',
                    'full_error': error_str
                }
            else:
                return {
                    'error': 'AI Analysis Failed',
                    'details': error_str,
                    'full_error': error_str
                }
    
    def _call_gemini(self, messages, file_paths, scenario_text):
        """Call Google Gemini API (FREE tier available) with retry logic and throttling"""
        # Throttle request to avoid rate limits
        self._throttle_request()
        
        # Import Google API exceptions for better error handling
        try:
            from google.api_core import exceptions as google_exceptions
        except ImportError:
            google_exceptions = None
        
        # Extract system prompt and user content from messages
        system_prompt = messages[0]["content"] if messages and messages[0].get("role") == "system" else ""
        user_content = messages[-1]["content"] if messages and messages[-1].get("role") == "user" else scenario_text
        
        # Combine system prompt and user content for Gemini
        prompt = f"{system_prompt}\n\n{user_content}"
        
        # Prepare content parts (text + images if any)
        content_parts = [prompt]
        
        # Add images if provided
        if file_paths:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_ext = os.path.splitext(file_path)[1].lower()
                    if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        import PIL.Image
                        img = PIL.Image.open(file_path)
                        content_parts.append(img)
        
        # Use single model only - gemini-2.5-flash (as specified)
        model_name = "gemini-2.5-flash"
        max_retries = 0  # NO retries - single attempt only to avoid multiple API calls
        base_delay = 30  # Start with 30 seconds delay (very conservative)
        
        # Single attempt only - no retries
        try:
            # Verify model is available before making request
            try:
                model = self.genai.GenerativeModel(model_name)
                print(f"[API] Using model: {model_name} with key: {os.getenv('GEMINI_API_KEY')[:20]}...")
            except Exception as model_error:
                error_msg = str(model_error)
                if "404" in error_msg or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                    raise Exception(f"Model '{model_name}' not available. The model may not exist or your API key doesn't have access. Error: {error_msg}")
                raise
            
            # For text-only requests
            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 1500,  # Reduced to save tokens
                    }
                )
            else:
                # For requests with images, use content_parts
                response = model.generate_content(
                    content_parts,
                    generation_config={
                        "temperature": 0.3,
                        "max_output_tokens": 1500,  # Reduced to save tokens
                    }
                )
            
            # Check response structure - handle safety filters FIRST before accessing text
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Check finish_reason FIRST (before trying to access text)
                # finish_reason 2 = SAFETY, 3 = RECITATION, etc.
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                # Handle safety filters - check both string and numeric codes
                if finish_reason == 'SAFETY' or finish_reason == 2:
                    raise Exception("Content was blocked by Gemini safety filters. Please try rephrasing your scenario in a more neutral way.")
                
                # Handle other blocking reasons
                if finish_reason and finish_reason != 1:  # 1 = STOP (success)
                    reason_map = {
                        2: 'SAFETY',
                        3: 'RECITATION',
                        4: 'OTHER',
                        5: 'MAX_TOKENS'
                    }
                    reason_name = reason_map.get(finish_reason, f'REASON_{finish_reason}')
                    raise Exception(f"Gemini API response blocked: {reason_name}. Please try rephrasing your scenario.")
                
                # Now safely try to get text (only if finish_reason is OK)
                # Try response.text first (easiest)
                try:
                    if hasattr(response, 'text') and response.text:
                        return response.text
                except Exception:
                    # If response.text fails, try accessing parts directly
                    pass
                
                # Try accessing text from candidate parts
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        if len(candidate.content.parts) > 0:
                            part = candidate.content.parts[0]
                            if hasattr(part, 'text'):
                                return part.text
                            elif isinstance(part, dict) and 'text' in part:
                                return part['text']
                
                # If we get here, no text was found
                raise Exception("Empty response from Gemini API - no text content returned")
            
            # Fallback: try response.text if no candidates structure
            elif hasattr(response, 'text') and response.text:
                return response.text
            else:
                raise Exception("Empty response from Gemini API - no candidates or text returned")
                
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Better error handling for Gemini
            if "404" in error_msg or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                raise Exception(f"Gemini model '{model_name}' not available. Error: {error_msg}")
            elif "403" in error_msg or "permission" in error_msg.lower() or "API key" in error_msg.lower():
                raise Exception(f"Gemini API key invalid or permission denied. Please check your GEMINI_API_KEY in .env file. Error: {error_msg}")
            elif ("429" in error_msg or 
                  "quota" in error_msg.lower() or 
                  "rate limit" in error_msg.lower() or 
                  "RESOURCE_EXHAUSTED" in error_msg or
                  "resource_exhausted" in error_msg.lower() or
                  "Quota exceeded" in error_msg or
                  "quota exceeded" in error_msg.lower()):
                # Check if this is actually a rate limit or a model error
                if "404" in error_msg or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                    raise Exception(f"Model '{model_name}' not available. This might be causing the error. Try using 'gemini-1.5-flash' instead. Error: {error_msg}")
                raise Exception(f"Gemini API rate limit exceeded. Please wait 2-3 minutes and try again. Free tier: 15 requests/minute, 1,500 requests/day. Error: {error_msg}")
            elif "safety" in error_msg.lower() or "blocked" in error_msg.lower():
                raise Exception(f"Content was blocked by Gemini safety filters. Please try rephrasing your scenario. Error: {error_msg}")
            else:
                raise Exception(f"Gemini API error: {error_msg}")
    
    def _is_arabic_text(self, text):
        """Check if text contains Arabic characters"""
        arabic_chars = set('ابتثجحخدذرزسشصضطظعغفقكلمنهوي')
        text_chars = set(text.replace(' ', '').replace('\n', ''))
        # If more than 30% of characters are Arabic, consider it Arabic
        if len(text_chars) == 0:
            return False
        arabic_ratio = len(text_chars & arabic_chars) / len(text_chars)
        return arabic_ratio > 0.3
    
    def _parse_ai_response(self, response_text):
        """Parse AI response to extract structured information"""
        result = {
            'tags': [],
            'confidence': 'Medium',
            'reasoning': '',
            'mind_map_reference': ''
        }
        
        is_arabic = self._is_arabic_text(response_text)
        
        lines = response_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract tags (support both English and Arabic)
            if ('recommended tag' in line.lower() or 'tag(s)' in line.lower() or 
                'العلامة' in line or 'العلامات' in line or 'موصى بها' in line):
                # Extract tag names
                if ':' in line or ':' in line:
                    separator = ':' if ':' in line else ':'
                    tag_part = line.split(separator, 1)[1].strip()
                    # Remove brackets and split
                    tag_part = tag_part.replace('[', '').replace(']', '').replace(']', '').replace('[', '')
                    tags = [t.strip() for t in tag_part.split(',')]
                    result['tags'] = [t for t in tags if t]
            
            # Extract confidence (support both languages)
            if ('confidence' in line.lower() or 'الثقة' in line or 'مستوى الثقة' in line) and (':' in line or ':' in line):
                separator = ':' if ':' in line else ':'
                conf = line.split(separator, 1)[1].strip()
                conf = conf.replace('[', '').replace(']', '').replace(']', '').replace('[', '')
                # Translate Arabic confidence levels
                if is_arabic:
                    conf_lower = conf.lower()
                    if 'عالي' in conf_lower or 'عالية' in conf_lower or 'high' in conf_lower:
                        result['confidence'] = 'High'
                    elif 'منخفض' in conf_lower or 'منخفضة' in conf_lower or 'low' in conf_lower:
                        result['confidence'] = 'Low'
                    else:
                        result['confidence'] = 'Medium'
                else:
                    result['confidence'] = conf
            
            # Extract reasoning (support both languages)
            if 'reasoning' in line.lower() or 'المنطق' in line or 'الاستدلال' in line:
                current_section = 'reasoning'
                separator = ':' if ':' in line else ':'
                if separator in line:
                    result['reasoning'] = line.split(separator, 1)[1].strip()
                continue
            
            # Extract mind map reference (support both languages)
            if ('mind map reference' in line.lower() or 'reference' in line.lower() or 
                'مرجع' in line or 'خريطة العقل' in line):
                current_section = 'reference'
                separator = ':' if ':' in line else ':'
                if separator in line:
                    result['mind_map_reference'] = line.split(separator, 1)[1].strip()
                continue
            
            # Continue adding to current section
            if current_section == 'reasoning':
                result['reasoning'] += ' ' + line
            elif current_section == 'reference':
                result['mind_map_reference'] += ' ' + line
        
        # Clean up
        result['reasoning'] = result['reasoning'].strip()
        result['mind_map_reference'] = result['mind_map_reference'].strip()
        
        return result

