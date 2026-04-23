import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import errorcode
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "skillify_premium_secret"

# DB Config
DB_CONFIG = {
    'user': 'root',
    'password': 'nashra@2025',
    'host': 'localhost',
    'auth_plugin': 'mysql_native_password'
}
DB_NAME = 'skillify'

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        cursor.execute(f"USE {DB_NAME}")

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(50) NOT NULL,
                lastname VARCHAR(50) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'mentor', 'admin') NOT NULL,
                skills TEXT,
                course TEXT,
                college VARCHAR(100),
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error during initialization: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

init_db()

def get_db():
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    return mysql.connector.connect(**config)

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        
        # Joined string for multi-select
        skills = ", ".join(request.form.getlist("skills"))
        course = ", ".join(request.form.getlist("course"))
        college = request.form.get("college")
        bio = request.form.get("bio")

        if not all([firstname, lastname, username, email, password, role]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users 
                (firstname, lastname, username, email, password, role, skills, course, college, bio) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (firstname, lastname, username, email, hashed_password, role, skills, course, college, bio))
            conn.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as err:
             if err.errno == errorcode.ER_DUP_ENTRY:
                 flash("Username or Email already exists.", "error")
             else:
                 flash(f"Database error: {err}", "error")
        finally:
             if 'cursor' in locals(): cursor.close()
             if 'conn' in locals(): conn.close()
             
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
            user = None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['firstname'] = user['firstname']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
        user = cursor.fetchone()
    except mysql.connector.Error:
        user = None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
    
    if user:
        if user['role'] == 'student':
            return render_template("dashboard_student.html", user=user)
        elif user['role'] == 'mentor':
            return render_template("dashboard_mentor.html", user=user)
        elif user['role'] == 'admin':
            return render_template("dashboard_admin.html", user=user)
    
    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
        user = cursor.fetchone()
    except mysql.connector.Error:
        user = None
    finally:
         if 'cursor' in locals(): cursor.close()
         if 'conn' in locals(): conn.close()
    
    return render_template("profile.html", user=user)

@app.route("/browse")
def browse():
    if "user_id" not in session:
        return redirect(url_for("login"))
        
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, firstname, lastname, role, skills, college FROM users WHERE id != %s", (session["user_id"],))
        users = cursor.fetchall()
    except mysql.connector.Error:
        users = []
    finally:
         if 'cursor' in locals(): cursor.close()
         if 'conn' in locals(): conn.close()
    
    return render_template("browse.html", users=users)

@app.route("/requests")
def request_page():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("requests.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)