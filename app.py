from flask import Flask, render_template, jsonify, request
from database import load_positions_from_db, load_position_from_db
from sqlalchemy import text

app = Flask(__name__)


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
  return  render_template('positionpage.html', job=position)
  
@app.route("/position/<id>/apply")
def apply_to_position(id):
  data = request.args
  return jsonify(data)
  
  

if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)



  
