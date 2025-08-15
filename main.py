
import os
from flask import Flask, flash, render_template, request, redirect, jsonify, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
from flask_sqlalchemy import SQLAlchemy

# local imports (assumes you have model.py and chatbot_logic.py)a
# model.py should expose: db, User, Chat
# chatbot_logic.get_bot_response(message) should check local FAQ/DB and return a string or None
from app.model import User, Chat
from chatbot_logic import get_bot_response


# Load environment variables from .env
# from pathlib import Path
# load_dotenv(dotenv_path=Path(__file__).parent / "api.env")


# # Read OpenAI API key from environment variable (do NOT hardcode)
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")

# # Initialize OpenAI client
# client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

app = Flask(__name__)

# Basic config
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "change-me-in-production")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///todo.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy()

# Initialize DB and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create DB tables if not present
with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


@app.route('/')
def home():
    # Chat frontend (templates/index.html)
    return render_template('index.html')


@app.route('/base')
def base():
    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', "").strip()
        password = request.form.get('password', "")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for('home'))
        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username', "").strip()
        email = request.form.get('email', "").strip()
        password = request.form.get('password', "")

        if not username or not email or not password:
            flash("Please fill all fields.", "warning")
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for('login'))

        hashed = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        flash("Signup successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for('login'))


def save_chat(user_id, message, response_text):
    """Helper to save chat in DB. user_id can be None for anonymous."""
    try:
        entry = Chat(user_id=user_id or None, message=message, response=response_text)
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        app.logger.error("Failed to save chat to DB: %s", e)


# def ask_openai(question: str) -> str:
#     """Call OpenAI and return text response (or raise an exception)."""
#     # Use a small temperature to get consistent answers; tune as needed.
#     resp = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful, safe healthcare assistant. Don't give a medical diagnosis."},
#             {"role": "user", "content": question}
#         ],
#         temperature=0.3,
#         max_tokens=800,
#     )
#     # The structure below matches the SDK pattern used earlier in this project
#     return resp.choices[0].message.content


@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        bot_reply = get_bot_response(user_message)  # call your chatbot function
        return jsonify({"response": bot_reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


    # try:
    #     completion = client.chat.completions.create(
    #         model="gpt-4o-mini",  # or "gpt-3.5-turbo" if preferred
    #         messages=[
    #             {"role": "system", "content": "You are a helpful healthcare chatbot."},
    #             {"role": "user", "content": user_message}
    #         ],
    #         max_tokens=200
    #     )

    #     bot_response = completion.choices[0].message.content.strip()
    #     return jsonify({"response": bot_response})

    # except Exception as e:
    #     return jsonify({"error": str(e)})


# A simple debug route that returns recent chats (optional; remove in production)
@app.route('/recent_chats', methods=['GET'])
@login_required
def recent_chats():
    try:
        chats = Chat.query.order_by(Chat.id.desc()).limit(50).all()
        out = [{"id": c.id, "user_id": c.user_id, "message": c.message, "response": c.response} for c in chats]
        return jsonify(out)
    except Exception as e:
        app.logger.error("Failed to fetch chats: %s", e)
        return jsonify({"error": "Server error"}), 500
    

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

if __name__ == '__main__':
    # Use debug=True while developing; set to False in production
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
