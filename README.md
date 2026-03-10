# 🗳️ AI Voting System with Chatbot

A modern, secure voting system with integrated AI chatbot powered by Google Gemini. Users can register, vote for candidates, view live results, and interact with an intelligent chatbot for voting assistance.

![Voting System](https://img.shields.io/badge/Python-Flask-blue?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Gemini-purple?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## ✨ Features

### 🔐 Authentication
- **User Registration** - Secure account creation with validation
- **Login System** - Session-based authentication
- **Password Security** - SHA-256 hashed passwords

### 🗳️ Voting System
- **Dynamic Candidates** - Add/remove candidates easily
- **One Vote Per User** - Prevents duplicate voting
- **Live Results** - Real-time vote counting with percentages

### 🤖 AI Chatbot
- **Gemini AI Powered** - Intelligent voting assistant
- **Quick Commands** - One-click navigation
- **Conversational Interface** - Natural language queries

### 🎨 Modern UI
- **Instagram-style Design** - Clean, modern interface
- **Responsive** - Works on all devices
- **Animated** - Smooth transitions and effects

## 📁 Project Structure

```
voting chatbot/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── login.html       # Login page
│   ├── register.html   # Registration page
│   ├── dashboard.html  # Main voting dashboard
│   ├── chatbot.html    # AI chatbot interface
│   └── manage_candidates.html # Candidate management
└── static/             # CSS/JS files (if any)
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd "voting chatbot"
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Gemini AI** (Optional)
   - Open `app.py`
   - Replace `YOUR_API_KEY` with your Google Gemini API key:
   ```python
   GEMINI_API_KEY = "your-api-key-here"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open browser**
   - Navigate to: `http://127.0.0.1:5000`

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key
```

### Database
The application uses SQLite (`voting.db`) which is automatically created on first run.

## 📝 Usage Guide

### For Voters
1. **Register** - Create an account at `/register`
2. **Login** - Sign in at `/login`
3. **View Candidates** - See available candidates on dashboard
4. **Cast Vote** - Select your preferred candidate
5. **View Results** - See live election results

### For Administrators
1. **Manage Candidates** - Navigate to `/manage_candidates`
2. **Add Candidate** - Fill in name and description
3. **Delete Candidate** - Remove unwanted candidates

### Chatbot Commands
- `register` - Get registration instructions
- `login` - Get login instructions  
- `vote` - Learn how to vote
- `results` - View election results
- `help` - Show all available commands
- Or ask any question about voting!

## 🛠️ Technologies Used

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Authentication**: Flask-Login
- **AI**: Google Gemini
- **Frontend**: HTML, CSS, JavaScript

## 🔒 Security Features

- Password hashing with SHA-256
- Session-based authentication
- SQL injection prevention (parameterized queries)
- Input validation and sanitization
- One vote per user enforcement

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Google Gemini AI for powering the chatbot
- Flask community for the excellent framework
- Design

 inspiration from Instagram---

Made with ❤️ for secure, modern voting systems

