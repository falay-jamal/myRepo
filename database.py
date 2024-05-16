from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, UserMixin
import mysql.connector
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_fallback_key')

login_manager = LoginManager()
login_manager.init_app(app)

db = mysql.connector.connect(
    host="localhost",
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', '12345'),
    database="streamlit_logins",
    ssl_disabled=False
)

cursor = db.cursor()

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f"User({self.username!r})"

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()
    if row:
        return User(row[0], row[1], row[2])  # Return an instance of User

@app.route("/register", methods=["POST"])
def register():
    data = request.form
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username or password not provided"}), 400

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        return jsonify({"error": "Username is already taken"}), 409

    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    db.commit()
    return jsonify({"message": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.form
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username or password not provided"}), 400

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user_data = cursor.fetchone()
    if user_data and check_password_hash(user_data[2], password):
        user = User(user_data[0], user_data[1], user_data[2])
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route("/")
def index():
    return "Welcome to the index page"

if __name__ == "__main__":
    app.run(debug=True)
