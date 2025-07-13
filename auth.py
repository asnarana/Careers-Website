from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

auth = Blueprint('auth', __name__)
db_connectionstring = os.environ['SECRET_KEY_NCSU']
engine = create_engine(db_connectionstring,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem",
                       }})

Session = sessionmaker(bind=engine)

# signup route for new users. adds this user to db and redirects to login page
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session = Session()
        # Check if user exists
        user_exists = session.query(User).filter_by(username=username).first()
        if user_exists:
            flash('Username already exists.')
            return redirect(url_for('auth.signup'))

        if password is None:
            flash('Password field cannot be empty.')
            return redirect(url_for('auth.signup'))

        # Create new user
        new_user = User(username=username,
                        password=generate_password_hash(password,
                                                        method='sha256'))
        session.add(new_user)
        session.commit()

        return redirect(url_for('auth.login'))
    return render_template('signup.html')

# login route for existing users. checks if user exists and redirects to dashboard
# if admin, redirects to admin dashboard, else if user, redirects to home page where user can apply to positions 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session = Session()
        user = session.query(User).filter_by(username=username).first()
        if user and password is not None \
        and  check_password_hash(str(user.password), password):
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('login.html')
