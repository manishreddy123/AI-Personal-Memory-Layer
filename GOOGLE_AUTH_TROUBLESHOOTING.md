# Google Authentication Troubleshooting Guide

## 🚨 Error 403: access_denied

This error occurs when your Google Cloud Console project is not properly configured for OAuth authentication.

## 🔧 Step-by-Step Fix

### 1. **Check Google Cloud Console Setup**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services** → **Credentials**

### 2. **Configure OAuth Consent Screen**

1. Go to **APIs & Services** → **OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace account)
3. Fill in required fields:
   - **App name**: Personal Memory AI
   - **User support email**: Your email
   - **Developer contact information**: Your email
4. **Add scopes**:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar.readonly`
5. **Add test users** (for External apps):
   - Add your own email address
   - Add any other emails you want to test with
6. **Save and continue**

### 3. **Create/Update OAuth 2.0 Credentials**

1. Go to **APIs & Services** → **Credentials**
2. Click **+ CREATE CREDENTIALS** → **OAuth 2.0 Client IDs**
3. Choose **Desktop application**
4. Name it: "Personal Memory AI Desktop"
5. Download the JSON file
6. Rename it to `credentials.json` and place it in your project root

### 4. **Enable Required APIs**

1. Go to **APIs & Services** → **Library**
2. Search and enable:
   - **Gmail API**
   - **Google Calendar API**

### 5. **Update Your Environment**

Make sure your `.env` file has:
```
GOOGLE_CLIENT_SECRET_FILE=credentials.json
```

### 6. **Clear Existing Tokens**

Delete these files if they exist:
- `token.json`
- `token_calendar.json`

## 🔍 Common Issues and Solutions

### Issue 1: "This app isn't verified"
**Solution**: 
- Click "Advanced" → "Go to Personal Memory AI (unsafe)"
- This is normal for personal projects

### Issue 2: "access_denied" with correct setup
**Solution**:
- Ensure your email is added as a test user
- Check that all required APIs are enabled
- Verify OAuth consent screen is properly configured

### Issue 3: "redirect_uri_mismatch"
**Solution**:
- Use Desktop application type (not Web application)
- Don't manually set redirect URIs for desktop apps

## 🧪 Testing the Fix

Run this test script to verify your setup:

```python
# test_google_auth.py
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

def test_gmail_auth():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    print("✅ Gmail authentication successful!")
    return creds

if __name__ == "__main__":
    test_gmail_auth()
```

## 📋 Checklist

- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Test users added (your email)
- [ ] Gmail API enabled
- [ ] Calendar API enabled
- [ ] OAuth 2.0 credentials created (Desktop type)
- [ ] credentials.json downloaded and placed in project root
- [ ] Old token files deleted
- [ ] Environment variable set correctly

## 🆘 Still Having Issues?

If you're still getting errors:

1. **Double-check test users**: Your email MUST be in the test users list
2. **Wait 5-10 minutes**: Changes can take time to propagate
3. **Try incognito mode**: Clear browser cache/cookies
4. **Check quotas**: Ensure you haven't exceeded API quotas

## 🔐 Security Notes

- Keep `credentials.json` secure and don't commit it to version control
- The `token.json` files contain your access tokens - also keep secure
- Consider using service accounts for production deployments
