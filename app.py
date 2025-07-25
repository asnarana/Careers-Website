from dotenv import load_dotenv
load_dotenv()
import os
import requests  # For sending HTTP requests to verify reCAPTCHA
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from database import load_positions_from_db, load_position_from_db, get_sql_session

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'devsecret')

# Add debugging for environment variables
try:
    site_key = os.environ['SITE']
    secret_key = os.environ['SECRET']
    print(f"reCAPTCHA Site Key loaded: {site_key[:10]}...")  # Show first 10 chars for debugging
    print(f"reCAPTCHA Secret Key loaded: {secret_key[:10]}...")  # Show first 10 chars for debugging
except KeyError as e:
    print(f"ERROR: Missing environment variable: {e}")
    print("Make sure your .env file contains SITE and SECRET variables")
    site_key = "missing_site_key"
    secret_key = "missing_secret_key"

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"  # Google reCAPTCHA verification URL
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

# Helper: login required decorator
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session and 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get('success')
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        is_admin = request.form.get("is_admin") == "on"
        if is_admin:
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session.clear()
                session['admin'] = True
                return redirect(url_for('admin_dashboard'))
            else:
                return render_template("login.html", error="Invalid admin credentials.", success=success)
        else:
            from models import User
            from sqlalchemy.orm import sessionmaker
            from sqlalchemy import create_engine
            db_connectionstring = os.environ['SECRET_KEY_NCSU']
            engine = create_engine(db_connectionstring, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
            Session = sessionmaker(bind=engine)
            dbsession = Session()
            user = dbsession.query(User).filter_by(username=username).first()
            from werkzeug.security import check_password_hash
            if user and check_password_hash(user.password, password):
                session.clear()
                session['user'] = user.username
                return redirect(url_for('home'))
            else:
                return render_template("login.html", error="Invalid user credentials.", success=success)
    return render_template("login.html", error=None, success=success)

@app.route("/signup", methods=["GET", "POST"])
def signup():
    success = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USERNAME:
            return render_template("signup.html", error="Not allowed. Only login as admin.", success=success)
        from models import User
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        db_connectionstring = os.environ['SECRET_KEY_NCSU']
        engine = create_engine(db_connectionstring, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
        Session = sessionmaker(bind=engine)
        dbsession = Session()
        user_exists = dbsession.query(User).filter_by(username=username).first()
        if user_exists:
            return render_template("signup.html", error="Username already exists.", success=success)
        from werkzeug.security import generate_password_hash
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        dbsession.add(new_user)
        dbsession.commit()
        # Show success message on login page
        return redirect(url_for('login', success='Account created successfully! Please log in.'))
    return render_template("signup.html", error=None, success=success)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
@login_required
def home():
  """
    Home route that displays a list of job positions.
    """
  positions = load_positions_from_db()
  return render_template('home.html', jobs=positions)


@app.route("/position/<id>")
@login_required
def show_position(id):
  """
    Route to display the application form for a specific job position.
    
    Parameters:
    - id (int): The ID of the job position.
    """
  position = load_position_from_db(id)
  if not position:
    return "Position Not Found", 404
  return render_template('positionpage.html',
                         job=position,
                         recaptcha_site_key=site_key,
                         message=None)


@app.route("/position/<id>/apply", methods=['POST'])
@login_required
def apply_to_position(id):
  honeypot = request.form.get('honeypot')
  if honeypot:
    message = {
        'text': 'Spam detected. Your application could not be processed.',
        'category': 'danger'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  recaptcha_response = request.form.get('g-recaptcha-response')

  if not recaptcha_response:
    message = {
        'text': 'Please complete the reCAPTCHA challenge.',
        'category': 'warning'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  data = {
      'secret': secret_key, 
      'response': recaptcha_response,  
      'remoteip': request.remote_addr  
  }

  try:
    verification_response = requests.post(RECAPTCHA_VERIFY_URL, data=data)
    verification_result = verification_response.json()
    print(f"reCAPTCHA verification result: {verification_result}")  # Debug output
  except requests.exceptions.RequestException as e:
    print(f"reCAPTCHA request error: {e}")  # Debug output
    message = {
        'text': 'Error verifying reCAPTCHA. Please try again.',
        'category': 'danger'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  if not verification_result.get('success'):
    print(f"reCAPTCHA verification failed: {verification_result}")  # Debug output
    message = {
        'text': 'reCAPTCHA verification failed. Please try again.',
        'category': 'danger'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  # Extract form data
  fullname = request.form.get('fullname')
  email = request.form.get('email')
  link = request.form.get('link')
  education = request.form.get('education')
  work = request.form.get('work')
  resume_link = request.form.get('resume_link')

  # basic validation to ensure required fields are filled
  if not all([fullname, email, education, work, resume_link]):
    message = {
        'text': 'Please fill out all required fields.',
        'category': 'warning'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  # Get user_id if logged in as user
  user_id = None
  if 'user' in session:
    from models import User
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    db_connectionstring = os.environ['SECRET_KEY_NCSU']
    engine = create_engine(db_connectionstring, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
    Session = sessionmaker(bind=engine)
    dbsession = Session()
    user = dbsession.query(User).filter_by(username=session['user']).first()
    if user:
        user_id = user.id

  # Check for existing application
  existing_app = None
  if user_id:
    sql_session = get_sql_session()
    existing_app = sql_session.execute(
        text("SELECT * FROM applications WHERE user_id = :user_id AND position_id = :position_id"),
        {'user_id': user_id, 'position_id': id}
    ).fetchone()
  else:
    existing_app = sql_session.execute(
        text("SELECT * FROM applications WHERE email = :email AND position_id = :position_id"),
        {'email': email, 'position_id': id}
    ).fetchone()

  if existing_app:
    message = {
        'text': 'You have already applied for this position.',
        'category': 'warning'
    }
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)

  # save the application to the database using raw SQL
  sql_session = get_sql_session()
  try:
    insert_query = text("""
            INSERT INTO applications (position_id, fullname, email, linkedin, education, work_experience, resume_link, user_id)
            VALUES (:position_id, :fullname, :email, :linkedin, :education, :work_experience, :resume_link, :user_id)
        """)
    sql_session.execute(
        insert_query, {
            'position_id': id,
            'fullname': fullname,
            'email': email,
            'linkedin': link,
            'education': education,
            'work_experience': work,
            'resume_link': resume_link,
            'user_id': user_id
        })
    sql_session.commit()
  except Exception as e:
    print(f"Database Error: {e}")  # Log the error for debugging
    message = {
        'text':
        'An error occurred while submitting your application. Please try again.',
        'category': 'danger'
    }
    sql_session.rollback()
    position = load_position_from_db(id)
    return render_template('positionpage.html',
                           job=position,
                           recaptcha_site_key=site_key,
                           message=message)
  finally:
    sql_session.close()

  # if everything is successful, render the form with a success message
  message = {
      'text': 'Your application has been submitted successfully!',
      'category': 'success'
  }
  position = load_position_from_db(id)
  return render_template('positionpage.html',
                         job=position,
                         recaptcha_site_key=site_key,
                         message=message)
# the route for admin dashboard
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine, text
    db_connectionstring = os.environ['SECRET_KEY_NCSU']
    engine = create_engine(db_connectionstring, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
    Session = sessionmaker(bind=engine)
    dbsession = Session()
    applications = dbsession.execute(text("""
        SELECT applications.*, users.username 
        FROM applications 
        LEFT JOIN users ON applications.user_id = users.id
    """)).mappings().all()
    positions = {p['id']: p['title'] for p in dbsession.execute(text("SELECT id, title FROM positions")).mappings().all()}
    return render_template("admin_dashboard.html", applications=applications, positions=positions)

if __name__ == "__main__":
  # Run the Flask application
  app.run(host='0.0.0.0', debug=True)
