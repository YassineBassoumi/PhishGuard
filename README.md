# 🛡️ PhishGuard AI

> An intelligent phishing detection system powered by machine learning that analyzes emails and URLs to protect users from phishing threats.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.2-blue.svg)](https://reactjs.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Machine Learning Models](#machine-learning-models)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

**PhishGuard AI** is a comprehensive phishing detection system that uses advanced machine learning algorithms to identify and protect against phishing attempts in emails and URLs. With Gmail integration, bulk analysis capabilities, and real-time threat detection, PhishGuard provides enterprise-grade security accessible to everyone.

### Key Highlights

- 🤖 **ML-Powered Detection** - 95%+ accuracy with Gradient Boosting and SVM models
- 📧 **Gmail Integration** - Direct Gmail inbox scanning with OAuth2
- 📊 **Advanced Analytics** - Real-time dashboard with threat distribution charts
- 🔍 **Bulk Analysis** - Process up to 50 emails or URLs simultaneously
- 🎨 **Modern UI** - Beautiful glassmorphism design with responsive layout
- 🔒 **Secure** - JWT authentication, bcrypt password hashing, and user data isolation

## ✨ Features

### Core Detection Capabilities

#### 📧 Email Phishing Detection
- **ML-Powered Analysis** using Support Vector Machine (SVM) with TF-IDF vectorization
- **Feature Detection**: phishing keywords, urgency language, credential requests
- **Confidence Scoring**: 0-100% threat confidence levels
- **Threat Classification**: Safe, Suspicious, or Dangerous
- **Real-time Analysis**: Instant results with detailed recommendations

#### 🔗 URL Phishing Detection (v3)
Advanced URL analysis with **12 optimized features**:
1. IP Address Detection
2. URL Length Analysis
3. URL Shortener Detection (60+ services)
4. @ Symbol Detection
5. Double Slash Redirecting
6. Dash in Domain (Typosquatting)
7. Subdomain Analysis
8. HTTPS Protocol Check
9. Non-standard Port Detection
10. Suspicious Keywords
11. Subdomain Parts Count
12. Suspicious TLD Detection

**Performance**: <100ms per URL, 95%+ accuracy

### User Features

- **🔐 Authentication System**: Secure registration, login, and profile management
- **📬 Gmail Integration**: OAuth2-based email fetching and analysis
- **📊 Bulk Analysis**: Process multiple emails/URLs with progress tracking
- **📈 Analytics Dashboard**: Statistics, threat distribution, and activity feed
- **🔍 Advanced Filtering**: Filter by type, threat level, date range, and search
- **💾 Analysis History**: Persistent storage of all analyses with SQLite

### UI/UX

- Modern glassmorphism design
- Fully responsive (mobile, tablet, desktop)
- Tab-based navigation
- Color-coded threat levels (🟢 Safe, 🟡 Suspicious, 🔴 Dangerous)
- Real-time updates and auto-refresh
- Interactive charts and visualizations

## 🚀 Technology Stack

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Database**: SQLite with SQLAlchemy (async)
- **Authentication**: JWT with bcrypt
- **ML Libraries**: scikit-learn, joblib
- **Gmail API**: OAuth2 integration
- **Python**: 3.8+

### Frontend
- **Framework**: React 19.2 with Vite
- **Styling**: Custom CSS with glassmorphism
- **State Management**: React Context API
- **Charts**: Custom SVG-based visualizations

### Machine Learning
- **Email Model**: SVM with TF-IDF vectorization
- **URL Model**: Gradient Boosting Classifier (12 features)
- **Training Dataset**: PhiUSIIL (235K URLs)
- **Model Accuracy**: 95%+ (URL), 85-90% (Email)

## 🛠️ Getting Started

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 16 or higher
- **npm** or **yarn**
- **Git**

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YassineBassoumi/PhishGuard.git
   cd PhishGuard
   ```

2. **Backend Setup**
   ```bash
   cd backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the `backend` directory:
   ```env
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///./phishguard.db
   GMAIL_CLIENT_ID=your-gmail-client-id
   GMAIL_CLIENT_SECRET=your-gmail-client-secret
   ```

5. **Initialize Database**
   ```bash
   cd backend
   python
   >>> from database import init_db
   >>> init_db()
   >>> exit()
   ```

## 🎯 Usage

### Running the Application

1. **Start the Backend** (from `backend` directory)
   ```bash
   python main.py
   ```
   Backend will run on `http://localhost:8000`

2. **Start the Frontend** (from `frontend` directory)
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Access the Application**
   
   Open your browser and navigate to `http://localhost:5173`

### First-Time Setup

1. **Register** a new account
2. **Login** with your credentials
3. Start analyzing emails and URLs!

### Gmail Integration (Optional)

To enable Gmail integration:
1. Create a Google Cloud project
2. Enable Gmail API
3. Create OAuth 2.0 credentials
4. Add credentials to `.env` file
5. Configure authorized redirect URIs

## 📚 API Documentation

Once the backend is running, visit the auto-generated API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update profile

#### Analysis
- `POST /api/analyze` - Analyze email or URL
- `POST /api/analyze/bulk` - Bulk analysis
- `GET /api/history` - Get analysis history
- `GET /api/history/filter` - Filtered history

#### Gmail
- `GET /api/gmail/auth` - Get Gmail OAuth URL
- `GET /api/gmail/callback` - OAuth callback
- `GET /api/gmail/emails` - Fetch Gmail emails
- `POST /api/gmail/analyze` - Analyze Gmail email

#### Statistics
- `GET /api/stats` - User statistics
- `GET /api/stats/distribution` - Threat distribution

## 🤖 Machine Learning Models

### URL Phishing Model (v3)

- **Algorithm**: Gradient Boosting Classifier
- **Features**: 12 optimized URL features
- **Training Data**: PhiUSIIL dataset (235,000 URLs)
- **Accuracy**: 95%+
- **Performance**: <100ms per URL

### Email Phishing Model

- **Algorithm**: Support Vector Machine (SVM)
- **Vectorization**: TF-IDF
- **Training Data**: Spam email dataset
- **Accuracy**: 85-90%
- **Performance**: <200ms per email

### Model Files

Models are located in `backend/models/`:
- `phishing_url_model_final_v3.pkl` - URL detection model
- `phishing_model.pkl` - Email detection model
- `vectorizer.pkl` - TF-IDF vectorizer

## 📸 Screenshots

<!-- Add screenshots here once available -->

## 🏗️ Project Structure

```
PhishGuard/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database models
│   ├── auth.py                 # Authentication logic
│   ├── models/                 # ML model files
│   ├── test_*.py               # Testing scripts
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── App.jsx             # Main application
│   │   └── index.css           # Styles
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
└── README.md
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Test URL detection
python test_url_quick.py

# Integration tests
python test_integration.py
```

### Model Testing

```bash
# Test URL model with sample URLs
python test_url_quick.py https://example.com
```

## 📊 Performance Metrics

- **URL Analysis**: <100ms per URL
- **Email Analysis**: <200ms per email
- **Bulk Processing**: 50 emails in <10 seconds
- **Model Accuracy**: 95%+ for URLs, 85-90% for emails
- **Database Queries**: <50ms average
- **API Response Time**: <300ms average

## 🔮 Roadmap

- [ ] Password reset via email
- [ ] Two-factor authentication (2FA)
- [ ] Browser extension
- [ ] Mobile app (iOS/Android)
- [ ] Export reports (PDF, CSV)
- [ ] Real-time email monitoring
- [ ] Advanced ML model training interface
- [ ] Team collaboration features
- [ ] Webhook integrations

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Yassine Bassoumi**
- GitHub: [@YassineBassoumi](https://github.com/YassineBassoumi)
- Email: yassinebasoumi@gmail.com

## 🙏 Acknowledgments

- PhiUSIIL dataset for URL phishing detection
- FastAPI for the amazing backend framework
- React team for the frontend framework
- scikit-learn for ML capabilities
- All contributors and supporters

---

<div align="center">

**⭐ If you find PhishGuard helpful, please consider giving it a star! ⭐**

Made with ❤️ by [Yassine Bassoumi](https://github.com/YassineBassoumi)

</div>
