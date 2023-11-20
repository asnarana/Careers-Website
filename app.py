from flask import Flask, render_template, jsonify

app = Flask(__name__)

JOBS = [
    {
        'id': 1,
        'title': '1887 Bistro Busser/Dishwasher',
        'location': 'Raleigh,NC',
        'Department': 'NC State Dining',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 2,
        'title': 'Café and Market Student Manager',
        'location': 'Raleigh,NC',
        'Department': 'NC State Dining',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 3,
        'title': 'Information Assistant',
        'location': 'Raleigh,NC',
        'Department': 'Campus Enterprises Administration',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 4,
        'title': 'Digital Multimedia Assistant',
        'location': 'Raleigh,NC',
        'Department': 'NC State Student Centers',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 5,
        'title': 'Gameday Operations Associate',
        'location': 'Raleigh,NC',
        'Department': 'WolfPack Outfitters/NC State Bookstore',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 6,
        'title': 'Setup Assistant',
        'location': 'Raleigh,NC',
        'Department': 'NC State Student Centers',
        'salary': '$10/hr with yearly bonus'
    },
    {
        'id': 7,
        'title': 'Social Media Content Creation Team',
        'location': 'Raleigh,NC',
        'Department': 'Campus Enterprises Administration',
        'salary': '$10/hr with yearly bonus'
    },
]


@app.route("/")
def helloWorld():
  return render_template('home.html', jobs=JOBS)


app.route("/api/jobs")


def listjobs():
  return jsonify(JOBS)


if __name__ == "__main__":
  app.run(host='0.0.0.0', debug=True)
