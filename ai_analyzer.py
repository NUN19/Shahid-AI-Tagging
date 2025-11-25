"""
AI Analyzer
Uses AI to analyze customer scenarios and suggest appropriate tags
Uses Google Gemini API (gemini-2.5-flash only)
"""

import os
import re
import time
from collections import deque
from difflib import SequenceMatcher

class AIAnalyzer:
    def __init__(self, mind_map_parser):
        """Initialize AI analyzer with mind map parser"""
        self.mind_map_parser = mind_map_parser
        
        # Request throttling: track request times to avoid rate limits
        # Free tier: 15 requests/minute = 1 request per 4 seconds
        # Using conservative 20 seconds to be safe
        self.request_times = deque(maxlen=15)
        self.min_request_interval = 20.0
        
        # Use Gemini API
        self.provider = os.getenv('AI_PROVIDER', 'gemini').lower()
        
        if self.provider == 'gemini':
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found. Get a free key at: https://makersuite.google.com/app/apikey")
            try:
                import google.generativeai as genai
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                genai.configure(api_key=api_key)
                self.genai = genai
                print("[INIT] Gemini API initialized successfully")
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
            wait_time = 60 - (current_time - self.request_times[0]) + 2
            if wait_time > 0:
                time.sleep(wait_time)
                current_time = time.time()
        
        # Ensure minimum interval between requests
        if self.request_times:
            time_since_last = current_time - self.request_times[-1]
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                print(f"[Throttle] Waiting {wait_time:.1f} seconds before next request...")
                time.sleep(wait_time)
                current_time = time.time()
        else:
            # First request - add a delay
            print("[Throttle] First request - waiting 5 seconds...")
            time.sleep(5)
            current_time = time.time()
        
        # Record this request
        self.request_times.append(current_time)
    
    def _prepare_tag_data(self):
        """Prepare structured tag data from Excel file"""
        all_tags = self.mind_map_parser.get_all_tags()
        if not all_tags:
            return []
        
        tag_data_list = []
        for tag_key, tag_info in all_tags.items():
            if 'tag_name' in tag_info:
                tag_data_list.append({
                    'tag_id': tag_info.get('tag_id', ''),
                    'tag_name': tag_info.get('tag_name', ''),
                    'tag_logic': tag_info.get('logic', ''),
                    'customer_scenarios': tag_info.get('customer_scenarios', ''),
                    'sheet': tag_info.get('sheet', '')
                })
        
        return tag_data_list
    
    def _extract_key_concepts(self, text):
        """Extract key concepts from scenario text using comprehensive terms from Excel file"""
        if not text:
            return []
        
        # Comprehensive terms extracted from "List of tags 2025.xlsx" Tag_Logic and Customer_Scenarios
        comprehensive_terms = [
            # Subscription & Payment
            'subscribe', 'subscribed', 'subscription', 'payment', 'pay', 'paid', 'card', 'itunes', 
            'voucher', 'promo', 'promotion', 'offer', 'offers', 'discount', 'lto', 'long term', 
            'trial', 'free', 'billing', 'invoice', 'charge', 'deduct', 'deduction', 'refund',
            'cancel', 'cancelled', 'cancellation', 'renew', 'renewal', 'expire', 'expired', 'expiry',
            
            # Content & Streaming
            'watch', 'watching', 'stream', 'streaming', 'video', 'content', 'contents', 'quality', 
            'resolution', 'buffering', 'loading', 'play', 'playing', 'pause', 'download', 'upload',
            'episodes', 'shows', 'shorts', 'sports',
            
            # Account & Profile
            'account', 'accounts', 'profile', 'profiles', 'login', 'logout', 'logged', 'logging',
            'password', 'email', 'phone', 'number', 'username', 'user', 'verify', 'verification', 
            'otp', 'active', 'inactive', 'suspended', 'blocked', 'restricted',
            
            # Device & Network
            'device', 'devices', 'link', 'linked', 'unlink', 'manage', 'management', 'managing',
            'ip', 'address', 'addresses', 'network', 'connection', 'internet', 'wifi', 'mobile',
            'app', 'application', 'website', 'page', 'screen',
            
            # Issues & Problems
            'error', 'issue', 'problem', 'not working', 'failed', 'failure', 'cannot', 'unable',
            'facing', 'faced', 'stuck', 'attempts', 'trying', 'still',
            
            # Services & Features
            'vip', 'premium', 'ads', 'advertisement', 'concurrent', 'session', 'sessions', 
            'limit', 'limits', 'maximum', 'exceed', 'exceeded', 'access', 'accessible', 
            'available', 'unavailable', 'offline',
            
            # Actions & Operations
            'add', 'remove', 'change', 'update', 'updated', 'modify', 'reset', 'retrieve', 
            'recover', 'restore', 'locate', 'find', 'found', 'gather', 'check', 'checked', 
            'checking', 'educate', 'educated', 'educating', 'guide', 'guided', 'guidance',
            'assist', 'assistance', 'help', 'resolve', 'resolved',
            
            # Business Systems
            'evergent', 'gigya', 'salesforce', 'clevertap', 'gobx', 'shahid', 'mbc', 
            'checkpoint', 'checkpoints', 'airtable', 'slack',
            
            # Customer Service
            'customer', 'agent', 'contact', 'inquire', 'inquiring', 'asking', 'asks', 
            'request', 'requested', 'escalate', 'escalated', 'ticket', 'team', 'leader',
            
            # Status & Information
            'status', 'details', 'information', 'code', 'date', 'end', 'last', 'first',
            'previous', 'previously', 'current', 'package', 'plan', 'price', 'country',
            'channel', 'method', 'case', 'cases', 'specific', 'related', 'registered',
            'purchased', 'redeem', 'refer', 'referring', 'eligible', 'activated',
            
            # Technical Terms
            'technical', 'feature', 'rights', 'supported', 'according', 'ensure', 'must',
            'required', 'possible', 'correct', 'different', 'another', 'any', 'all',
            'someone', 'using', 'used', 'getting', 'keep', 'retain', 'follow', 'provide',
            'identified', 'list', 'name', 'net', 'order', 'partner', 'parent', 'questions',
            'received', 'receiving', 'share', 'side', 'steps', 'table', 'tag', 'them',
            'then', 'through', 'via', 'whenever', 'whether', 'why', 'working', 'yearly',
            'yet', 'already', 'being', 'had', 'into', 'message', 'name', 'them', 'then',
        ]
        
        text_lower = text.lower()
        found_concepts = []
        
        # Check for important multi-word phrases
        multi_word_terms = [
            'not working', 'long term', 'concurrent session', 'concurrent sessions', 
            'linked device', 'linked devices', 'payment method', 'subscription plan',
            'account management', 'device management', 'contact information', 
            'use this tag', 'when customer', 'if customer', 'check if', 'gather all',
            'maximum concurrent', 'exceeded the limit', 'facing an issue', 
            'not able to', 'unable to', 'cannot access', 'cannot watch',
            'cannot stream', 'cannot play', 'cannot download', 'cannot upload', 
            'cannot login', 'cannot logout', 'cannot change', 'cannot update', 
            'cannot modify', 'cannot remove', 'cannot add', 'cannot link', 
            'cannot unlink', 'cannot cancel', 'cannot refund',
            'error while', 'issue while', 'problem while', 'failed to', 
            'stuck on', 'loading for', 'buffering while',
            'ip address', 'email address', 'phone number', 'contact number', 
            'verification code', 'otp code', 'password reset', 'account recovery',
            'session limit', 'device limit', 'premium feature', 'vip feature',
        ]
        
        # Check multi-word terms first
        for term in multi_word_terms:
            if term in text_lower:
                found_concepts.append(term)
        
        # Then check single-word terms
        for term in comprehensive_terms:
            if term not in found_concepts:
                pattern = r'\b' + re.escape(term) + r'\b'
                if re.search(pattern, text_lower):
                    found_concepts.append(term)
        
        return found_concepts
    
    def _normalize_tag_id(self, tag_id):
        """Normalize tag ID to standard format (T + 4 digits, e.g., T0009)"""
        if not tag_id:
            return None
        
        cleaned = re.sub(r'[^\w]', '', str(tag_id).upper())
        
        if cleaned.startswith('T'):
            number_part = cleaned[1:]
        else:
            number_part = cleaned
        
        try:
            number = int(number_part) if number_part else 0
            return f"T{number:04d}"
        except ValueError:
            return f"T{number_part.zfill(4)}" if number_part else None
    
    def _get_tag_by_id(self, tag_id):
        """Get tag name by tag ID"""
        all_tags = self.mind_map_parser.get_all_tags()
        if not all_tags:
            return None
        
        tag_id_normalized = self._normalize_tag_id(tag_id)
        if not tag_id_normalized:
            return None
        
        for tag_data in all_tags.values():
            if 'tag_id' in tag_data:
                tag_id_from_map = str(tag_data['tag_id']).strip()
                tag_id_from_map_normalized = self._normalize_tag_id(tag_id_from_map)
                
                if tag_id_normalized == tag_id_from_map_normalized:
                    return tag_data.get('tag_name')
        
        return None
    
    def _extract_tag_ids_from_text(self, text):
        """Extract tag IDs from text"""
        patterns = [
            r'\bT\d{4}\b',
            r'\bT\d{1,3}\b',
            r'\btag\s+(?:id|#)?\s*[:\-]?\s*(T\d{1,4})',
            r'(?:tag|tags?)\s+(T\d{1,4})',
            r'\[(T\d{1,4})\]',
            r'\(T\d{1,4}\)',
        ]
        
        found_ids = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                tag_id = match if isinstance(match, str) else match[0] if match else None
                if tag_id:
                    normalized_id = self._normalize_tag_id(tag_id)
                    if normalized_id and normalized_id not in found_ids:
                        found_ids.append(normalized_id)
        
        return found_ids
    
    def _normalize_tag_name(self, tag_name):
        """Normalize tag name for matching"""
        if not tag_name:
            return ""
        normalized = ' '.join(tag_name.split())
        normalized = re.sub(r'^(tag|tags?):\s*', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'\s*\(.*?\)\s*$', '', normalized)
        return normalized.strip()
    
    def _fuzzy_match_tag(self, extracted_tag, available_tags, threshold=0.85):
        """Find best matching tag using fuzzy string matching"""
        if not extracted_tag or not available_tags:
            return None, 0.0
        
        normalized_extracted = self._normalize_tag_name(extracted_tag).lower()
        best_match = None
        best_score = 0.0
        
        for tag_name in available_tags:
            normalized_tag = self._normalize_tag_name(tag_name).lower()
            similarity = SequenceMatcher(None, normalized_extracted, normalized_tag).ratio()
            
            if normalized_extracted == normalized_tag:
                similarity = 1.0
            
            if normalized_extracted in normalized_tag or normalized_tag in normalized_extracted:
                similarity = max(similarity, 0.9)
            
            if similarity > best_score:
                best_score = similarity
                best_match = tag_name
        
        if best_score >= threshold:
            return best_match, best_score
        return None, best_score
    
    def _extract_tag_name_from_response(self, response_text):
        """Extract tag name from AI response"""
        if not response_text:
            return None
        
        all_tags = self.mind_map_parser.get_all_tags()
        if not all_tags:
            return None
        
        available_tag_names = [tag['tag_name'] for tag in all_tags.values() if 'tag_name' in tag]
        
        # Pattern 1: "Tag: [tag name]"
        pattern1 = r'(?:^|\n)\s*Tag\s*:\s*([^\n]+?)(?:\n|$)'
        matches1 = re.findall(pattern1, response_text, re.IGNORECASE | re.MULTILINE)
        for match in matches1:
            tag_name = match.strip()
            if tag_name in available_tag_names:
                return tag_name
            fuzzy_match, score = self._fuzzy_match_tag(tag_name, available_tag_names, threshold=0.90)
            if fuzzy_match:
                return fuzzy_match
        
        # Pattern 2: Extract tag IDs
        tag_ids = self._extract_tag_ids_from_text(response_text)
        for tag_id in tag_ids:
            tag_name = self._get_tag_by_id(tag_id)
            if tag_name:
                return tag_name
        
        # Pattern 3: Quoted tag names
        pattern3 = r'"([^"]{15,})"'
        matches3 = re.findall(pattern3, response_text)
        for match in matches3:
            tag_name = match.strip()
            if tag_name in available_tag_names:
                return tag_name
            fuzzy_match, score = self._fuzzy_match_tag(tag_name, available_tag_names, threshold=0.90)
            if fuzzy_match:
                return fuzzy_match
        
        # Pattern 4: Direct match
        response_lower = response_text.lower()
        for tag_name in available_tag_names:
            normalized_tag = self._normalize_tag_name(tag_name).lower()
            if normalized_tag in response_lower:
                if len(normalized_tag.split()) >= 2:
                    return tag_name
        
        return None
    
    def _call_gemini(self, prompt, file_paths=None, max_retries=3):
        """Call Google Gemini API with retry logic"""
        # Throttle request
        self._throttle_request()
        
        model_name = "gemini-2.5-flash"
        
        # Prepare content parts
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
        
        # Generation config
        gen_config = {
            "temperature": 0.3,
            "max_output_tokens": 1500,
        }
        
        # Try to create model
        try:
            model = self.genai.GenerativeModel(model_name)
            print(f"[API] Using model: {model_name}")
        except Exception as model_error:
            error_msg = str(model_error)
            if "404" in error_msg or "not found" in error_msg.lower():
                raise Exception(f"Model '{model_name}' not available. Error: {error_msg}")
            raise
        
        # Retry logic
        last_error = None
        for attempt in range(max_retries):
            try:
                print(f"[API] Attempt {attempt + 1}/{max_retries}")
                
                # Safety settings - Block nothing to avoid false positives
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
                # Explicitly list supported categories to avoid 400 errors with unsupported ones
                # The API only accepts specific categories
                supported_categories = [
                    HarmCategory.HARM_CATEGORY_HARASSMENT,
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                ]
                
                # Add Civic Integrity if available (it appears in some API versions)
                if hasattr(HarmCategory, 'HARM_CATEGORY_CIVIC_INTEGRITY'):
                    supported_categories.append(HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY)
                
                safety_settings = {
                    category: HarmBlockThreshold.BLOCK_NONE
                    for category in supported_categories
                }

                # Call API - NO safety_settings, let API use defaults
                response = model.generate_content(
                    content_parts,
                    generation_config=gen_config,
                    safety_settings=safety_settings
                )
                
                # Check response
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    finish_reason = getattr(candidate, 'finish_reason', None)
                    
                    print(f"[API] Response finish_reason: {finish_reason}")
                    
                    # Check if blocked
                    finish_reason_str = str(finish_reason) if finish_reason is not None else None
                    finish_reason_int = None
                    try:
                        if finish_reason is not None:
                            if isinstance(finish_reason, int):
                                finish_reason_int = finish_reason
                            elif isinstance(finish_reason, str) and finish_reason.isdigit():
                                finish_reason_int = int(finish_reason)
                    except:
                        pass
                    
                    is_safety_block = (
                        finish_reason == 'SAFETY' or 
                        finish_reason == 2 or 
                        finish_reason_str == 'SAFETY' or
                        finish_reason_str == '2' or
                        finish_reason_int == 2
                    )
                    
                    if is_safety_block:
                        # Get detailed blocking information
                        blocking_info = []
                        if hasattr(candidate, 'safety_ratings'):
                            for rating in candidate.safety_ratings:
                                category = getattr(rating, 'category', 'unknown')
                                probability = getattr(rating, 'probability', 'unknown')
                                threshold = getattr(rating, 'threshold', 'unknown')
                                blocking_info.append(f"Category: {category}, Probability: {probability}, Threshold: {threshold}")
                        
                        error_details = f"Content was blocked by safety filters. Finish reason: {finish_reason}"
                        if blocking_info:
                            error_details += f"\nSafety ratings: {'; '.join(blocking_info)}"
                        
                        last_error = Exception(error_details)
                        
                        if attempt < max_retries - 1:
                            print(f"[API] Blocked, retrying... ({attempt + 1}/{max_retries})")
                            time.sleep(2)  # Wait before retry
                            continue
                        else:
                            raise last_error
                    
                    # Try to extract text
                    text = None
                    try:
                        if hasattr(response, 'text') and response.text:
                            text = response.text.strip()
                    except:
                        pass
                    
                    if not text:
                        try:
                            if hasattr(candidate, 'content') and candidate.content:
                                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                    if len(candidate.content.parts) > 0:
                                        part = candidate.content.parts[0]
                                        if hasattr(part, 'text') and part.text:
                                            text = part.text.strip()
                        except:
                            pass
                    
                    if text:
                        print(f"[API] Successfully extracted response ({len(text)} chars)")
                        return text
                    else:
                        raise Exception(f"Empty response from API. Finish reason: {finish_reason}")
                
                else:
                    raise Exception("No candidates in response")
                    
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # Check if it's a blocking error
                if 'blocked' in error_msg.lower() or 'safety' in error_msg.lower() or 'SAFETY' in error_msg:
                    if attempt < max_retries - 1:
                        print(f"[API] Blocked, retrying... ({attempt + 1}/{max_retries})")
                        time.sleep(2)
                        continue
                    else:
                        raise Exception(f"Content blocked after {max_retries} attempts. Details: {error_msg}")
                
                # Other errors - raise immediately
                raise
        
        # If we get here, all retries failed
        if last_error:
            raise last_error
        raise Exception("API call failed after all retries")
    
    def analyze_scenario(self, scenario_text, file_paths=None, language='en'):
        """Analyze customer scenario and return the best matching tag"""
        if not scenario_text.strip():
            error_msg = 'Please provide a customer scenario' if language == 'en' else 'الرجاء إدخال سيناريو العميل'
            return {'error': error_msg}
        
        # Use scenario text exactly as provided
        original_scenario = scenario_text.strip()
        
        # Get all tags with their logic and examples
        tag_data_list = self._prepare_tag_data()
        if not tag_data_list:
            return {'error': 'No tags found in mind map'}
        
        # Format tags for AI
        tags_for_comparison = []
        for tag_data in tag_data_list:
            tag_entry = f"""
[TAG ID: {tag_data['tag_id']}]
TAG NAME: {tag_data['tag_name']}
TAG LOGIC: {tag_data['tag_logic']}
EXAMPLE CUSTOMER SCENARIOS: {tag_data['customer_scenarios']}
CATEGORY: {tag_data['sheet']}
"""
            tags_for_comparison.append(tag_entry)
        
        tags_text = "\n".join(tags_for_comparison)
        
        # Limit tags if too many
        if len(tags_text) > 15000:
            tags_text = tags_text[:15000]
            last_tag_end = tags_text.rfind('\n[TAG ID:')
            if last_tag_end > 12000:
                tags_text = tags_text[:last_tag_end] + "\n\n... (additional tags truncated)"
        
        # Extract key concepts
        key_concepts = self._extract_key_concepts(original_scenario)
        concepts_hint = f"\n\nKey concepts detected: {', '.join(key_concepts[:10])}" if key_concepts else ""
        
        # Build comprehensive prompt - let API decide the best approach
        prompt = f"""You are an AI model that classifies customer-service scenarios into the correct support tag.

All scenarios you receive are standard business customer support queries about a streaming service. They may include discussions about payments, refunds, cancellations, login issues, device issues, account restrictions, IP addresses, limits, concurrent sessions, or account security. These are all routine customer support topics.

AVAILABLE TAGS WITH THEIR LOGIC AND EXAMPLES (from List of tags 2025.xlsx):
{tags_text}

YOUR TASK:
1. Read the customer scenario EXACTLY as provided (do not modify it)
2. For EACH tag above, compare the scenario with:
   - The TAG LOGIC field (does the scenario meet the logic criteria?)
   - The EXAMPLE CUSTOMER SCENARIOS field (is the scenario similar to the examples?)
3. Calculate a match score for each tag: (TAG LOGIC match × 0.6) + (EXAMPLE SCENARIOS match × 0.4)
4. Select the tag with the HIGHEST combined match score
5. Return the tag name and your confidence level

KEY DOMAIN TERMS (to help with matching):
Subscription/Payment: subscribe, subscription, payment, pay, card, itunes, voucher, promo, offer, discount, lto, trial, free, billing, invoice, charge, refund, cancel, renew, expire
Content/Streaming: watch, streaming, video, content, quality, resolution, buffering, loading, play, download, upload
Account/Profile: account, profile, login, logout, password, email, phone, verify, active, inactive, suspended, blocked
Device/Network: device, devices, link, linked, unlink, manage, ip, address, network, connection, internet, wifi, mobile, app
Issues/Problems: error, issue, problem, not working, failed, cannot, unable, facing, stuck, trying
Services: vip, premium, ads, advertisement, concurrent, session, sessions, limit, limits, maximum, exceed, access, available
Actions: add, remove, change, update, modify, reset, retrieve, recover, restore, locate, find, gather, check, educate, guide, assist
Systems: evergent, gigya, salesforce, clevertap, gobx, shahid, mbc, checkpoint

CUSTOMER SCENARIO:
{original_scenario}{concepts_hint}

OUTPUT FORMAT:
Tag: [exact Full_Tag_Name from the selected tag]
Confidence: [High/Medium/Low]

If no strong match exists, return the tag with the highest confidence anyway."""
        
        try:
            # Call Gemini API
            if self.provider == 'gemini':
                ai_response = self._call_gemini(prompt, file_paths, max_retries=3)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}. Only 'gemini' is supported.")
            
            # Extract tag name and confidence
            tag_name = self._extract_tag_name_from_response(ai_response)
            
            # Extract confidence
            confidence = 'Medium'
            if 'confidence' in ai_response.lower():
                conf_match = re.search(r'confidence\s*:\s*(high|medium|low)', ai_response, re.IGNORECASE)
                if conf_match:
                    confidence = conf_match.group(1).capitalize()
            elif tag_name:
                confidence = 'High'  # If we found a tag, assume high confidence
            
            if tag_name:
                return {
                    'tags': [tag_name],
                    'confidence': confidence,
                    'reasoning': '',
                    'mind_map_reference': '',
                    'full_response': ai_response
                }
            else:
                # Try to find any tag mentioned in response (fallback)
                all_tags = self.mind_map_parser.get_all_tags()
                available_tag_names = [tag['tag_name'] for tag in all_tags.values() if 'tag_name' in tag]
                
                # Look for any tag name in response
                response_lower = ai_response.lower()
                for tag_name in available_tag_names:
                    normalized_tag = self._normalize_tag_name(tag_name).lower()
                    if normalized_tag in response_lower and len(normalized_tag.split()) >= 2:
                        return {
                            'tags': [tag_name],
                            'confidence': 'Low',  # Low confidence since we had to search
                            'reasoning': '',
                            'mind_map_reference': '',
                            'full_response': ai_response
                        }
                
                return {
                    'error': 'No tag found',
                    'details': 'Could not extract a valid tag name from AI response',
                    'full_response': ai_response
                }
            
        except Exception as e:
            error_str = str(e)
            
            # Provide detailed error information
            if 'blocked' in error_str.lower() or 'safety' in error_str.lower():
                return {
                    'error': 'Content Blocked',
                    'details': error_str,
                    'solution': 'The content was blocked by safety filters. Check the details above for specific blocking reasons.',
                    'full_error': error_str
                }
            elif ('API key' in error_str and 'invalid' in error_str.lower()) or ('403' in error_str and 'permission' in error_str.lower()):
                return {
                    'error': 'Invalid Gemini API Key',
                    'details': 'The Gemini API key is invalid or has insufficient permissions.',
                    'solution': 'Please check your GEMINI_API_KEY in the .env file.',
                    'full_error': error_str
                }
            elif 'rate limit' in error_str.lower() or 'quota' in error_str.lower() or '429' in error_str:
                return {
                    'error': 'Gemini API Rate Limit Exceeded',
                    'details': f'Your API key has exceeded the rate limit.',
                    'solution': f'Please wait 2-3 minutes before trying again.',
                    'full_error': error_str
                }
            elif 'model not available' in error_str.lower() or '404' in error_str:
                return {
                    'error': 'Gemini Model Not Available',
                    'details': 'The requested Gemini model is not available.',
                    'solution': 'Please check your API key has access to gemini-2.5-flash.',
                    'full_error': error_str
                }
            else:
                return {
                    'error': 'AI Analysis Failed',
                    'details': error_str,
                    'full_error': error_str
                }
