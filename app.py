import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import mysql.connector

from db import init_db, get_db

app = Flask(__name__)
app.secret_key = "skillify_premium_secret"

UPLOAD_FOLDER = 'static/uploads/videos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Database on Startup
init_db()

# --- HELPER ROUTE FOR DB QUERIES ---
def execute_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        if commit: conn.commit()
        if fetchone: return cursor.fetchone()
        if fetchall: return cursor.fetchall()
        return True
    except mysql.connector.Error as err:
        flash(f"Database Error: {err}", "error")
        return None
    finally:
         if 'cursor' in locals(): cursor.close()
         if 'conn' in locals(): conn.close()

# --- MAIN ROUTES ---
@app.route("/")
def home():
    if "user_id" in session: return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/explore")
def explore():
    return render_template("explore.html")

# --- AUTHENTICATION ROUTES ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = request.form
        skills = ", ".join(data.getlist("skills"))
        course = ", ".join(data.getlist("course"))
        mentor_type = data.get("mentor_type", None)
        
        if not all([data.get("firstname"), data.get("email"), data.get("password")]):
            flash("Please fill in required fields.", "error")
            return redirect(url_for('signup'))
            
        hashed_pw = generate_password_hash(data.get("password"))
        query = '''INSERT INTO users (firstname, lastname, username, email, password, role, mentor_type, skills, course, college, bio) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        params = (data.get("firstname"), data.get("lastname"), data.get("username"), data.get("email"), 
                  hashed_pw, data.get("role"), mentor_type, skills, course, data.get("college"), data.get("bio"))
        
        if execute_query(query, params, commit=True):
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
            
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = execute_query("SELECT * FROM users WHERE email=%s", (request.form.get("email"),), fetchone=True)
        if user and check_password_hash(user['password'], request.form.get("password")):
            session.update({'user_id': user['id'], 'username': user['username'], 'role': user['role'], 'firstname': user['firstname']})
            return redirect(url_for('dashboard'))
        flash("Invalid username or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DASHBOARD & PROFILE ---
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session: return redirect(url_for("login"))
    user = execute_query("SELECT * FROM users WHERE id=%s", (session["user_id"],), fetchone=True)
    if user:
        if user['role'] == 'student':
            certs = execute_query("SELECT * FROM certificates WHERE student_id=%s", (user['id'],), fetchall=True)
            return render_template("dashboard_student.html", user=user, certs=certs)
        elif user['role'] == 'mentor':
            videos = execute_query("SELECT * FROM videos WHERE mentor_id=%s", (user['id'],), fetchall=True)
            return render_template("dashboard_mentor.html", user=user, videos=videos)
        elif user['role'] == 'admin':
            return render_template("dashboard_admin.html", user=user)
    return redirect(url_for("home"))

@app.route("/profile")
def profile():
    if "user_id" not in session: return redirect(url_for("login"))
    user = execute_query("SELECT * FROM users WHERE id=%s", (session["user_id"],), fetchone=True)
    return render_template("profile.html", user=user)

@app.route("/browse")
def browse():
    if "user_id" not in session: return redirect(url_for("login"))
    users = execute_query("SELECT id, firstname, lastname, role, mentor_type, skills, college FROM users WHERE id!=%s", (session["user_id"],), fetchall=True)
    return render_template("browse.html", users=users)

@app.route("/requests")
def request_page():
    if "user_id" not in session: return redirect(url_for("login"))
    return render_template("requests.html")

# --- NEW FEATURES: VIDEOS & CERTIFICATES ---
@app.route("/videos", methods=["GET", "POST"])
def videos_page():
    if "user_id" not in session: return redirect(url_for("login"))
    
    if request.method == "POST" and session.get("role") == "mentor":
        title = request.form.get("title")
        desc = request.form.get("description")
        file = request.files.get("video_file")
        url = request.form.get("video_url")
        video_path = url
        
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            video_path = f"/static/uploads/videos/{filename}"
            
        execute_query("INSERT INTO videos (mentor_id, title, description, video_url) VALUES (%s, %s, %s, %s)",
                      (session["user_id"], title, desc, video_path), commit=True)
        flash("Video uploaded successfully!", "success")
        return redirect(url_for("videos_page"))
        
    all_videos = execute_query("SELECT v.*, u.firstname, u.lastname FROM videos v JOIN users u ON v.mentor_id=u.id ORDER BY v.created_at DESC", fetchall=True)
    return render_template("videos.html", videos=all_videos)

@app.route("/issue_certificate", methods=["POST"])
def issue_certificate():
    if session.get("role") != "mentor": return redirect(url_for("dashboard"))
    student_id = request.form.get("student_id")
    skill = request.form.get("skill")
    execute_query("INSERT INTO certificates (student_id, skill, issued_by_mentor_id) VALUES (%s, %s, %s)",
                  (student_id, skill, session["user_id"]), commit=True)
    flash("Certificate issued successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/certificate/<int:cert_id>")
def view_certificate(cert_id):
    query = """SELECT c.*, s.firstname as s_first, s.lastname as s_last, m.firstname as m_first, m.lastname as m_last 
               FROM certificates c 
               JOIN users s ON c.student_id = s.id 
               LEFT JOIN users m ON c.issued_by_mentor_id = m.id WHERE c.id=%s"""
    cert = execute_query(query, (cert_id,), fetchone=True)
    if cert:
        return render_template("certificate.html", cert=cert)
    flash("Certificate not found", "error")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(debug=True)