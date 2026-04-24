import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    'user': 'root',
    'password': 'nashra@2025',
    'host': 'localhost',
    'auth_plugin': 'mysql_native_password'
}
DB_NAME = 'skillify'

def get_db():
    config = DB_CONFIG.copy()
    config['database'] = DB_NAME
    return mysql.connector.connect(**config)

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        cursor.execute(f"USE {DB_NAME}")

        # Users table with mentor_type
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firstname VARCHAR(50) NOT NULL,
                lastname VARCHAR(50) NOT NULL,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('student', 'mentor', 'admin') NOT NULL,
                mentor_type VARCHAR(50) DEFAULT NULL,
                skills TEXT,
                course TEXT,
                college VARCHAR(100),
                bio TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                mentor_id INT,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                video_url VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (mentor_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Certificates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                skill VARCHAR(100) NOT NULL,
                issued_by_mentor_id INT,
                issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (issued_by_mentor_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Database error during initialization: {err}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()
