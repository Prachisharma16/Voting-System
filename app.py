from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime
import hashlib
import re
import requests
import google.generativeai as genai

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# =========================
# FLASK-LOGIN SETUP
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, id, username, email=None, google_id=None):
        self.id = id
        self.username = username
        self.email = email
        self.google_id = google_id
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, google_id FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'], user['google_id'])
    return None


# =========================
# VALIDATION FUNCTIONS (Instagram-like)
# =========================

def is_valid_username(username):
    """Username: alphanumeric, underscores, periods, 3-30 characters"""
    return re.fullmatch(r"[a-zA-Z0-9_.]{3,30}", username) is not None


def is_valid_password(password):
    """Password: minimum 6 characters"""
    return len(password) >= 6


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# =========================
# DATABASE SETUP
# =========================

def get_db_connection():
    conn = sqlite3.connect('voting.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            has_voted BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            voted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add default candidates if none exist
    cursor.execute("SELECT COUNT(*) FROM candidates")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO candidates (name, description) VALUES (?, ?)", 
                       ('Alice Johnson', 'Experienced leader with vision for progress'))
        cursor.execute("INSERT INTO candidates (name, description) VALUES (?, ?)", 
                       ('Bob Williams', 'Dedicated advocate for community growth'))
        cursor.execute("INSERT INTO candidates (name, description) VALUES (?, ?)", 
                       ('Carol Davis', 'Innovative thinker with practical solutions'))
    
    conn.commit()
    conn.close()


def get_candidates():
    """Get all candidates from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description FROM candidates ORDER BY id")
    candidates = cursor.fetchall()
    conn.close()
    return {c['id']: {'name': c['name'], 'description': c['description']} for c in candidates}


init_database()


# =========================
# GEMINI CONFIG
# =========================
GEMINI_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)


# =========================
# ROUTES
# =========================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error = 'Please enter both username and password.'
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            password_hash = hash_password(password)
            cursor.execute(
                "SELECT id, username, email, google_id FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_obj = User(user['id'], user['username'], user['email'], user['google_id'])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid username or password.'
    
    return render_template('login.html', error=error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error = 'Please fill in all fields.'
        elif not is_valid_username(username):
            error = 'Invalid username. Use 3-30 characters (letters, numbers, underscores, periods).'
        elif not is_valid_password(password):
            error = 'Password must be at least 6 characters.'
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            password_hash = hash_password(password)
            
            try:
                cursor.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, password_hash)
                )
                conn.commit()
                
                cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
                user = cursor.fetchone()
                conn.close()
                
                user_obj = User(user['id'], user['username'])
                login_user(user_obj)
                return redirect(url_for('dashboard'))
            except sqlite3.IntegrityError:
                conn.close()
                error = 'Username already exists. Please choose a different one.'
    
    return render_template('register.html', error=error)


# =========================
# DASHBOARD ROUTES
# =========================

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.id
    username = current_user.username
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT has_voted FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    has_voted = bool(user['has_voted']) if user else False
    
    # Get candidates from database
    cursor.execute("SELECT id, name, description FROM candidates ORDER BY id")
    candidates_rows = cursor.fetchall()
    candidates = {c['id']: {'name': c['name'], 'description': c['description']} for c in candidates_rows}
    
    cursor.execute("SELECT candidate_id, COUNT(*) as votes FROM votes GROUP BY candidate_id")
    votes_data = cursor.fetchall()
    conn.close()
    
    total_votes = 0
    for row in votes_data:
        if row['candidate_id'] in candidates:
            candidates[row['candidate_id']]['votes'] = row['votes']
            total_votes += row['votes']
    
    results = []
    for cid, data in candidates.items():
        votes = data.get('votes', 0)
        percentage = round((votes / total_votes * 100), 1) if total_votes > 0 else 0
        results.append({
            'id': cid,
            'name': data['name'],
            'description': data.get('description', ''),
            'votes': votes,
            'percentage': percentage
        })
    
    return render_template('dashboard.html',
                           username=username, 
                           has_voted=has_voted,
                           results=results,
                           total_votes=total_votes,
                           candidates=candidates)


@app.route('/cast_vote', methods=['POST'])
@login_required
def cast_vote():
    data = request.get_json()
    candidate_id = data.get('candidate')
    
    # Validate candidate exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM candidates WHERE id = ?", (candidate_id,))
    candidate = cursor.fetchone()
    if not candidate:
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid candidate.'})
    
    user_id = current_user.id
    
    cursor.execute("SELECT has_voted FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user or user['has_voted']:
        conn.close()
        return jsonify({'success': False, 'message': 'You have already voted.'})
    
    cursor.execute(
        "INSERT INTO votes (user_id, candidate_id, voted_at) VALUES (?, ?, ?)",
        (user_id, candidate_id, datetime.now())
    )
    cursor.execute(
        "UPDATE users SET has_voted = TRUE WHERE id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Vote recorded successfully!'})


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# =========================
# CHATBOT ROUTES
# =========================

@app.route('/chatbot')
def chatbot():
    """Serve the chatbot interface"""
    return render_template('chatbot.html')


@app.route('/send_message', methods=['POST'])
def send_message():
    """Handle chatbot messages and return AI responses"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    
    # Check if user is logged in
    user_context = ""
    if current_user.is_authenticated:
        user_context = f"Current user: {current_user.username}"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT has_voted FROM users WHERE id = ?", (current_user.id,))
        user = cursor.fetchone()
        conn.close()
        if user and user['has_voted']:
            user_context += " - User has already voted."
        else:
            user_context += " - User has not voted yet."
    
    # Process the message - check if it's a command or conversational
    response = process_chatbot_message(user_message, user_context)
    
    return jsonify({'response': response})


def process_chatbot_message(user_message, context=""):
    """Process chatbot messages and return appropriate responses"""
    message = user_message.lower().strip()
    
    # Direct commands
    commands = {
        'register': 'To register, please go to the registration page: /register',
        'login': 'To login, please go to: /login',
        'vote': 'To vote, please login and visit the dashboard: /dashboard',
        'results': 'View live results on your dashboard after logging in: /dashboard',
        'logout': 'Click logout on the dashboard or visit: /logout',
        'help': '''📖 Available Commands:
• register - Create new account
• login - Sign in to your account  
• vote - Cast your vote
• results - View current results
• logout - Sign out

💡 You can also ask me questions about voting, candidates, or election procedures!''',
    }
    
    # Check for direct commands
    if message in commands:
        return commands[message]
    
    # Conversational queries - use Gemini AI
    try:
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
        
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config=generation_config
        )
        
        prompt = f"""
        You are an AI assistant for a voting system chatbot. Your role is to help users with voting-related queries and provide friendly, helpful responses.

        Context: {context}
        
        User Message: {user_message}
        
        Available voting system commands:
        - register: Create new account
        - login: Sign in to account
        - vote: Cast vote
        - results: View election results
        - logout: Sign out
        - help: Show help
        
        Please respond in a helpful, conversational manner. If the user asks about voting procedures, candidates, or election information, provide helpful information. For technical commands like registration, voting, etc., guide them to use the specific commands.
        
        Keep responses concise (2-3 sentences max) and friendly. If the query is not related to voting, politely redirect to voting topics.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Fallback responses for common questions
        fallback_responses = {
            'hello': 'Hello! 👋 How can I help you with voting today?',
            'hi': 'Hi there! 🗳️ What would you like to know about voting?',
            'hey': 'Hey! 👋 How can I assist you with the voting system?',
            'how does voting work': 'To vote: 1) Register an account, 2) Login, 3) Go to Dashboard, 4) Select a candidate and submit your vote. Each user gets one vote!',
            'candidates': 'The current candidates are:\n1. Alice Johnson - Experienced leader with vision for progress\n2. Bob Williams - Dedicated advocate for community growth\n3. Carol Davis - Innovative thinker with practical solutions',
            'can i vote': 'Yes! If you have an account and haven\'t voted yet, you can cast your vote in the dashboard. Each registered user gets one vote!',
            'election': 'This is a secure voting system where registered users can vote once for their preferred candidate. Results are updated in real-time!',
        }
        
        for key, response in fallback_responses.items():
            if key in message:
                return response
        
        return '🤖 I\'m having trouble connecting to AI right now. Type "help" for available commands or try again later.'


# =========================
# CANDIDATE MANAGEMENT ROUTES
# =========================

@app.route('/manage_candidates', methods=['GET', 'POST'])
@login_required
def manage_candidates():
    """Manage candidates - add new candidates"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if name:
            cursor.execute("INSERT INTO candidates (name, description) VALUES (?, ?)", 
                         (name, description))
            conn.commit()
    
    cursor.execute("SELECT id, name, description FROM candidates ORDER BY id")
    candidates = cursor.fetchall()
    conn.close()
    
    return render_template('manage_candidates.html', candidates=candidates)


@app.route('/delete_candidate/<int:candidate_id>')
@login_required
def delete_candidate(candidate_id):
    """Delete a candidate"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_candidates'))


# =========================
# RUN APP
# =========================
if __name__ == '__main__':
    app.run(debug=True)

