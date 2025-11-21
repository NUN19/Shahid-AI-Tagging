# Shareable App Implementation Plan

## Goal
Transform the app into a shareable web application where:
- Users visit a link (cloud-hosted or ngrok tunnel)
- Users upload their own mind map Excel file
- App works with the uploaded mind map per session
- No hardcoded mind map file required

## Architecture Changes

### Current State
- Mind map is hardcoded: `'Updated Mind Map.xlsx'`
- Loaded at app startup (line 22 in app.py)
- Single global instance

### New State
- Mind map uploaded per user session
- Stored temporarily in session storage
- Each user can have their own mind map
- Mind map persists for the session duration

## Implementation Plan

### 1. Session-Based Mind Map Storage

**Changes to `app.py`:**
- Add Flask session support with secret key
- Remove hardcoded mind map initialization
- Store mind map file path in session
- Create session-scoped mind map parser and AI analyzer

**Storage Strategy:**
- Upload mind map to `mind_maps/` folder with session ID
- File name: `mind_map_{session_id}.xlsx`
- Clean up old files periodically (older than 24 hours)

### 2. Setup/Upload Page

**New Route: `/setup`**
- First page users see if no mind map uploaded
- Upload form for Excel file
- Validation (check if it's a valid Excel file)
- Success message and redirect to main app

**New Template: `templates/setup.html`**
- Bilingual (English/Arabic) matching existing UI
- Drag-and-drop file upload
- File validation feedback
- Instructions for Excel format

### 3. API Endpoints

**New: `/api/upload-mindmap` (POST)**
- Accept Excel file upload
- Validate file format
- Save to session-specific location
- Initialize mind map parser
- Return success/error

**New: `/api/check-mindmap` (GET)**
- Check if mind map is loaded for current session
- Return status (loaded/not loaded)

**Modify: `/api/analyze`**
- Check if mind map exists before processing
- Return error if no mind map uploaded

**Modify: `/api/tags`**
- Check if mind map exists before returning tags

### 4. Frontend Changes

**Modify `templates/index.html`:**
- Add JavaScript to check mind map status on load
- Redirect to `/setup` if no mind map loaded
- Show current mind map info (filename, sheets count)
- Option to change/upload new mind map

### 5. Session Management

**Session Configuration:**
- `SECRET_KEY` from environment (or auto-generate)
- Session timeout: 24 hours (or configurable)
- Per-session mind map storage

**Cleanup:**
- Background task to clean old mind map files
- Or cleanup on app startup

### 6. Error Handling

- Handle invalid Excel files gracefully
- Show user-friendly error messages
- Support for corrupted Excel files
- File size limits (e.g., 10MB for mind map)

## File Structure Changes

```
.
├── app.py                    # [MODIFY] Session-based mind map
├── mind_map_parser.py        # [NO CHANGE] Already flexible
├── ai_analyzer.py            # [NO CHANGE] Works with parser
├── templates/
│   ├── index.html            # [MODIFY] Add mind map status check
│   └── setup.html            # [NEW] Mind map upload page
├── mind_maps/                # [EXISTS] Store uploaded mind maps
│   └── mind_map_{session_id}.xlsx
└── requirements.txt          # [NO CHANGE] Flask has sessions built-in
```

## User Flow

### First Visit
1. User visits link → `/setup` page
2. User uploads Excel mind map file
3. File validated and saved
4. Redirected to main app (`/`)
5. App works with uploaded mind map

### Subsequent Requests (Same Session)
1. User visits link → Main app (`/`)
2. Mind map already loaded from session
3. User can analyze scenarios immediately

### New Session
1. User visits link → `/setup` page (if session expired)
2. Upload mind map again

## Deployment Options

### Option A: Cloud Hosting (Permanent Link)
**Platforms:** Render, Heroku, Railway, Fly.io

**Steps:**
1. Push code to GitHub
2. Connect to Render/Heroku
3. Set environment variables:
   - `GEMINI_API_KEY`
   - `SECRET_KEY` (for sessions)
4. Deploy
5. Share permanent link

**Pros:**
- Permanent URL
- 24/7 availability
- No local setup needed

**Cons:**
- Requires cloud account
- Free tiers have limitations

### Option B: Ngrok Tunnel (Temporary Link)
**For:** Quick sharing, testing, temporary access

**Steps:**
1. Run app locally: `python app.py`
2. Start ngrok: `ngrok http 5000`
3. Share ngrok URL
4. Users can access immediately

**Pros:**
- Instant sharing
- No cloud setup
- Free tier available

**Cons:**
- URL changes on restart (unless authtoken)
- Requires your PC to be running
- Temporary solution

## Security Considerations

1. **File Upload Security:**
   - Validate file extensions (.xlsx, .xls only)
   - Check file size limits
   - Scan for malicious content (basic validation)

2. **Session Security:**
   - Use secure session cookies
   - Set appropriate session timeout
   - Clean up old files regularly

3. **Rate Limiting:**
   - Limit mind map uploads per session
   - Prevent abuse of API endpoints

## Testing Checklist

- [ ] Upload valid Excel file → Success
- [ ] Upload invalid file → Error message
- [ ] Upload mind map → Can analyze scenarios
- [ ] No mind map → Redirected to setup
- [ ] Session expires → Prompt to re-upload
- [ ] Multiple users → Each has own mind map
- [ ] File cleanup → Old files removed

## Migration Notes

**For Existing Users:**
- If `Updated Mind Map.xlsx` exists, can auto-load on first run
- Or require upload for consistency
- Document the change in README

## Questions to Consider

1. **Auto-load existing file?**
   - If `Updated Mind Map.xlsx` exists, should we auto-load it?
   - Or always require upload for consistency?

2. **Mind map persistence:**
   - Keep for session only (24 hours)?
   - Or allow "remember this mind map" option?

3. **Multiple mind maps:**
   - Allow switching between multiple uploaded mind maps?
   - Or one per session?

4. **File size limit:**
   - What's the maximum mind map file size? (Recommend: 10MB)

## Next Steps

1. Review this plan
2. Confirm approach and answer questions above
3. Implement changes
4. Test locally
5. Deploy to cloud or set up ngrok
6. Share link with users

---

**Ready to implement?** Let me know if you want any changes to this plan!

