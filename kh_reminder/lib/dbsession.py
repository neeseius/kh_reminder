from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from kh_reminder.models import Administrator
from pysqlcipher3 import dbapi2 as sqlcipher


class Session:
    engine = None
    engine_object = None
    status = "sealed"
    DBSession = scoped_session(sessionmaker())

    @classmethod
    def set_engine(cls):
        cls.engine = create_engine(cls.engine_object.url, poolclass=NullPool)

    @classmethod
    def set_dbsession(cls):
        cls.DBSession = scoped_session(sessionmaker())
        cls.DBSession.configure(bind=cls.engine)

    @classmethod
    def rekey_db(cls, username, password):
        cls.DBSession.close()
        db = sqlcipher.connect(cls.engine_object.url.database)
        db.executescript(f"PRAGMA KEY='{cls.engine_object.url.password}';")
        db.executescript(f"PRAGMA REKEY='{password}';")
        db.close()

        cls.status = "sealed"
        cls.authenticate(username, password)

    @classmethod
    def authenticate(cls, username, password):
        engine_object = create_engine(cls.engine_object.url, poolclass=NullPool)
        engine_object.url.password = password
        engine = create_engine(engine_object.url)
        Session = sessionmaker(bind=engine)
        session = Session()

        auth_result = False
        was_sealed = False

        try:
            session.query(Administrator).filter(Administrator.username == username).one()
            auth_result = True

        except Exception as e:
            print("Authentication Failed")
            print(e)

        finally:
            session.close()

        if auth_result is True and cls.status == "sealed":
            was_sealed = True
            cls.engine_object = engine
            cls.set_engine()
            cls.DBSession.close()
            cls.set_dbsession()
            cls.status = "unsealed"

        return auth_result, was_sealed
