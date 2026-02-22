# 🛡️ PhishGuard

A comprehensive phishing detection and email security platform powered by machine learning. PhishGuard helps users identify and protect against phishing attacks through intelligent email and URL analysis.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.100+-green.svg)

## ✨ Features

### 🔍 Detection & Analysis
- **ML-Powered Email Detection** - Advanced machine learning models for phishing email identification
- **URL Analysis** - Real-time URL scanning with high accuracy phishing detection
- **Bulk Analysis** - Process multiple emails simultaneously for efficient threat assessment
- **Risk Scoring** - Detailed risk assessment with actionable recommendations

### 🔐 Security & Authentication
- **Multi-Factor Authentication (2FA)** - Enhanced account security with TOTP
- **Email Verification** - Secure account activation process
- **Session Management** - Monitor and control active sessions across devices
- **Password Reset** - Secure password recovery with email verification
- **Brute Force Protection** - Rate limiting and account lockout mechanisms

### 📧 Email Integration
- **Gmail Integration** - OAuth2 authentication for Gmail accounts
- **Outlook Integration** - Microsoft Graph API integration for Outlook/Office 365
- **Multi-Provider Support** - Manage multiple email accounts from different providers
- **Real-time Sync** - Automatic email fetching and analysis

### 👥 User Management
- **User Profiles** - Customizable profiles with avatar upload
- **Role-Based Access Control** - Admin, user, and superadmin roles
- **Account Security** - Comprehensive security settings and monitoring
- **Activity Tracking** - Detailed audit logs of user actions

### 📊 Admin Panel
- **User Management** - View, edit, ban, and manage user accounts
- **Audit Logs** - Complete system activity tracking
- **Email Provider Management** - Monitor and manage OAuth integrations
- **Statistics Dashboard** - Real-time analytics and insights
- **User Activity Monitoring** - Track login patterns and suspicious behavior

### 🔔 Notifications
- **In-App Notifications** - Real-time alerts for security events
- **Email Alerts** - Notifications for dangerous emails, login attempts, and security changes
- **Customizable Alerts** - Configure notification preferences

## 🏗️ Architecture

```
PhishGuard/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models and schemas
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   │   └── detection/  # ML detection modules
│   │   ├── middleware/     # Rate limiting, monitoring
│   │   └── utils/          # Helper functions
│   ├── ml_models/          # Trained ML models
│   └── scripts/            # Database and setup scripts
│
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   │   └── admin/      # Admin panel components
    │   ├── contexts/       # React contexts
    │   ├── services/       # API services
    │   └── pages/          # Page components
    └── public/             # Static assets
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL database
- Gmail/Outlook OAuth credentials (for email integration)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

5. Initialize database:
```bash
python scripts/init_db.py
```

6. Start the server:
```bash
python run.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📚 API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔧 Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy (async)
- **ML Libraries**: scikit-learn, XGBoost
- **Authentication**: JWT, OAuth2 (Google, Microsoft)
- **Email**: Gmail API, Microsoft Graph API
- **Security**: bcrypt, python-jose, rate limiting

### Frontend
- **Framework**: React 18
- **Styling**: Tailwind CSS
- **Routing**: React Router
- **State Management**: Context API
- **HTTP Client**: Axios
- **UI Components**: Custom components with Tailwind

### Machine Learning
- **Email Detection**: Custom trained model with NLP features
- **URL Detection**: XGBoost classifier with URL feature extraction
- **Feature Engineering**: TF-IDF, domain analysis, pattern recognition

## 🛠️ Development

### Running Tests

Backend tests:
```bash
cd backend
python -m pytest
```

### Database Management

Create a superadmin:
```bash
python scripts/promote_to_superadmin.py
```

Verify user email:
```bash
python scripts/verify_user.py
```

Clean up orphaned profile pictures:
```bash
python scripts/cleanup_orphaned_pictures.py
```

## 📖 Documentation

- [Backend Documentation](./DOCUMENTATION_BACKEND_COMPLETE.md)
- [Frontend Documentation](./DOCUMENTATION_FRONTEND_COMPLETE.md)
- [Backend Implementation Guide](./BACKEND_PART5_FINAL.md)

## 🔒 Security Features

- JWT-based authentication with refresh tokens
- Password hashing with bcrypt
- Rate limiting on sensitive endpoints
- CORS protection
- SQL injection prevention through ORM
- XSS protection
- CSRF token validation
- Session management with device tracking
- Audit logging for security events
- Email notifications for suspicious activities

## 🌟 Key Highlights

- **High Accuracy**: ML models trained on extensive phishing datasets
- **Real-time Protection**: Instant analysis of emails and URLs
- **User-Friendly**: Intuitive interface for both users and administrators
- **Scalable**: Built with modern async architecture
- **Secure**: Enterprise-grade security features
- **Extensible**: Modular design for easy feature additions

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Yassine Bassoumi**
- Email: yassinebasoumi@gmail.com
- GitHub: [@YassineBassoumi](https://github.com/YassineBassoumi)

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📧 Support

For support, email yassinebasoumi@gmail.com or open an issue on GitHub.

---

Made with ❤️ by Yassine Bassoumi
