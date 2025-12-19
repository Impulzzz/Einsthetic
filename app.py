from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from services.ai_service import AIService
from services.firebase_service import FirebaseService
from dotenv import load_dotenv
import os
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret")

# Initialize Services
ai_service = AIService()
firebase_service = FirebaseService()

@app.context_processor
def inject_config():
    return {
        "config": {
            "apiKey": os.getenv("FIREBASE_API_KEY"),
            "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
            "projectId": os.getenv("FIREBASE_PROJECT_ID"),
            "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
            "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
            "appId": os.getenv("FIREBASE_APP_ID")
        }
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.before_request
def auth_gate():
    # Whitelist open routes
    allowed_routes = ['home', 'login', 'signup', 'static', 'api_session_login', 'dev_login']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('home'))

@app.route('/signup')
def signup():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/login')
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# TEMP: Dev Route
@app.route('/dev/login')
def dev_login():
    # Allow custom user ID via query param: /dev/login?uid=test_user_123
    user_id = request.args.get('uid', 'dev_tester')
    session['user'] = {'uid': user_id, 'email': f'{user_id}@test.com'}
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/quiz-setup')
@login_required
def quiz_setup():
    return render_template('quiz_setup.html')

@app.route('/quiz')
@login_required
def quiz():
    # Subject/Difficulty passed via query params, handled by frontend JS
    return render_template('quiz.html')

# API Routes
@app.route('/api/session_login', methods=['POST'])
def api_session_login():
    data = request.json
    id_token = data.get('idToken')
    try:
        decoded_token = firebase_service.verify_token(id_token)
        if decoded_token:
            session['user'] = decoded_token
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@app.route('/api/generate_question', methods=['POST'])
@login_required
def api_generate_question():
    data = request.json
    subject = data.get('subject', 'Algorithms')
    topic = data.get('topic')
    difficulty = data.get('difficulty', 'Medium')
    question = ai_service.generate_question(subject, difficulty, topic)
    if question:
        return jsonify(question)
    return jsonify({"error": "Failed to generate question"}), 500

@app.route('/api/save_attempt', methods=['POST'])
@login_required
def api_save_attempt():
    data = request.json
    print(f"Received save_attempt data: {data}")
    user_id = session['user']['uid'] # Securely get uid from session
    subject = data.get('subject')
    score = data.get('score')
    time_taken = data.get('time_taken')
    question_data = data.get('question_data')
    difficulty = data.get('difficulty', 'Medium')
    is_correct = data.get('is_correct', False)
    
    doc_id = firebase_service.save_attempt(user_id, subject, score, time_taken, question_data, difficulty, is_correct)
    if doc_id:
        return jsonify({"success": True, "id": doc_id})
    return jsonify({"error": "Failed to save data"}), 500

@app.route('/api/analytics/<user_id>', methods=['GET'])
@login_required
def api_analytics(user_id):
    # Ensure user can only access their own analytics or admin
    if user_id != session['user']['uid']:
         return jsonify({"error": "Unauthorized"}), 403
    data = firebase_service.get_user_analytics(user_id)
    return jsonify(data)

@app.route('/api/current_user', methods=['GET'])
@login_required
def api_current_user():
    return jsonify({"uid": session['user']['uid'], "email": session['user'].get('email', '')})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
