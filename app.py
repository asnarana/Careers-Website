from dotenv import load_dotenv
load_dotenv()
import os
import requests  # For sending HTTP requests to verify reCAPTCHA
from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from database import load_positions_from_db, load_position_from_db, get_sql_session

app = Flask(__name__)
# Correct: key_func is set only once during initialization

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


@app.route("/")
def home():
  """
    Home route that displays a list of job positions.
    """
  positions = load_positions_from_db()
  return render_template('home.html', jobs=positions)


@app.route("/position/<id>")
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

  # Basic validation to ensure required fields are filled
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

  # Save the application to the database using raw SQL
  sql_session = get_sql_session()
  try:
    # Prepare the SQL statement with parameterized queries to prevent SQL injection
    insert_query = text("""
            INSERT INTO applications (position_id, fullname, email, linkedin, education, work_experience, resume_link)
            VALUES (:position_id, :fullname, :email, :linkedin, :education, :work_experience, :resume_link)
        """)
    sql_session.execute(
        insert_query, {
            'position_id': id,
            'fullname': fullname,
            'email': email,
            'linkedin': link,
            'education': education,
            'work_experience': work,
            'resume_link': resume_link
        })
    sql_session.commit()
  except Exception as e:
    # Handle any database-related errors
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

  # If everything is successful, render the form with a success message
  message = {
      'text': 'Your application has been submitted successfully!',
      'category': 'success'
  }
  position = load_position_from_db(id)
  return render_template('positionpage.html',
                         job=position,
                         recaptcha_site_key=site_key,
                         message=message)


if __name__ == "__main__":
  # Run the Flask application
  app.run(host='0.0.0.0', debug=True)
