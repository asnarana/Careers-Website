# Careers-Website

A web application for managing and applying to student positions at NCSU.

## Features
- User signup and login
- List of available job positions
- Application form with Google reCAPTCHA
- Application status dashboard

## Requirements
- Python 3.10
- MySQL database

## Installation

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd Careers-Website
```

### 2. Install dependencies
You can use either `pip` or `poetry`:

**Using pip:**
```sh
pip install -r requirements.txt
```

**Or using poetry:**
```sh
poetry install
```

### 3. Set environment variables
The app requires the following environment variables:
- `SITE`: Google reCAPTCHA site key
- `SECRET`: Google reCAPTCHA secret key
- `SECRET_KEY_NCSU`: SQLAlchemy connection string for MySQL

Example (Linux/macOS):
```sh
export SITE=your_recaptcha_site_key
export SECRET=your_recaptcha_secret_key
export SECRET_KEY_NCSU="mysql+pymysql://<username>:<password>@<host>/<database>"
```
On Windows (CMD):
```cmd
set SITE=your_recaptcha_site_key
set SECRET=your_recaptcha_secret_key
set SECRET_KEY_NCSU="mysql+pymysql://<username>:<password>@<host>/<database>"
```

**Note:**
- Replace `<username>`, `<password>`, `<host>`, and `<database>` with your actual MySQL credentials and database information.
- The password is the one you set for your MySQL user. It is not provided in this codebase.

#### How to find or set your MySQL password
- If you installed MySQL yourself, use the password you created for your user (often `root`).
- If you are using a managed/cloud MySQL, check your provider's dashboard for credentials.
- If someone else set up the database, ask them for the credentials.
- If you forgot your password, you may need to reset it using MySQL tools. [See MySQL documentation for password reset instructions.](https://dev.mysql.com/doc/refman/8.0/en/resetting-permissions.html)

### 4. Database setup
- Ensure your MySQL database is running and accessible.
- Create the required tables: `users`, `applications`, and `positions`.
- You can use the ORM models in `models.py` to generate the tables automatically:

```python
from models import Base
from database import engine
Base.metadata.create_all(engine)
```

### 5. Run the application
```sh
python app.py
```
The app will be available at [http://localhost:5000](http://localhost:5000).

## License
MIT License
