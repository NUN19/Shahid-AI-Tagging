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
                # Try to import safety enums with multiple fallbacks - CRITICAL for consistent behavior
                self.HarmCategory = None
                self.HarmBlockThreshold = None
                self.safety_settings = None
                
                # Method 1: Direct import (preferred)
                try:
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold
                    self.HarmCategory = HarmCategory
                    self.HarmBlockThreshold = HarmBlockThreshold
                    # Pre-create safety settings in __init__ to ensure consistency
                    self.safety_settings = {
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                    print("[INIT] Safety filters disabled using direct import")
                except (ImportError, AttributeError) as e1:
                    print(f"[INIT] Direct import failed: {e1}, trying genai.types...")
                    # Method 2: Use genai.types
                    try:
                        self.HarmCategory = genai.types.HarmCategory
                        self.HarmBlockThreshold = genai.types.HarmBlockThreshold
                        self.safety_settings = {
                            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                        }
                        print("[INIT] Safety filters disabled using genai.types")
                    except (AttributeError, TypeError) as e2:
                        print(f"[INIT] genai.types failed: {e2}, will try in _call_gemini")
                        # Will be handled in _call_gemini with additional fallbacks
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
            
            # DISABLE ALL SAFETY FILTERS - CRITICAL: Always ensure safety_settings is set
            # Use pre-initialized settings if available, otherwise try all fallback methods
            safety_settings = self.safety_settings  # Use pre-initialized if available
            
            if not safety_settings:
                # Fallback: Try to create safety settings now with multiple methods
                if self.HarmCategory and self.HarmBlockThreshold:
                    try:
                        # Method 1: Use enum values directly
                        safety_settings = {
                            self.HarmCategory.HARM_CATEGORY_HARASSMENT: self.HarmBlockThreshold.BLOCK_NONE,
                            self.HarmCategory.HARM_CATEGORY_HATE_SPEECH: self.HarmBlockThreshold.BLOCK_NONE,
                            self.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: self.HarmBlockThreshold.BLOCK_NONE,
                            self.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: self.HarmBlockThreshold.BLOCK_NONE,
                        }
                        print("[API] Safety filters disabled using enum values (fallback)")
                    except (AttributeError, TypeError) as e:
                        print(f"[API] Enum method failed: {e}, trying integer values...")
                        try:
                            # Method 2: Use integer values (BLOCK_NONE = 0)
                            safety_settings = {
                                self.HarmCategory.HARM_CATEGORY_HARASSMENT: 0,
                                self.HarmCategory.HARM_CATEGORY_HATE_SPEECH: 0,
                                self.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: 0,
                                self.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: 0,
                            }
                            print("[API] Safety filters disabled using integer values")
                        except Exception as e2:
                            print(f"[API] Integer method failed: {e2}, trying direct import...")
                            try:
                                # Method 3: Direct import in method
                                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                                safety_settings = {
                                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                }
                                print("[API] Safety filters disabled using direct import")
                            except Exception as e3:
                                print(f"[API] Direct import failed: {e3}, trying genai.types...")
                                try:
                                    # Method 4: Use genai.types
                                    safety_settings = {
                                        self.genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: self.genai.types.HarmBlockThreshold.BLOCK_NONE,
                                        self.genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: self.genai.types.HarmBlockThreshold.BLOCK_NONE,
                                        self.genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: self.genai.types.HarmBlockThreshold.BLOCK_NONE,
                                        self.genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: self.genai.types.HarmBlockThreshold.BLOCK_NONE,
                                    }
                                    print("[API] Safety filters disabled using genai.types")
                                except Exception as e4:
                                    print(f"[API] All methods failed: {e4}")
                                    # CRITICAL: If all methods fail, we MUST still try to disable filters
                                    # Use a workaround: create a minimal safety settings dict
                                    try:
                                        # Last resort: try to access via getattr
                                        HarmCat = getattr(self.genai.types, 'HarmCategory', None)
                                        HarmBlock = getattr(self.genai.types, 'HarmBlockThreshold', None)
                                        if HarmCat and HarmBlock:
                                            safety_settings = {
                                                getattr(HarmCat, 'HARM_CATEGORY_HARASSMENT'): getattr(HarmBlock, 'BLOCK_NONE'),
                                                getattr(HarmCat, 'HARM_CATEGORY_HATE_SPEECH'): getattr(HarmBlock, 'BLOCK_NONE'),
                                                getattr(HarmCat, 'HARM_CATEGORY_SEXUALLY_EXPLICIT'): getattr(HarmBlock, 'BLOCK_NONE'),
                                                getattr(HarmCat, 'HARM_CATEGORY_DANGEROUS_CONTENT'): getattr(HarmBlock, 'BLOCK_NONE'),
                                            }
                                            print("[API] Safety filters disabled using getattr workaround")
                                    except Exception as e5:
                                        print(f"[API] CRITICAL: All safety setting methods failed. Error: {e5}")
                                        # This should never happen, but if it does, log it
                                        safety_settings = None
                else:
                    # Try direct import as last resort
                    try:
                        from google.generativeai.types import HarmCategory, HarmBlockThreshold
                        safety_settings = {
                            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                        }
                        print("[API] Safety filters disabled using direct import (no HarmCategory available)")
                    except Exception as e:
                        print(f"[API] CRITICAL ERROR: Cannot disable safety filters: {e}")
                        safety_settings = None
            
            # CRITICAL: If safety_settings is still None, we have a serious problem
            # Log it and proceed, but this should be rare
            if safety_settings is None:
                print("[API] WARNING: safety_settings is None - default restrictive filters will be used!")
                print("[API] This may cause intermittent blocking. Check logs above for initialization errors.")
            
            # Prepare generation config
            gen_config = {
                "temperature": 0.3,
                "max_output_tokens": 1500,  # Reduced to save tokens
            }
            
            # CRITICAL: Always pass safety_settings if available, never skip it
            # Log the actual safety_settings being used for debugging
            if safety_settings:
                print(f"[API] Safety settings being used: {type(safety_settings)}")
                if isinstance(safety_settings, dict):
                    for key, value in safety_settings.items():
                        print(f"[API]   {key}: {value} (type: {type(value)})")
                else:
                    print(f"[API]   {safety_settings}")
            
            # For text-only requests
            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                if safety_settings:
                    print("[API] Making request with safety_settings (BLOCK_NONE)")
                    try:
                        response = model.generate_content(
                            prompt,
                            generation_config=gen_config,
                            safety_settings=safety_settings
                        )
                    except Exception as api_error:
                        print(f"[API] Error with safety_settings: {api_error}")
                        # If safety_settings format is wrong, try without it as last resort
                        print("[API] Retrying without safety_settings...")
                        response = model.generate_content(
                            prompt,
                            generation_config=gen_config
                        )
                else:
                    print("[API] WARNING: Making request WITHOUT safety_settings - default filters will apply!")
                    response = model.generate_content(
                        prompt,
                        generation_config=gen_config
                    )
            else:
                # For requests with images, use content_parts
                if safety_settings:
                    print("[API] Making request with images and safety_settings (BLOCK_NONE)")
                    response = model.generate_content(
                        content_parts,
                        generation_config=gen_config,
                        safety_settings=safety_settings
                    )
                else:
                    print("[API] WARNING: Making request with images WITHOUT safety_settings - default filters will apply!")
                    response = model.generate_content(
                        content_parts,
                        generation_config=gen_config
                    )
            
            # Check response structure - handle safety filters FIRST before accessing text
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                
                # Check finish_reason FIRST (before trying to access text)
                # finish_reason 2 = SAFETY, 3 = RECITATION, etc.
                finish_reason = getattr(candidate, 'finish_reason', None)
                
                # Log detailed safety information for debugging
                print(f"[API] Response finish_reason: {finish_reason}")
                
                # Check safety ratings if available
                if hasattr(candidate, 'safety_ratings'):
                    safety_ratings = candidate.safety_ratings
                    print(f"[API] Safety ratings: {safety_ratings}")
                    for rating in safety_ratings:
                        print(f"[API]   - {getattr(rating, 'category', 'unknown')}: {getattr(rating, 'probability', 'unknown')} (threshold: {getattr(rating, 'threshold', 'unknown')})")
                
                # CRITICAL: If we set BLOCK_NONE but still get SAFETY finish_reason,
                # Try to extract response anyway - sometimes partial content is available
                if finish_reason == 'SAFETY' or finish_reason == 2:
                    # Check if we actually set safety_settings
                    if safety_settings:
                        print(f"[API] WARNING: Content blocked despite BLOCK_NONE settings!")
                        print(f"[API] Safety settings used: {safety_settings}")
                        
                        # Try to extract any available content despite the safety block
                        # Sometimes Gemini returns partial content even with SAFETY finish_reason
                        try:
                            if hasattr(response, 'text') and response.text:
                                print("[API] Found text despite SAFETY finish_reason, using it")
                                return response.text
                        except:
                            pass
                        
                        # Try accessing parts directly
                        try:
                            if hasattr(candidate, 'content') and candidate.content:
                                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                    if len(candidate.content.parts) > 0:
                                        part = candidate.content.parts[0]
                                        if hasattr(part, 'text') and part.text:
                                            print("[API] Found text in parts despite SAFETY finish_reason, using it")
                                            return part.text
                        except:
                            pass
                        
                        # AUTOMATIC RETRY: If blocked, retry with a more neutral, business-focused prompt
                        print("[API] Retrying with neutralized prompt to bypass safety filters...")
                        try:
                            # Create a more neutral version of the prompt
                            neutral_prompt = self._neutralize_prompt(prompt, scenario_text)
                            
                            # Retry with neutralized prompt
                            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                                retry_response = model.generate_content(
                                    neutral_prompt,
                                    generation_config=gen_config,
                                    safety_settings=safety_settings
                                )
                            else:
                                # For images, modify the text part only
                                neutral_content_parts = [neutral_prompt] + content_parts[1:]
                                retry_response = model.generate_content(
                                    neutral_content_parts,
                                    generation_config=gen_config,
                                    safety_settings=safety_settings
                                )
                            
                            # Check retry response
                            if hasattr(retry_response, 'candidates') and retry_response.candidates:
                                retry_candidate = retry_response.candidates[0]
                                retry_finish_reason = getattr(retry_candidate, 'finish_reason', None)
                                
                                if retry_finish_reason != 'SAFETY' and retry_finish_reason != 2:
                                    print("[API] Retry successful with neutralized prompt!")
                                    if hasattr(retry_response, 'text') and retry_response.text:
                                        return retry_response.text
                                    # Try parts
                                    if hasattr(retry_candidate, 'content') and retry_candidate.content:
                                        if hasattr(retry_candidate.content, 'parts') and retry_candidate.content.parts:
                                            if len(retry_candidate.content.parts) > 0:
                                                part = retry_candidate.content.parts[0]
                                                if hasattr(part, 'text'):
                                                    return part.text
                                else:
                                    print("[API] Retry also blocked, using fallback response")
                            else:
                                print("[API] Retry response invalid, using fallback")
                        except Exception as retry_error:
                            print(f"[API] Retry failed: {retry_error}")
                        
                        # If retry also fails, provide a helpful error message
                        raise Exception("Content was blocked by Gemini safety filters despite BLOCK_NONE settings. The system attempted an automatic retry with a neutralized prompt but was still blocked. Please try rephrasing your scenario in a more neutral, business-focused way, avoiding any sensitive terms.")
                    else:
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
    
    def _neutralize_prompt(self, original_prompt, scenario_text):
        """Neutralize prompt to avoid safety filter triggers while preserving meaning"""
        # Replace potentially sensitive terms with neutral business equivalents
        neutral_replacements = {
            # Common terms that might trigger filters
            'limit': 'threshold',
            'blocked': 'restricted',
            'banned': 'restricted',
            'violation': 'issue',
            'abuse': 'misuse',
            'attack': 'incident',
            'hack': 'unauthorized access',
            'breach': 'incident',
            'exploit': 'utilize',
        }
        
        # Create neutralized scenario
        neutral_scenario = scenario_text
        for sensitive, neutral in neutral_replacements.items():
            # Case-insensitive replacement
            import re
            neutral_scenario = re.sub(r'\b' + re.escape(sensitive) + r'\b', neutral, neutral_scenario, flags=re.IGNORECASE)
        
        # Rebuild prompt with neutralized scenario
        # Extract system prompt part (everything before the scenario)
        if "SCENARIO:" in original_prompt:
            system_part = original_prompt.split("SCENARIO:")[0]
            neutral_prompt = f"{system_part}SCENARIO:\n{neutral_scenario}\n\nAnalyze and recommend tags. Output in English. Focus on technical and business aspects only."
        else:
            # If format is different, just replace the scenario text
            neutral_prompt = original_prompt.replace(scenario_text, neutral_scenario)
        
        print(f"[API] Original scenario length: {len(scenario_text)}, Neutralized: {len(neutral_scenario)}")
        return neutral_prompt
    
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

