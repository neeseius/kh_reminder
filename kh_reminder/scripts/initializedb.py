from getpass import getpass
from pysqlcipher3 import dbapi2 as sqlcipher
from sqlalchemy import create_engine, engine_from_config
from pyramid.paster import get_appsettings
from sqlalchemy.orm import scoped_session, sessionmaker
from kh_reminder.models import Base, Signature, Administrator
import os


def main():
    thisdir = os.path.dirname(os.path.abspath(__file__))
    ini = os.path.join(thisdir, os.path.pardir, os.path.pardir, 'production.ini')
    settings = get_appsettings(ini)
    dbpath = settings["database_path"]
    engine = create_engine(dbpath)

    username = input("kh_reminder Administrator Username: ")
    password = getpass("kh_reminder Administrator Temporary Password: ")

    db = sqlcipher.connect(engine.url.database)
    db.executescript("PRAGMA KEY='%s';" % password)
    #db.execute("CREATE TABLE administrator (username text primary key);")
    #db.execute("CREATE TABLE signature (message text primary key);")
    #db.execute(f"INSERT INTO administrator (username) values ('{username}');")
    #db.execute(f"INSERT INTO signature (message) values ('');")
    db.commit()
    db.close()


    engine_object = engine_from_config(settings)
    engine_object.url.password = password
    engine = create_engine(engine_object.url)
    DBSession = scoped_session(sessionmaker())
    DBSession.configure(bind=engine)

    Base.metadata.create_all(engine)

    admin = Administrator(username=username)
    DBSession.add(admin)

    sig = Signature(message = "")
    DBSession.add(sig)

    DBSession.commit()


if __name__ == '__main__':
    main()
