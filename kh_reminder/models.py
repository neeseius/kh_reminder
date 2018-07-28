from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, collate
from sqlalchemy.orm import scoped_session, sessionmaker
from pyramid.security import Allow


DBSession = scoped_session(sessionmaker())
Base = declarative_base()

class Attendant(Base):
    __tablename__ = 'attendants'
    id = Column(Integer, nullable=False, primary_key=True)
    fname = Column(Text, nullable=False)
    lname = Column(Text, nullable=False)
    email = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    send_email = Column(Integer, nullable=False)
    send_sms = Column(Integer, nullable=False)

    def __init__(self, fname, lname, email='', phone='', send_email=0, send_sms=0):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.phone = phone
        self.send_email = send_email
        self.send_sms = send_sms

class RootFactory(object):
    __acl__ = [ (Allow, 'group:edit', 'edit') ]
    def __init__(self, request):
        pass
