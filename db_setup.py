import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('job_tracker.db')

# Create a cursor object
cursor = conn.cursor()

# Create Users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

# Create Job Applications table with job_link column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS job_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        company_name TEXT NOT NULL,
        position TEXT NOT NULL,
        application_status TEXT NOT NULL,
        applied_date TEXT NOT NULL,
        job_link TEXT NOT NULL,  -- New column for job link
        timer_end_date TEXT,
        email_sent BOOLEAN DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Create Potential Applications table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS potential_applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        company_name TEXT NOT NULL,
        position TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Create Interview Reports table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS interview_reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        company_name TEXT NOT NULL,
        position TEXT NOT NULL,
        interview_date TEXT,
        feedback TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Commit changes and close connection
conn.commit()
conn.close()
