# Troubleshooting Guide - Registration & Password Reset Issues

## Common Issues and Solutions

### 1. Registration Not Working

#### Symptoms:
- Registration form submits but nothing happens
- Error message appears
- Email verification not received

#### Possible Causes & Solutions:

**A. SMTP Email Configuration Missing**

The most common issue is missing email configuration in your `.env` file.

Check your `backend/.env` file has these settings:

```env
# Email Configuration (Required for registration & password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=PhishGuard AI
```

**For Gmail:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate an "App Password" (not your regular password)
4. Use that app password in `SMTP_PASSWORD`

**B. Backend Not Running**

Make sure your backend server is running:
```bash
cd backend
python run.py
```

Check the console for errors.

**C. CORS Issues**

If you see CORS errors in browser console, check that `frontend` URL is in the CORS origins in `backend/app/main.py`:

```python
origins = [
    "http://localhost:5173",  # Your frontend URL
    "http://localhost:5174",
]
```

**D. Database Connection Issues**

Check your `DATABASE_URL` in `.env` is correct and the database is accessible.

### 2. Password Reset Not Working

#### Symptoms:
- "Email sent" message appears but no email received
- Reset link doesn't work
- Token expired error

#### Solutions:

**A. Check Email Configuration** (same as above)

**B. Check Spam Folder**

Password reset emails might be in spam/junk folder.

**C. Token Expiration**

Reset tokens expire after 1 hour. Request a new one if expired.

**D. Check Backend Logs**

Look at `backend/phishguard.log` for email sending errors:

```bash
tail -f backend/phishguard.log
```

### 3. Debugging Steps

#### Step 1: Check Backend Health

Open browser and go to: `http://localhost:8000/api/health`

Should return: `{"status": "healthy"}`

#### Step 2: Check API Documentation

Go to: `http://localhost:8000/docs`

Try the `/api/auth/register` endpoint manually with test data.

#### Step 3: Check Browser Console

Open browser DevTools (F12) → Console tab

Look for:
- Network errors (red)
- CORS errors
- 400/500 status codes

#### Step 4: Check Backend Logs

```bash
# Windows
type backend\phishguard.log

# Linux/Mac
tail -n 50 backend/phishguard.log
```

Look for:
- "Registration failed"
- "Failed to send verification email"
- SMTP connection errors

### 4. Quick Test

Test if email sending works:

```python
# Create test_email.py in backend folder
import asyncio
from app.services.email_service import email_service

async def test():
    result = await email_service.send_email(
        to_email="your-email@example.com",
        subject="Test Email",
        html_content="<h1>Test</h1><p>If you receive this, email is working!</p>"
    )
    print(f"Email sent: {result}")

asyncio.run(test())
```

Run:
```bash
cd backend
python test_email.py
```

### 5. Alternative: Skip Email Verification (Development Only)

For testing purposes, you can temporarily disable email verification:

**Option A: Manually verify user in database**

```bash
cd backend
python scripts/verify_user.py
```

**Option B: Modify registration to auto-verify** (NOT for production)

In `backend/app/routes/auth.py`, change:
```python
# Create user (email_verified defaults to False)
user = await auth_service.create_user(...)
```

To:
```python
# Create user with email verified (TESTING ONLY)
user = await auth_service.create_user(...)
user.email_verified = True  # Add this line
```

### 6. Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Email already registered" | Email exists in database | Use different email or reset password |
| "Username already registered" | Username taken | Choose different username |
| "Registration failed" | Backend error | Check backend logs |
| "Erreur de connexion au serveur" | Backend not running | Start backend server |
| "Token invalide ou expiré" | Reset link expired | Request new reset link |

### 7. Environment Variables Checklist

Make sure your `backend/.env` has:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname

# JWT
SECRET_KEY=your-secret-key-here

# Email (REQUIRED for registration/reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FROM_NAME=PhishGuard AI

# OAuth (optional for now)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

### 8. Still Not Working?

1. **Restart backend server** after changing `.env`
2. **Clear browser cache** and localStorage
3. **Check firewall** isn't blocking SMTP port 587
4. **Try different email provider** (Gmail, Outlook, etc.)
5. **Check backend console** for real-time errors

### Need More Help?

Check the logs and share:
1. Error message from browser console
2. Error from `backend/phishguard.log`
3. Your `.env` configuration (hide sensitive values)
