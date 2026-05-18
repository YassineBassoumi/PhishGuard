# 🛡️ PhishGuard AI - Advanced Phishing Detection System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.5-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2.0-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

PhishGuard AI is an intelligent phishing detection system that combines machine learning models with rule-based analysis to protect users from email and URL-based phishing attacks. The system features a modern React frontend and a powerful FastAPI backend with real-time analysis capabilities.

## 🌟 Key Features

### 🔍 Advanced Detection Engine
- **Hybrid Analysis**: Combines email text analysis (LinearSVC, 97.5% accuracy) with URL analysis (Random Forest, 23 features)
- **Real-time Progressive Analysis**: Step-by-step indicators showing analysis progress
- **Bulk Analysis**: Process multiple emails simultaneously with summary statistics
- **Multi-model Approach**: Separate specialized models for email content and URL patterns
- **Decision Tracing**: Full transparency on how verdicts are reached

### 📧 Email Provider Integration
- **Gmail Integration**: OAuth 2.0 authentication with automatic token refresh
- **Outlook Integration**: Microsoft OAuth 2.0 support
- **Direct Inbox Analysis**: Scan emails directly from your mailbox
- **Advanced Search**: Filter and search through your emails
- **Automatic Scanning**: Background monitoring for new threats

### 👤 User Management & Security
- **JWT Authentication**: Secure token-based authentication
- **Two-Factor Authentication (2FA)**: TOTP-based additional security layer
- **Email Verification**: Confirm user email addresses
- **Password Reset**: Secure password recovery flow
- **Session Management**: Track and manage active sessions across devices
- **Rate Limiting**: Protection against abuse and DDoS attacks
- **Account Security**: Profile management with security settings

### 📊 Analytics & Reporting
- **Personal Dashboard**: View your analysis history and statistics
- **Threat Distribution**: Visualize threat levels across analyses
- **Historical Data**: Filter and search past analyses
- **Real-time Notifications**: Get alerted about detected threats
- **Admin Panel**: System-wide statistics and user management

### 🎨 Modern User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Dark/Light Mode**: Comfortable viewing in any environment
- **Interactive Charts**: Powered by Recharts for data visualization
- **Real-time Updates**: Live analysis progress indicators
- **Intuitive Navigation**: Clean, user-friendly interface


## 🏗️ Architecture

### Technology Stack

**Backend:**
- **Framework**: FastAPI 0.115.5 (Python 3.9+)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (async)
- **ML Libraries**: scikit-learn 1.8.0, XGBoost 2.1.3, pandas, numpy
- **Authentication**: python-jose (JWT), passlib (bcrypt), pyotp (2FA)
- **Email APIs**: google-api-python-client, httpx
- **Feature Extraction**: tldextract, email-validator

**Frontend:**
- **Framework**: React 19.2.0 with Vite 7.2.4
- **Routing**: React Router DOM 7.13.0
- **Styling**: Tailwind CSS 4.1.18
- **Charts**: Recharts 3.7.0
- **Icons**: Lucide React 0.563.0
- **HTTP Client**: Axios 1.13.5

### Project Structure

```
PhishGuard/
├── backend/
│   ├── app/
│   │   ├── models/              # Database models & Pydantic schemas
│   │   │   ├── database_models.py
│   │   │   ├── user_models.py
│   │   │   ├── schemas.py
│   │   │   └── ...
│   │   ├── routes/              # API endpoints
│   │   │   ├── analysis.py      # Core analysis endpoints
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── gmail.py         # Gmail integration
│   │   │   ├── outlook.py       # Outlook integration
│   │   │   ├── admin.py         # Admin panel
│   │   │   └── ...
│   │   ├── services/            # Business logic
│   │   │   ├── detection/       # ML detection system
│   │   │   │   ├── hybrid_email_detector.py
│   │   │   │   ├── email_detector.py
│   │   │   │   ├── url_detector.py
│   │   │   │   ├── email_preprocessor.py
│   │   │   │   ├── feature_extractors/
│   │   │   │   │   ├── email_features.py
│   │   │   │   │   └── url_features.py
│   │   │   │   ├── models/
│   │   │   │   │   ├── model_loader.py
│   │   │   │   │   └── model_config.py
│   │   │   │   └── utils/
│   │   │   ├── auth_service.py
│   │   │   ├── stats_service.py
│   │   │   └── ...
│   │   ├── middleware/          # Custom middleware
│   │   │   ├── rate_limiter.py
│   │   │   └── database_monitor.py
│   │   ├── database.py          # Database configuration
│   │   └── main.py              # Application entry point
│   ├── ml_models/               # Trained ML models
│   │   ├── phishing_model.pkl
│   │   ├── vectorizer.pkl
│   │   └── phishing_url_best_model.pkl
│   ├── scripts/                 # Utility scripts
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── AnalysisForm.jsx
│   │   │   ├── ResultsDisplay.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── EmailProviderSelector.jsx
│   │   │   ├── admin/
│   │   │   └── ...
│   │   ├── contexts/            # React contexts
│   │   │   ├── AuthContext.jsx
│   │   │   └── EmailProviderContext.jsx
│   │   ├── services/            # API services
│   │   │   └── adminApi.js
│   │   ├── pages/               # Page components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── public/
│   ├── package.json
│   └── vite.config.js
└── README.md
```


## 🚀 Getting Started

### Prerequisites

- **Python**: 3.9 or higher
- **Node.js**: 16 or higher
- **PostgreSQL**: 13 or higher
- **pip**: Python package manager
- **npm**: Node package manager

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/YassineBassoumi/PhishGuard.git
cd PhishGuard
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# Initialize database
python scripts/init_db.py

# Start the backend server
python run.py
```

The backend API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

#### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`


## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/phishguard_db

# JWT Configuration
SECRET_KEY=your-secret-key-here-generate-a-strong-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email Configuration (for notifications and verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM_EMAIL=noreply@phishguard.com
SMTP_FROM_NAME=PhishGuard AI

# Google OAuth (Gmail Integration)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/gmail/callback

# Microsoft OAuth (Outlook Integration)
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/outlook/callback

# Application Settings
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Security Settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### OAuth Setup

#### Gmail Integration

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URI: `http://localhost:8000/api/gmail/callback`
6. Copy Client ID and Client Secret to `.env`

#### Outlook Integration

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register a new application
3. Add Microsoft Graph API permissions (Mail.Read)
4. Add redirect URI: `http://localhost:8000/api/outlook/callback`
5. Create a client secret
6. Copy Application (client) ID and secret to `.env`

### Database Setup

```bash
# Create PostgreSQL database
createdb phishguard_db

# Or using psql
psql -U postgres
CREATE DATABASE phishguard_db;
\q

# Run migrations (handled by init_db.py)
python backend/scripts/init_db.py
```


## 📖 API Documentation

### Core Endpoints

#### Analysis Endpoints

**POST /api/analyze-email**
- Analyze email/message content using hybrid approach (text + URL analysis)
- Requires authentication
- Request body: `{"content": "email text"}`
- Returns: threat level, confidence, features, recommendations, decision trace

**POST /api/analyze-url**
- Analyze URL for phishing indicators
- Requires authentication
- Request body: `{"url": "https://example.com"}`
- Returns: threat level, confidence, features, recommendations

**POST /api/analyze-bulk**
- Analyze multiple emails in bulk (max 50)
- Requires authentication
- Request body: `{"emails": ["email1", "email2", ...]}`
- Returns: individual results + summary statistics

**POST /api/analyze-progressive**
- Progressive URL analysis with step-by-step indicators
- Requires authentication
- Returns: real-time analysis indicators + final verdict

**POST /api/analyze-email-progressive**
- Progressive email analysis with step-by-step indicators
- Requires authentication
- Returns: real-time analysis indicators + final verdict

#### Authentication Endpoints

**POST /api/auth/register**
- Register new user account
- Request body: `{"username": "user", "email": "user@example.com", "password": "password"}`

**POST /api/auth/login**
- Login and receive JWT token
- Request body: `{"username": "user", "password": "password"}`

**POST /api/auth/verify-email**
- Verify email address with token

**POST /api/auth/enable-2fa**
- Enable two-factor authentication
- Returns QR code for authenticator app

**POST /api/auth/verify-2fa**
- Verify 2FA code during login

#### Statistics Endpoints

**GET /api/stats**
- Get user-specific statistics
- Requires authentication

**GET /api/history**
- Get analysis history with filters
- Query params: `limit`, `analysis_type`, `threat_level`, `start_date`, `end_date`
- Requires authentication

**GET /api/threat-distribution**
- Get threat level distribution
- Requires authentication

#### Email Provider Endpoints

**GET /api/gmail/auth**
- Initiate Gmail OAuth flow

**GET /api/gmail/emails**
- Fetch emails from Gmail
- Requires authentication + Gmail connection

**GET /api/outlook/auth**
- Initiate Outlook OAuth flow

**GET /api/outlook/emails**
- Fetch emails from Outlook
- Requires authentication + Outlook connection

For complete API documentation, visit `http://localhost:8000/docs` after starting the backend.


## 🤖 Machine Learning Models

### Hybrid Detection System

PhishGuard uses a sophisticated hybrid approach that combines multiple specialized models:

#### 1. Email Text Detector
- **Algorithm**: LinearSVC (Support Vector Classification)
- **Vectorization**: TF-IDF (Term Frequency-Inverse Document Frequency)
- **Accuracy**: 97.5%
- **Features**: Text patterns, keywords, linguistic analysis
- **Model Files**: 
  - `phishing_model.pkl` - Trained SVM classifier
  - `vectorizer.pkl` - TF-IDF vectorizer
- **Use Case**: Analyzes email content for phishing patterns, urgency language, and suspicious keywords

#### 2. URL Detector
- **Algorithm**: Random Forest Classifier
- **Features**: 23 URL-based features including:
  - Domain characteristics (length, entropy, TLD risk)
  - URL structure (special characters, path depth, subdomains)
  - Security indicators (HTTPS, IP usage, shorteners)
  - Suspicious patterns (embedded domains, @ symbols)
- **Accuracy**: 100% on test dataset
- **Model File**: `phishing_url_best_model.pkl`
- **Use Case**: Deep analysis of URLs extracted from emails

#### 3. Hybrid Combiner
- **Logic**: Intelligent rule-based combination of text and URL verdicts
- **Priority Rules**:
  1. Dangerous URL + Non-safe text → DANGEROUS
  2. Majority URLs dangerous → DANGEROUS
  3. Dangerous text + Suspicious URL → DANGEROUS
  4. Dangerous URL + Safe text → SUSPICIOUS (escalation)
  5. Any suspicious URL → SUSPICIOUS
  6. Suspicious text + All safe URLs → SAFE (downgrade)
  7. All safe → SAFE
- **Confidence**: Weighted average (60% text, 40% URLs)
- **Decision Tracing**: Full transparency on which rules fired

### Feature Extraction

#### Email Features
- Phishing keywords detection
- Urgency language patterns
- Credential request indicators
- Suspicious link patterns
- HTML/text content analysis
- Sender information validation

#### URL Features (23 total)
1. `is_https` - HTTPS protocol presence
2. `use_of_ip` - IP address instead of domain
3. `subdomain_count` - Number of subdomains
4. `hostname_length` - Length of hostname
5. `domain_entropy` - Randomness of domain name
6. `tld_risk` - Top-level domain risk score
7. `sus_url` - Suspicious keywords in URL
8. `short_url` - URL shortener detection
9. `url_length` - Total URL length
10. `count@` - @ symbol count
11. `count_embed_domian` - Embedded domain patterns
12. `path_length` - URL path length
13. `count_dir` - Directory depth
14. `special_char_ratio` - Ratio of special characters
15. `count-` - Hyphen count
16. `count-digits` - Digit count
17-23. Additional structural features

### Model Training

Models were trained on curated phishing datasets with:
- **Email Dataset**: 10,000+ legitimate and phishing emails
- **URL Dataset**: 50,000+ legitimate and phishing URLs
- **Validation**: Cross-validation with 80/20 train-test split
- **Optimization**: Hyperparameter tuning using GridSearchCV


## 🧪 Testing

### Manual Testing

#### Test Email Analysis
```bash
curl -X POST http://localhost:8000/api/analyze-email \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "content": "URGENT! Your account has been suspended. Click here to verify: http://suspicious-link.com"
  }'
```

#### Test URL Analysis
```bash
curl -X POST http://localhost:8000/api/analyze-url \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "url": "http://phishing-site.com/login"
  }'
```

#### Test Bulk Analysis
```bash
curl -X POST http://localhost:8000/api/analyze-bulk \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "emails": [
      "Legitimate email content here",
      "URGENT! Click this link now!",
      "Your package is ready for delivery"
    ]
  }'
```

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Running Debug Scripts

```bash
# Test email analysis consistency
python backend/scripts/debug_email_analysis_inconsistency.py

# Initialize/reset database
python backend/scripts/init_db.py
```


## 🔒 Security Features

### Authentication & Authorization
- **JWT Tokens**: Secure stateless authentication
- **Password Hashing**: Bcrypt with salt
- **Two-Factor Authentication**: TOTP-based (compatible with Google Authenticator, Authy)
- **Email Verification**: Confirm user email addresses
- **Session Management**: Track and revoke active sessions
- **Password Reset**: Secure token-based password recovery

### API Security
- **Rate Limiting**: Configurable request limits per IP
- **CORS**: Configured for specific origins
- **Input Validation**: Pydantic schemas for all requests
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
- **XSS Protection**: Content sanitization

### Data Protection
- **Database Encryption**: Sensitive data encrypted at rest
- **Token Expiration**: Automatic cleanup of expired sessions
- **Secure OAuth**: Industry-standard OAuth 2.0 flows
- **Environment Variables**: Sensitive config in .env files (not committed)

### Monitoring & Logging
- **Request Logging**: All API requests logged
- **Error Tracking**: Detailed error logs with stack traces
- **Database Monitoring**: Connection pool and query performance tracking
- **Audit Trail**: Analysis history with user attribution


## 🐛 Troubleshooting

### Common Issues

#### 1. Gmail "invalid_grant" Error
**Problem**: Gmail OAuth tokens expire after 7 days in development mode

**Solution**:
- Publish your Google Cloud app to production
- Or implement automatic token refresh (already included in PhishGuard)
- See detailed guide: [GMAIL_TOKEN_FIX.md](GMAIL_TOKEN_FIX.md)

#### 2. Database Connection Error
**Problem**: `asyncpg.exceptions.InvalidCatalogNameError`

**Solution**:
```bash
# Create the database
createdb phishguard_db

# Or update DATABASE_URL in .env to point to existing database
```

#### 3. CORS Errors in Frontend
**Problem**: Browser blocks API requests

**Solution**:
- Ensure frontend URL is in `origins` list in `backend/app/main.py`
- Check that backend is running on correct port (8000)
- Verify FRONTEND_URL in .env matches your dev server

#### 4. ML Models Not Found
**Problem**: `FileNotFoundError: phishing_model.pkl`

**Solution**:
- Ensure `ml_models/` directory exists in backend
- Models should be in `backend/ml_models/`
- Contact repository maintainer for trained model files

#### 5. Rate Limit Exceeded
**Problem**: `429 Too Many Requests`

**Solution**:
- Wait for rate limit window to reset (default: 60 seconds)
- Adjust `RATE_LIMIT_REQUESTS` in .env for development
- Use authentication to get higher limits

#### 6. Email Analysis Inconsistency
**Problem**: Different results for same email from different sources

**Solution**:
- This was fixed in v1.0 with HTML preprocessing
- Ensure you're using latest version
- See: [FIX_EMAIL_ANALYSIS_INCONSISTENCY.md](FIX_EMAIL_ANALYSIS_INCONSISTENCY.md)

### Debug Mode

Enable detailed logging:

```python
# In backend/app/main.py
logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Getting Help

- Check the [Issues](https://github.com/YassineBassoumi/PhishGuard/issues) page
- Review API documentation at `/docs`
- Check application logs in `backend/phishguard.log`


## 📚 Additional Documentation

### Project Documentation
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Summary of recent fixes and improvements
- **[GMAIL_TOKEN_FIX.md](GMAIL_TOKEN_FIX.md)** - Gmail OAuth token management guide
- **[FIX_EMAIL_ANALYSIS_INCONSISTENCY.md](FIX_EMAIL_ANALYSIS_INCONSISTENCY.md)** - Email analysis consistency fix

### Technical Documentation
- **[BACKEND_PART2_MODELS.md](BACKEND_PART2_MODELS.md)** - Database models and schemas
- **[BACKEND_PART3_ROUTES.md](BACKEND_PART3_ROUTES.md)** - API routes documentation
- **[BACKEND_PART4_SERVICES.md](BACKEND_PART4_SERVICES.md)** - Service layer architecture
- **[ML_URL_FEATURES_DOCUMENTATION.md](ML_URL_FEATURES_DOCUMENTATION.md)** - ML feature engineering details

### Scripts Documentation
- **[backend/scripts/README.md](backend/scripts/README.md)** - Utility scripts guide


## 🚀 Deployment

### Production Considerations

#### Backend Deployment

1. **Environment Variables**: Update `.env` for production
   - Use strong `SECRET_KEY`
   - Set production database URL
   - Configure production OAuth redirect URIs
   - Update `FRONTEND_URL` to production domain

2. **Database**: 
   - Use managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
   - Enable SSL connections
   - Set up automated backups

3. **Server**:
   - Use production ASGI server (Uvicorn with Gunicorn)
   - Enable HTTPS with SSL certificates
   - Configure reverse proxy (Nginx)
   - Set up process manager (systemd, supervisor)

4. **Security**:
   - Enable rate limiting
   - Configure CORS for production domain only
   - Set up monitoring and alerting
   - Regular security updates

#### Frontend Deployment

1. **Build**:
```bash
cd frontend
npm run build
```

2. **Deploy**: 
   - Static hosting (Vercel, Netlify, AWS S3 + CloudFront)
   - Update API base URL to production backend
   - Configure environment variables

3. **CDN**: Use CDN for static assets

#### Docker Deployment (Optional)

```dockerfile
# Example Dockerfile for backend
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```


## 🤝 Contributing

We welcome contributions to PhishGuard! Here's how you can help:

### Development Workflow

1. **Fork the Repository**
```bash
git clone https://github.com/YassineBassoumi/PhishGuard.git
cd PhishGuard
```

2. **Create a Feature Branch**
```bash
git checkout -b feature/amazing-feature
```

3. **Make Your Changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation as needed

4. **Test Your Changes**
   - Test all affected endpoints
   - Verify frontend functionality
   - Check for console errors

5. **Commit Your Changes**
```bash
git add .
git commit -m "Add amazing feature"
```

6. **Push to Your Fork**
```bash
git push origin feature/amazing-feature
```

7. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review

### Code Style

**Python (Backend)**:
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and small

**JavaScript/React (Frontend)**:
- Use functional components with hooks
- Follow React best practices
- Use meaningful variable names
- Keep components modular

### Areas for Contribution

- 🐛 Bug fixes
- ✨ New features
- 📝 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Test coverage
- 🌐 Internationalization
- 🔒 Security improvements
- ⚡ Performance optimizations


## 📊 Project Statistics

- **Backend**: ~15,000 lines of Python code
- **Frontend**: ~10,000 lines of JavaScript/React code
- **API Endpoints**: 50+ REST endpoints
- **ML Models**: 3 trained models (Email SVM, URL Random Forest, Hybrid Combiner)
- **Database Tables**: 10+ tables with relationships
- **React Components**: 40+ reusable components
- **Features**: 23 URL features, 100+ email text features

## 🎯 Roadmap

### Version 1.1 (Planned)
- [ ] Mobile app (React Native)
- [ ] Browser extension (Chrome, Firefox)
- [ ] Advanced reporting and analytics
- [ ] Multi-language support
- [ ] API rate limiting per user tier

### Version 1.2 (Future)
- [ ] Real-time email monitoring
- [ ] Integration with more email providers
- [ ] Custom ML model training interface
- [ ] Threat intelligence feeds integration
- [ ] Team collaboration features

### Version 2.0 (Vision)
- [ ] Deep learning models (BERT, transformers)
- [ ] Image-based phishing detection
- [ ] SMS/WhatsApp phishing detection
- [ ] Enterprise features (SSO, LDAP)
- [ ] White-label solution


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 PhishGuard Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 👥 Authors & Contributors

- **Yassine Bassoumi** - *Initial work* - [YassineBassoumi](https://github.com/YassineBassoumi)

See also the list of [contributors](https://github.com/YassineBassoumi/PhishGuard/contributors) who participated in this project.

## 🙏 Acknowledgments

- **Phishing Datasets**: Thanks to the cybersecurity community for providing training datasets
- **Open Source Libraries**: FastAPI, React, scikit-learn, and all other dependencies
- **Security Research**: Inspired by academic research in phishing detection
- **Community**: Thanks to all contributors and users providing feedback

## 📞 Contact & Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/YassineBassoumi/PhishGuard/issues)
- **Email**: support@phishguard.com (if available)
- **Documentation**: [Full documentation](https://github.com/YassineBassoumi/PhishGuard/wiki)

## ⭐ Star History

If you find PhishGuard useful, please consider giving it a star on GitHub! It helps the project grow and reach more users.

---

**Built with ❤️ for a safer internet**

**Last Updated**: May 18, 2026
**Version**: 1.0.0
**Status**: Active Development
