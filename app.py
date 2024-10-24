from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime, timedelta 

app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class to work with Flask-Login
class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], email=user[1])
    return None

@app.route('/')
def home():
    return '''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Job Tracker Home</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css" />
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">

            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    background-color: #f4f4f4;
                }
                .container {
                    text-align: center;
                    background: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                }
                h1 {
                    color: #333;
                    animation: fadeInDown 1s; /* Custom animation for the heading */
                }
                p {
                    color: #666;
                    animation: fadeInUp 1s; /* Custom animation for the paragraph */
                }
                .btn {
                    display: inline-block;
                    padding: 10px 20px;
                    margin: 10px 0;
                    border: none;
                    border-radius: 5px;
                    background-color: #007BFF;
                    color: #fff;
                    cursor: pointer;
                    text-decoration: none;
                    animation: fadeIn 1s; /* Fade-in animation for the button */
                }
                .btn:hover {
                    background-color: #0056b3;
                }
                .social-icons {
                    display: flex;
                    justify-content: center;
                    margin-top: 20px;
                }
                .social-icon {
                    font-size: 24px; /* Icon size */
                    color: #007BFF; /* Icon color */
                    margin: 0 15px; /* Space between icons */
                    transition: color 0.3s; /* Smooth color transition */
                }
                .social-icon:hover {
                    color: #0056b3; /* Color change on hover */
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="animate__animated animate__fadeInDown">Welcome to the Job Application Tracker</h1>
                <p class="animate__animated animate__fadeInUp">Made By Sohail Rashed</p>
                <div class="animate__animated animate__fadeInUp">
                <div class="social-icons">
                    <a href="https://www.instagram.com/sohail_d.rashed/" target="_blank" class="social-icon">
                        <i class="fab fa-instagram"></i>
                    </a>
                    <a href="https://github.com/SohailR98" target="_blank" class="social-icon">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="https://www.facebook.com/sohail.rashed.9/" target="_blank" class="social-icon">
                        <i class="fab fa-facebook"></i>
                    </a>
                </div>
                </div>
                <p class="animate__animated animate__fadeInUp">Track your job applications efficiently and stay organized.</p>
                <p>
                    <a class="btn animate__animated animate__fadeIn" href="/login">Login</a>
                    or 
                    <a class="btn animate__animated animate__fadeIn" href="/register">Register</a>
                    to start tracking your job applications.
                </p>
            </div>
        </body>
        </html>
    '''



# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to SQLite and insert new user
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()

        # Check if the email is already registered
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('Email already registered')
        else:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        
        conn.close()
    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to SQLite and verify user
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        
        if user and user[1] == password:
            user_obj = User(id=user[0], email=email)
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password')
        
        conn.close()
    return render_template('login.html')

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if request.method == 'POST':
        company_name = request.form['company_name']
        position = request.form['position']
        status = request.form['status']
        applied_date = request.form['applied_date']
        job_link = request.form['job_link']  # New field for job link

        # Ensure applied_date is in 'YYYY-MM-DD' format and convert to 'YYYY-MM-DD HH:MM:SS'
        try:
            applied_date = datetime.strptime(applied_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.')
            return redirect(url_for('add_job'))

        # Insert new job application into the database
        conn = sqlite3.connect('job_tracker.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO job_applications (user_id, company_name, position, application_status, applied_date, job_link)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (current_user.id, company_name, position, status, applied_date, job_link))
        conn.commit()
        conn.close()

        flash('Job application added successfully')
        return redirect(url_for('dashboard'))
    return render_template('add_job.html')

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        company_name = request.form['company_name']
        position = request.form['position']
        status = request.form['status']
        applied_date = request.form['applied_date']
        job_link = request.form['job_link']  # New field for job link

        # Update job application
        cursor.execute("""
            UPDATE job_applications
            SET company_name = ?, position = ?, application_status = ?, applied_date = ?, job_link = ?
            WHERE id = ? AND user_id = ?
        """, (company_name, position, status, applied_date, job_link, job_id, current_user.id))
        conn.commit()
        conn.close()

        flash('Job application updated successfully')
        return redirect(url_for('dashboard'))

    # Retrieve job details to edit
    cursor.execute("SELECT * FROM job_applications WHERE id = ? AND user_id = ?", (job_id, current_user.id))
    job = cursor.fetchone()
    conn.close()

    return render_template('edit_job.html', job=job)

@app.route('/delete_job/<int:job_id>', methods=['POST'])
@login_required
def delete_job(job_id):
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM job_applications WHERE id = ? AND user_id = ?", (job_id, current_user.id))
    conn.commit()
    conn.close()

    flash('Job application deleted successfully')
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM job_applications WHERE user_id = ?", (current_user.id,))
    jobs = cursor.fetchall()
    conn.close()

   # Calculate timer_end_date dynamically and prepare job data for rendering
    updated_jobs = []
    for job in jobs:
        job = list(job)  # Convert tuple to list to allow modification
        job_id, user_id, company_name, position, application_status, applied_date, job_link, email_sent = job
        
        # Calculate timer_end_date dynamically
        applied_date_dt = datetime.strptime(applied_date, "%Y-%m-%d %H:%M:%S")
        timer_end_date_dt = applied_date_dt + timedelta(days=30)
        timer_end_date = timer_end_date_dt.strftime("%Y-%m-%d")
        
        updated_jobs.append((job_id, user_id, company_name, position, application_status, applied_date, job_link, timer_end_date, email_sent))
    
    return render_template('dashboard.html', jobs=updated_jobs)

@app.route('/update_email_sent/<int:job_id>', methods=['POST'])
@login_required
def update_email_sent(job_id):
    email_sent = int(request.form.get('email_sent', 0))
    
    conn = sqlite3.connect('job_tracker.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE job_applications SET email_sent = ? WHERE id = ? AND user_id = ?", (email_sent, job_id, current_user.id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
