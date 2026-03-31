from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'skillify_super_secret_key'

def init_db():
    """Initializes the database and the required tables if they don't exist."""
    print("Attempting to connect to MySQL Server to initialize database...")
    try:
        # Connect to MySQL Server (without specifying a DB first)
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nashra@2025"
        )
        cursor = conn.cursor()
        
        # Create the skillify database
        cursor.execute("CREATE DATABASE IF NOT EXISTS skillify")
        conn.commit()
        cursor.close()
        conn.close()
        
        # Reconnect to the specifically created database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="nashra@2025",
            database="skillify"
        )
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(100) NOT NULL,
                lastname VARCHAR(100) NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                email VARCHAR(150) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                skills TEXT,
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and 'users' table initialized successfully.")
    except Exception as e:
        print("Error initializing database:", e)

# Call initialization on startup
init_db()

def get_db():
    """Helper function to get a database connection."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="nashra@2025",
        database="skillify"
    )

# HOME / LANDING PAGE
@app.route('/')
def home():
    return render_template('index.html')

# SIGNUP
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']
            
            # Additional fields depending on role, join them into JSON/text or simple string
            skills = request.form.get('skills', '')
            bio = request.form.get('bio', '')
            admin_code = request.form.get('admin_code', '')
            
            # Example logic for admin validation
            if role == 'admin' and admin_code != 'SECRET2025':
                flash("Invalid admin code provided.", "error")
                return redirect(url_for('signup'))
            
            # Hash password for safety
            hashed_pw = generate_password_hash(password)
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("SELECT * FROM users WHERE email=%s OR username=%s", (email, username))
            if cursor.fetchone():
                flash("Email or Username already exists.", "error")
                return redirect(url_for('signup'))
            
            cursor.execute(
                "INSERT INTO users (firstname, lastname, username, email, password, role, skills, bio) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (firstname, lastname, username, email, hashed_pw, role, skills, bio)
            )
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Signup error: {e}")
            flash(f"An error occurred during signup: {str(e)}", "error")
            return redirect(url_for('signup'))

    return render_template('signup.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                # Setup session
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                
                # Role-based redirect
                if user['role'] == 'student':
                    return redirect(url_for('dashboard_student'))
                elif user['role'] == 'mentor':
                    return redirect(url_for('dashboard_mentor'))
                elif user['role'] == 'admin':
                    return redirect(url_for('dashboard_admin'))
                else:
                    return redirect(url_for('dashboard_student'))
                    
            else:
                flash("Invalid credentials. Please try again.", "error")
        except Exception as e:
            print("Login error:", e)
            flash("Database connection error.", "error")
            
    return render_template('login.html')

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('home'))

# DASHBOARDS
@app.route('/dashboard/student')
def dashboard_student():
    if 'user_id' not in session or session.get('role') != 'student':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    return render_template('dashboard_student.html')

@app.route('/dashboard/mentor')
def dashboard_mentor():
    if 'user_id' not in session or session.get('role') != 'mentor':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
    return render_template('dashboard_mentor.html')

@app.route('/dashboard/admin')
def dashboard_admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Unauthorized access.", "error")
        return redirect(url_for('login'))
        
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, firstname, lastname, username, email, role, created_at FROM users")
        all_users = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Admin user fetch error:", e)
        all_users = []
        
    return render_template('dashboard_admin.html', users=all_users)

# EXPLORE
@app.route('/explore')
def explore():
    return render_template('explore.html')

# PROFILE
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Profile fetch error:", e)
        user_data = None
        
    return render_template('profile.html', user=user_data)

# REQUESTS
@app.route('/requests')
def requests_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('requests.html')


if __name__ == '__main__':
    app.run(debug=True)