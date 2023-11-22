from flask import Flask, render_template, jsonify
from database import load_positions_from_db
from sqlalchemy import text

app = Flask(__name__)


@app.route("/")
def helloWorld():
  positions = load_positions_from_db()
  return render_template('home.html', jobs=positions)


# @app.route("/api/jobs")
# def listjobs():
#   return jsonify(JOBS)

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
