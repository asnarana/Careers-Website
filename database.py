from sqlalchemy import create_engine, text

# setting up connection to mySQL database this database is stored on
# mySQLalchemy server.
db_connectionstring = "mysql+pymysql://xoyjqkx4z1xvgj3gk63b:pscale_pw_njgKUHfcq0uWckHF6y2G8fgxYhrVxpLXRkusIM5dRHn@aws.connect.psdb.cloud/ncsucareers?charset=utf8mb4"
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


# database: ncsucareers
# username: xoyjqkx4z1xvgj3gk63b
# host: aws.connect.psdb.cloud
# password: pscale_pw_njgKUHfcq0uWckHF6y2G8fgxYhrVxpLXRkusIM5dRHn
