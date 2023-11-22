from sqlalchemy import create_engine, text
import os
# setting up connection to mySQL database this database is stored on
# mySQLalchemy server.
db_connectionstring = os.environ['SECRET_KEY']
engine = create_engine(db_connectionstring,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem",
                       }})


def load_positions_from_db():
  with engine.connect() as conn:
    result = conn.execute(text("select * from positions"))

    ncsupositions = [
        dict(zip(result.keys(), row, strict=False))
        for row in result.fetchall()
    ]
    return ncsupositions
