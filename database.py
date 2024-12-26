from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
# setting up connection to mySQL database this database is stored on
# mySQLalchemy server.
db_connectionstring = os.environ['SECRET_KEY_NCSU']
engine = create_engine(db_connectionstring,
                       connect_args={"ssl": {
                           "ssl_ca": "/etc/ssl/cert.pem",
                       }})

Session = sessionmaker(bind=engine)


def get_sql_session():

  return Session()


def load_positions_from_db():
  session = get_sql_session()
  try:
    #text to prevent sql injection - safely creates a textual sql query
    result = session.execute(text("select * from positions"))
    positions = [dict(zip(result.keys(), row)) for row in result.fetchall()]
    return positions
  except Exception as e:
    print(f"Error accessing database: {e}")
    return []
  finally:
    session.close()


def load_position_from_db(id):
  session = get_sql_session()
  try:
    result = session.execute(text("SELECT * FROM positions WHERE id = :val"),
                             {'val': id})
    row = result.fetchone()
    return dict(zip(result.keys(), row)) if row else None
  except Exception as e:
    print(f"Error accessing database: {e}")
    return None
  finally:
    session.close()
