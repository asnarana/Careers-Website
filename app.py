from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from database import load_positions_from_db, load_position_from_db
from sqlalchemy import create_engine
from models import Application, User
from database import get_sql_session
from werkzeug.security import generate_password_hash, check_password_hash

from auth import auth as auth_blueprint

app = Flask(__name__)
app.register_blueprint(auth_blueprint, url_prefix='/auth')


@app.route("/")
def helloWorld():
  positions = load_positions_from_db()
  return render_template('home.html', jobs=positions)


# creating route to display position descriptions when apply button is pressed
@app.route("/position/<id>")
def show_ncsu_position(id):
  position = load_position_from_db(id)
  if not position:
    return "Position Not Found", 404
  return render_template('positionpage.html', job=position)

# rotue for when user has pressed submit button 
@app.route("/position/<id>/apply", methods=['POST'])
def apply_to_position(id):
  data = request.form
  return jsonify(data)


@app.route("/dashboard")
def dashboard():
  sql_session = get_sql_session(
  )  # Define sql_session within the function scope
  if 'user_id' not in session:
    return redirect(url_for('login'))  # Redirect to login if not logged in
  user_applications = sql_session.query(Application).filter_by(
      user_id=session['user_id']).all()
  return render_template('dashboard.html', applications=user_applications)


@app.route("/login", methods=['GET',
                              'POST'])  # Placeholder for login functionality
def login():
  sql_session = get_sql_session(
  )  # Define sql_session within the login function scope
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    user = sql_session.query(User).filter_by(username=username).first()
    if user is not None and check_password_hash(str(user.password), password):
      # Use check_password_hash function to compare hashed password
      session['user_id'] = user.id
      return redirect(url_for('dashboard'))
    return 'Login Failed'
  return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']

    sql_session = get_sql_session()
    # Check if the user already exists
    existing_user = sql_session.query(User).filter_by(
        username=username).first()
    if existing_user:
      return 'User already exists', 400  # Or handle this with a flash message and redirect

    # Create a new user and hash the password
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(username=username, password=hashed_password)
    sql_session.add(new_user)
    sql_session.commit()
    return redirect(
        url_for('login'))  # Redirect to login after successful registration

  # If it's a GET request, just display the signup form
  return render_template('signup.html')


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
