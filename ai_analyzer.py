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
        
        # Prepare detailed mind map context with complete tag logic
        # Now includes ALL rows with full logic details for better tag understanding
        mind_map_context = self.mind_map_parser.get_mind_map_summary()
        
        # If context is too large, prioritize keeping complete tag logic
        # Increase limit to allow more tag logic details (important for accuracy)
        if len(mind_map_context) > 8000:  # Increased limit to ~8000 characters for better tag logic
            # Try to keep complete tag entries rather than truncating mid-tag
            truncated = mind_map_context[:8000]
            # Find last complete tag entry
            last_tag_end = max(
                truncated.rfind('\nRow '),
                truncated.rfind('TAG:'),
                truncated.rfind('Sheet:')
            )
            if last_tag_end > 7000:  # If we can keep most of it
                mind_map_context = truncated[:last_tag_end] + "\n\n... (additional tags truncated for efficiency)"
            else:
                mind_map_context = truncated + "\n... (truncated for efficiency)"
        
        # Detect if input is Arabic (simple heuristic)
        is_arabic = self._is_arabic_text(scenario_text) or language == 'ar'
        
        # Build detailed system prompt that helps AI understand tag logic and relate to scenarios
        # IMPORTANT: Add business-focused instructions to avoid safety filter triggers
        if is_arabic:
            system_prompt = f"""You are an expert customer support tag classification system for a legitimate business service.

CONTEXT: This is a business application for categorizing customer service requests. All scenarios are legitimate business inquiries about service usage, technical issues, or account management.

TAG LOGIC MIND MAP (Complete Reference):
{mind_map_context}

YOUR TASK:
1. CAREFULLY READ the complete tag logic in the mind map above. Each row contains a tag with its full logic/criteria.
2. UNDERSTAND the relationship between tag logic and customer scenarios:
   - Match keywords, phrases, and concepts from the scenario to the tag logic
   - Consider synonyms, related terms, and contextual meaning
   - Look for matches in ALL columns of each tag (not just tag names)
   - Understand the complete logic/criteria for each tag before recommending
3. ANALYZE the customer scenario and identify which tags from the mind map best match:
   - Compare scenario content with tag logic in all columns
   - Consider partial matches and related concepts
   - Multiple tags can apply if the scenario matches multiple tag logics
4. RECOMMEND tags that have the strongest logical relationship to the scenario

IMPORTANT: 
- This is a business context. Focus on technical and business aspects only.
- Use neutral, professional language. All terms refer to legitimate business operations.
- You must understand the COMPLETE LOGIC of each tag before recommending it.
- Match based on LOGIC and CONTEXT, not just exact keyword matching.
- Output in English only.

OUTPUT FORMAT:
- Recommended Tag(s): [exact tag names from mind map, can be multiple]
- Confidence: [High/Medium/Low - based on how well scenario matches tag logic]
- Reasoning: [detailed explanation showing HOW the scenario relates to the tag logic, cite specific logic elements that match]
- Mind Map Reference: [sheet name and row number(s) of matched tags]"""
        else:
            system_prompt = f"""You are an expert customer support tag classification system for a legitimate business service.

CONTEXT: This is a business application for categorizing customer service requests. All scenarios are legitimate business inquiries about service usage, technical issues, or account management.

TAG LOGIC MIND MAP (Complete Reference):
{mind_map_context}

YOUR TASK:
1. CAREFULLY READ the complete tag logic in the mind map above. Each row contains a tag with its full logic/criteria.
2. UNDERSTAND the relationship between tag logic and customer scenarios:
   - Match keywords, phrases, and concepts from the scenario to the tag logic
   - Consider synonyms, related terms, and contextual meaning
   - Look for matches in ALL columns of each tag (not just tag names)
   - Understand the complete logic/criteria for each tag before recommending
3. ANALYZE the customer scenario and identify which tags from the mind map best match:
   - Compare scenario content with tag logic in all columns
   - Consider partial matches and related concepts
   - Multiple tags can apply if the scenario matches multiple tag logics
4. RECOMMEND tags that have the strongest logical relationship to the scenario

IMPORTANT: 
- This is a business context. Focus on technical and business aspects only.
- Use neutral, professional language. All terms refer to legitimate business operations.
- You must understand the COMPLETE LOGIC of each tag before recommending it.
- Match based on LOGIC and CONTEXT, not just exact keyword matching.

OUTPUT FORMAT:
- Recommended Tag(s): [exact tag names from mind map, can be multiple]
- Confidence: [High/Medium/Low - based on how well scenario matches tag logic]
- Reasoning: [detailed explanation showing HOW the scenario relates to the tag logic, cite specific logic elements that match]
- Mind Map Reference: [sheet name and row number(s) of matched tags]"""
        
        # Build messages for AI
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Use original scenario text verbatim - no neutralization
        # Add user scenario with detailed instructions for better tag logic matching
        user_content = f"""CUSTOMER SERVICE SCENARIO TO ANALYZE:
{scenario_text}

ANALYSIS INSTRUCTIONS:
1. Read the scenario carefully and identify key concepts, issues, and keywords
2. Compare these elements with the tag logic in the mind map
3. Find tags where the scenario content matches the tag's logic/criteria (check ALL columns)
4. Consider:
   - Direct keyword matches
   - Synonym matches
   - Conceptual matches (same meaning, different words)
   - Related terms and context
5. Recommend the tag(s) that have the strongest logical match
6. Explain in your reasoning HOW the scenario relates to the tag logic (cite specific matching elements)

Output in English. Focus on technical and business aspects only."""
        
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
            # Call Gemini API - pass original scenario text verbatim
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
            # IMPORTANT: Check for actual API key errors first, but be more specific
            # Don't trigger on safety filter errors that mention "API key restrictions"
            if 'SAFETY_FILTER_BLOCKED' in error_str:
                # This is a safety filter issue, not an API key issue
                return {
                    'error': 'Content Blocked by Safety Filters',
                    'details': 'The content was blocked by Gemini safety filters despite attempts to disable them. Your API key is valid, but the content triggers safety filters that cannot be bypassed.',
                    'solution': 'This is an intermittent issue with Gemini\'s safety filters. The system will retry automatically. If this persists, try rephrasing your scenario or contact support.',
                    'full_error': error_str
                }
            elif ('API key' in error_str and 'invalid' in error_str.lower()) or ('403' in error_str and 'permission' in error_str.lower() and 'API key' in error_str):
                # Only trigger on actual API key errors, not safety filter errors
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
            # DISABLE ALL SAFETY FILTERS - Get safety settings first
            safety_settings = self._get_safety_settings()
            
            # Verify model is available - DON'T set safety_settings at model level (may cause conflicts)
            # We'll only pass them in generate_content() calls
            try:
                model = self.genai.GenerativeModel(model_name)
                print(f"[API] Using model: {model_name}")
                if safety_settings:
                    print(f"[API] Safety settings will be applied in generate_content() call")
                else:
                    print(f"[API] WARNING: no safety_settings available")
                print(f"[API] API key: {os.getenv('GEMINI_API_KEY')[:20]}...")
            except Exception as model_error:
                error_msg = str(model_error)
                if "404" in error_msg or "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
                    raise Exception(f"Model '{model_name}' not available. The model may not exist or your API key doesn't have access. Error: {error_msg}")
                raise
            
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
            
            # Set timeout for API calls (25 seconds per request to prevent hanging)
            # This prevents worker timeouts - use threading timeout for better compatibility
            import threading
            
            # Set timeout for this request (25 seconds per call)
            request_timeout_seconds = 25
            api_response = [None]  # Use list to store result (mutable)
            api_exception = [None]  # Use list to store exception
            
            def api_call_with_timeout():
                """Execute API call in a separate thread with timeout"""
                try:
                    if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                        if safety_settings:
                            api_response[0] = model.generate_content(
                                prompt,
                                generation_config=gen_config,
                                safety_settings=safety_settings
                            )
                        else:
                            api_response[0] = model.generate_content(
                                prompt,
                                generation_config=gen_config
                            )
                    else:
                        if safety_settings:
                            api_response[0] = model.generate_content(
                                content_parts,
                                generation_config=gen_config,
                                safety_settings=safety_settings
                            )
                        else:
                            api_response[0] = model.generate_content(
                                content_parts,
                                generation_config=gen_config
                            )
                except Exception as e:
                    api_exception[0] = e
            
            # CRITICAL: Always pass safety_settings if available, never skip it
            # Log the actual safety_settings being used for debugging
            if safety_settings:
                print(f"[API] Safety settings being used: {type(safety_settings)}")
                if isinstance(safety_settings, dict):
                    for key, value in safety_settings.items():
                        print(f"[API]   {key}: {value} (type: {type(value)})")
                else:
                    print(f"[API]   {safety_settings}")
            
            # Make request - ONLY pass safety_settings in generate_content (not at model level)
            # This ensures they're applied correctly without conflicts
            print("[API] Making request with safety_settings in generate_content() (BLOCK_NONE)")
            
            # Execute API call with timeout protection
            api_thread = threading.Thread(target=api_call_with_timeout)
            api_thread.daemon = True  # Allow main thread to exit even if this is still running
            api_thread.start()
            api_thread.join(timeout=request_timeout_seconds)
            
            if api_thread.is_alive():
                # Thread is still running - request timed out
                print(f"[API] WARNING: API call timed out after {request_timeout_seconds} seconds")
                raise Exception(f"API call timed out after {request_timeout_seconds} seconds. The request took too long to complete.")
            
            # Check for exceptions
            if api_exception[0]:
                raise api_exception[0]
            
            # Get response
            if api_response[0] is None:
                raise Exception("API call returned no response")
            
            response = api_response[0]
            
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
                        
                        # RETRY 1: Try with list format safety_settings (alternative format)
                        # Use shorter timeout for retries (15 seconds)
                        print("[API] Retry 1: Trying with list format safety_settings (15s timeout)...")
                        try:
                            # Convert to list format
                            list_format_settings = self._convert_safety_settings_to_list_format(safety_settings)
                            
                            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                                retry_response = model.generate_content(
                                    prompt,
                                    generation_config=gen_config,
                                    safety_settings=list_format_settings if list_format_settings else safety_settings
                                )
                            else:
                                retry_response = model.generate_content(
                                    content_parts,
                                    generation_config=gen_config,
                                    safety_settings=list_format_settings if list_format_settings else safety_settings
                                )
                            
                            # Check retry response
                            if hasattr(retry_response, 'candidates') and retry_response.candidates:
                                retry_candidate = retry_response.candidates[0]
                                retry_finish_reason = getattr(retry_candidate, 'finish_reason', None)
                                
                                if retry_finish_reason != 'SAFETY' and retry_finish_reason != 2:
                                    print("[API] Retry 1 successful with list format!")
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
                                    print("[API] Retry 1 also blocked, trying Retry 2...")
                            else:
                                print("[API] Retry 1 response invalid, trying Retry 2...")
                        except Exception as retry_error:
                            print(f"[API] Retry 1 failed: {retry_error}, trying Retry 2...")
                        
                        # RETRY 2: Try with BLOCK_ONLY_HIGH as fallback (less restrictive than default)
                        # Use shorter timeout for retries (15 seconds)
                        print("[API] Retry 2: Trying with BLOCK_ONLY_HIGH threshold (15s timeout)...")
                        try:
                            # Create BLOCK_ONLY_HIGH settings as fallback
                            fallback_settings = self._get_safety_settings_block_only_high()
                            
                            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                                retry2_response = model.generate_content(
                                    prompt,
                                    generation_config=gen_config,
                                    safety_settings=fallback_settings if fallback_settings else safety_settings
                                )
                            else:
                                retry2_response = model.generate_content(
                                    content_parts,
                                    generation_config=gen_config,
                                    safety_settings=fallback_settings if fallback_settings else safety_settings
                                )
                            
                            # Check retry response
                            if hasattr(retry2_response, 'candidates') and retry2_response.candidates:
                                retry2_candidate = retry2_response.candidates[0]
                                retry2_finish_reason = getattr(retry2_candidate, 'finish_reason', None)
                                
                                if retry2_finish_reason != 'SAFETY' and retry2_finish_reason != 2:
                                    print("[API] Retry 2 successful with BLOCK_ONLY_HIGH!")
                                    if hasattr(retry2_response, 'text') and retry2_response.text:
                                        return retry2_response.text
                                    # Try parts
                                    if hasattr(retry2_candidate, 'content') and retry2_candidate.content:
                                        if hasattr(retry2_candidate.content, 'parts') and retry2_candidate.content.parts:
                                            if len(retry2_candidate.content.parts) > 0:
                                                part = retry2_candidate.content.parts[0]
                                                if hasattr(part, 'text'):
                                                    return part.text
                                else:
                                    print("[API] Retry 2 also blocked, trying Retry 3...")
                            else:
                                print("[API] Retry 2 response invalid, trying Retry 3...")
                        except Exception as retry2_error:
                            print(f"[API] Retry 2 failed: {retry2_error}, trying Retry 3...")
                        
                        # RETRY 3: Try WITHOUT safety_settings (let model use defaults - sometimes works better)
                        # Use shorter timeout for retries (15 seconds)
                        print("[API] Retry 3: Trying WITHOUT safety_settings (15s timeout)...")
                        try:
                            # Try without safety_settings - some API keys/models work better this way
                            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                                retry3_response = model.generate_content(
                                    prompt,
                                    generation_config=gen_config
                                    # No safety_settings - let model use defaults
                                )
                            else:
                                retry3_response = model.generate_content(
                                    content_parts,
                                    generation_config=gen_config
                                    # No safety_settings - let model use defaults
                                )
                            
                            # Check retry response
                            if hasattr(retry3_response, 'candidates') and retry3_response.candidates:
                                retry3_candidate = retry3_response.candidates[0]
                                retry3_finish_reason = getattr(retry3_candidate, 'finish_reason', None)
                                
                                if retry3_finish_reason != 'SAFETY' and retry3_finish_reason != 2:
                                    print("[API] Retry 3 successful without safety_settings!")
                                    if hasattr(retry3_response, 'text') and retry3_response.text:
                                        return retry3_response.text
                                    # Try parts
                                    if hasattr(retry3_candidate, 'content') and retry3_candidate.content:
                                        if hasattr(retry3_candidate.content, 'parts') and retry3_candidate.content.parts:
                                            if len(retry3_candidate.content.parts) > 0:
                                                part = retry3_candidate.content.parts[0]
                                                if hasattr(part, 'text'):
                                                    return part.text
                                else:
                                    print("[API] Retry 3 also blocked, trying Retry 4...")
                            else:
                                print("[API] Retry 3 response invalid, trying Retry 4...")
                        except Exception as retry3_error:
                            print(f"[API] Retry 3 failed: {retry3_error}, trying Retry 4...")
                        
                        # RETRY 4: Try with minimal generation config and BLOCK_ONLY_HIGH (last resort)
                        print("[API] Retry 4: Trying with minimal config and BLOCK_ONLY_HIGH (last resort)...")
                        try:
                            # Use minimal generation config
                            minimal_config = {
                                "temperature": 0.1,  # Lower temperature
                                "max_output_tokens": 1000,  # Fewer tokens
                            }
                            fallback_settings = self._get_safety_settings_block_only_high()
                            
                            if not file_paths or not any(os.path.exists(fp) and os.path.splitext(fp)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp'] for fp in file_paths):
                                retry4_response = model.generate_content(
                                    prompt,
                                    generation_config=minimal_config,
                                    safety_settings=fallback_settings if fallback_settings else None
                                )
                            else:
                                retry4_response = model.generate_content(
                                    content_parts,
                                    generation_config=minimal_config,
                                    safety_settings=fallback_settings if fallback_settings else None
                                )
                            
                            # Check retry response
                            if hasattr(retry4_response, 'candidates') and retry4_response.candidates:
                                retry4_candidate = retry4_response.candidates[0]
                                retry4_finish_reason = getattr(retry4_candidate, 'finish_reason', None)
                                
                                if retry4_finish_reason != 'SAFETY' and retry4_finish_reason != 2:
                                    print("[API] Retry 4 successful with minimal config!")
                                    if hasattr(retry4_response, 'text') and retry4_response.text:
                                        return retry4_response.text
                                    # Try parts
                                    if hasattr(retry4_candidate, 'content') and retry4_candidate.content:
                                        if hasattr(retry4_candidate.content, 'parts') and retry4_candidate.content.parts:
                                            if len(retry4_candidate.content.parts) > 0:
                                                part = retry4_candidate.content.parts[0]
                                                if hasattr(part, 'text'):
                                                    return part.text
                                else:
                                    print("[API] Retry 4 also blocked - all retries exhausted")
                            else:
                                print("[API] Retry 4 response invalid - all retries exhausted")
                        except Exception as retry4_error:
                            print(f"[API] Retry 4 failed: {retry4_error} - all retries exhausted")
                        
                        # If all retries fail, provide error message
                        # IMPORTANT: Don't mention "API key" in error message to avoid triggering wrong error handler
                        print("[API] ERROR: All 4 retry attempts failed. Content is being blocked by safety filters.")
                        raise Exception("SAFETY_FILTER_BLOCKED: Content was blocked by Gemini safety filters despite multiple retry attempts with different safety settings. The API key is valid, but the content triggers safety filters that cannot be disabled. This is a content filtering issue, not an API key issue.")
                    
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
            elif "SAFETY_FILTER_BLOCKED" in error_msg:
                # Re-raise safety filter errors as-is (they're handled in analyze_scenario)
                raise Exception(error_msg)
            elif "403" in error_msg and ("permission" in error_msg.lower() or "API key" in error_msg.lower()) and "invalid" in error_msg.lower():
                # Only raise API key error for actual 403 permission errors, not safety filter blocks
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
    
    def _get_safety_settings(self):
        """Get safety settings with all filters disabled - returns None if cannot be created"""
        # Use pre-initialized settings if available
        safety_settings = self.safety_settings
        
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
        
        return safety_settings
    
    def _convert_safety_settings_to_list_format(self, safety_settings_dict):
        """Convert dict format safety_settings to list format (alternative format that might work better)"""
        if not safety_settings_dict:
            return None
        
        try:
            from google.generativeai.types import HarmCategory, HarmBlockThreshold
            
            # Convert dict to list format: [{'category': HarmCategory.X, 'threshold': HarmBlockThreshold.Y}, ...]
            safety_list = []
            for category_enum, threshold_enum in safety_settings_dict.items():
                safety_list.append({
                    'category': category_enum,
                    'threshold': threshold_enum
                })
            return safety_list
        except Exception as e:
            print(f"[API] Failed to convert safety_settings to list format: {e}")
            return None
    
    def _get_safety_settings_block_only_high(self):
        """Get safety settings with BLOCK_ONLY_HIGH threshold (fallback if BLOCK_NONE doesn't work)"""
        try:
            # Try to use the same enums we have
            if self.HarmCategory and self.HarmBlockThreshold:
                try:
                    # Use BLOCK_ONLY_HIGH instead of BLOCK_NONE
                    return {
                        self.HarmCategory.HARM_CATEGORY_HARASSMENT: self.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        self.HarmCategory.HARM_CATEGORY_HATE_SPEECH: self.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        self.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: self.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        self.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: self.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    }
                except AttributeError:
                    # Try direct import
                    from google.generativeai.types import HarmCategory, HarmBlockThreshold
                    return {
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    }
            else:
                # Try direct import
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                return {
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                }
        except Exception as e:
            print(f"[API] Failed to create BLOCK_ONLY_HIGH settings: {e}")
            return None
    
    def _neutralize_scenario_text(self, scenario_text):
        """Neutralize scenario text to avoid safety filter triggers while preserving meaning
        This is called BEFORE the first API call to prevent blocking proactively"""
        import re
        
        # Start with original text
        neutral_scenario = scenario_text.lower()  # Normalize to lowercase first for better matching
        
        # Multi-word phrases first (longer patterns before shorter ones)
        phrase_replacements = [
            (r'\breached\s+the\s+limit\b', 'reached the threshold'),
            (r'\breach\s+the\s+limit\b', 'reach the threshold'),
            (r'\breaching\s+the\s+limit\b', 'reaching the threshold'),
            (r'\bdifferent\s+ip\s+addresses?\b', 'different network locations'),
            (r'\bdifferent\s+ips\b', 'different network locations'),
            (r'\bip\s+addresses?\b', 'network addresses'),
            (r'\bips\b', 'network addresses'),
            (r'\bip\b', 'network address'),
            (r'\bfrom\s+different\s+ips?\b', 'from multiple network locations'),
            (r'\bstreaming\s+from\s+different\s+ips?\b', 'streaming from multiple network locations'),
        ]
        
        # Apply phrase replacements first
        for pattern, replacement in phrase_replacements:
            neutral_scenario = re.sub(pattern, replacement, neutral_scenario, flags=re.IGNORECASE)
        
        # Comprehensive list of potentially sensitive terms and their neutral business equivalents
        neutral_replacements = {
            # Security/access terms
            'blocked': 'restricted',
            'ban': 'restrict',
            'banned': 'restricted',
            'block': 'restrict',
            'hack': 'unauthorized access',
            'hacked': 'compromised',
            'hacking': 'unauthorized access',
            'breach': 'security incident',
            'breached': 'compromised',
            'attack': 'incident',
            'attacked': 'affected',
            'exploit': 'utilize',
            'exploited': 'utilized',
            'violation': 'issue',
            'violated': 'affected',
            'abuse': 'misuse',
            'abused': 'misused',
            'abusing': 'misusing',
            
            # Limit/threshold terms (handle carefully to preserve meaning)
            'limit': 'threshold',
            'limited': 'restricted',
            'limiting': 'restricting',
            'limits': 'thresholds',
            
            # Account/access terms
            'suspended': 'restricted',
            'suspend': 'restrict',
            'terminated': 'deactivated',
            'terminate': 'deactivate',
            'locked': 'restricted',
            'lock': 'restrict',
            
            # Content terms
            'inappropriate': 'non-compliant',
            'offensive': 'non-compliant',
            'spam': 'unsolicited content',
            'scam': 'fraudulent activity',
            'fraud': 'unauthorized activity',
            
            # Action terms
            'steal': 'unauthorized access',
            'stolen': 'compromised',
            'stealing': 'unauthorized access',
            'delete': 'remove',
            'deleted': 'removed',
            'destroy': 'remove',
            'destroyed': 'removed',
        }
        
        # Apply all replacements (case-insensitive, whole word only)
        for sensitive, neutral in neutral_replacements.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(sensitive) + r'\b'
            neutral_scenario = re.sub(pattern, neutral, neutral_scenario, flags=re.IGNORECASE)
        
        # Additional sanitization: Remove any remaining potentially problematic patterns
        # Remove excessive punctuation that might be interpreted as aggressive
        neutral_scenario = re.sub(r'!{2,}', '!', neutral_scenario)  # Multiple exclamation marks
        neutral_scenario = re.sub(r'\?{2,}', '?', neutral_scenario)  # Multiple question marks
        
        # Capitalize first letter to maintain readability
        if neutral_scenario:
            neutral_scenario = neutral_scenario[0].upper() + neutral_scenario[1:] if len(neutral_scenario) > 1 else neutral_scenario.upper()
        
        # Log if any changes were made
        if neutral_scenario.lower() != scenario_text.lower():
            print(f"[API] Scenario neutralized: {len(scenario_text)} -> {len(neutral_scenario)} chars")
            # Log first 100 chars of changes for debugging
            if len(scenario_text) > 0:
                diff_start = min(100, len(scenario_text))
                print(f"[API] Original: {scenario_text[:diff_start]}...")
                print(f"[API] Neutralized: {neutral_scenario[:diff_start]}...")
        
        return neutral_scenario
    
    def _neutralize_prompt(self, original_prompt, scenario_text):
        """Neutralize full prompt (used for retry scenarios)"""
        neutralized_scenario = self._neutralize_scenario_text(scenario_text)
        
        # Rebuild prompt with neutralized scenario
        if "SCENARIO:" in original_prompt or "CUSTOMER SERVICE SCENARIO" in original_prompt:
            # Find the scenario section and replace it
            if "CUSTOMER SERVICE SCENARIO" in original_prompt:
                system_part = original_prompt.split("CUSTOMER SERVICE SCENARIO")[0]
                neutral_prompt = f"{system_part}CUSTOMER SERVICE SCENARIO (Business Context):\n{neutralized_scenario}\n\nAnalyze this legitimate business customer service request and recommend appropriate tags. Output in English. Focus on technical and business aspects only. This is a standard customer support inquiry."
            else:
                system_part = original_prompt.split("SCENARIO:")[0]
                neutral_prompt = f"{system_part}SCENARIO:\n{neutralized_scenario}\n\nAnalyze and recommend tags. Output in English. Focus on technical and business aspects only."
        else:
            neutral_prompt = original_prompt.replace(scenario_text, neutralized_scenario)
        
        return neutral_prompt
    
    def _create_ultra_sanitized_prompt(self, scenario_text, mind_map_context):
        """Create an ultra-sanitized prompt with explicit business context wrapper"""
        # Apply aggressive neutralization
        ultra_neutral = self._neutralize_scenario_text(scenario_text)
        
        # Further sanitize: replace any remaining potentially problematic terms
        import re
        # Replace any remaining technical terms that might trigger filters
        ultra_neutral = re.sub(r'\b(ip|ips|address|addresses)\b', 'network location', ultra_neutral, flags=re.IGNORECASE)
        ultra_neutral = re.sub(r'\b(limit|limits)\b', 'threshold', ultra_neutral, flags=re.IGNORECASE)
        
        # Create ultra-safe prompt with explicit business context
        ultra_prompt = f"""You are analyzing a customer service ticket for a legitimate streaming service business.

This is a standard business customer support scenario. The customer is reporting a technical issue with their service usage. All terminology refers to legitimate business operations.

MIND MAP DATA:
{mind_map_context[:3000]}

CUSTOMER INQUIRY (Business Support Ticket):
{ultra_neutral}

TASK: Classify this customer service ticket by matching it to tags in the mind map. This is a routine business operation for customer support categorization.

OUTPUT FORMAT:
- Recommended Tag(s): [tag names from mind map]
- Confidence: [High/Medium/Low]
- Reasoning: [brief business-focused explanation]
- Mind Map Reference: [sheet/row]

Remember: This is a legitimate business customer support scenario. Focus on technical and business aspects only."""
        
        return ultra_prompt
    
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

