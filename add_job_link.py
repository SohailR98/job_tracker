import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('job_tracker.db')

# Create a cursor object
cursor = conn.cursor()

# Add job_link column to job_applications table
try:
    cursor.execute('''
        ALTER TABLE job_applications ADD COLUMN job_link TEXT NOT NULL
    ''')
    print("job_link column added successfully.")
except sqlite3.OperationalError as e:
    print("Error:", e)

# Commit changes and close connection
conn.commit()
conn.close()