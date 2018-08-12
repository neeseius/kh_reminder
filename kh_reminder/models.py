from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Text, Integer, Date, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from pyramid.security import Allow


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

    @hybrid_property
    def fullname(self):
        return self.fname + " " + self.lname


class Meeting(Base):
    __tablename__ = 'meetings'
    id = Column(Integer, nullable=False, primary_key=True)
    date = Column(Date, nullable=False)
    meeting_type = Column(Text, nullable=False)
    assignment_types = Column(Text, nullable=False)
    assignments = relationship("Assignment")

    def __init__(self, date, meeting_type, assignment_types):
        self.date = date
        self.meeting_type = meeting_type
        self.assignment_types = assignment_types


class Assignment(Base):
    __tablename__ = 'assignments'
    id = Column(Integer, nullable=False, primary_key=True)
    assignment_type = Column(Text, nullable=False)
    attendant = Column(Text, nullable=False)
    meeting_id = Column(Integer, ForeignKey('meetings.id'))

    def __init__(self,assignment_type, attendant):
        self.assignment_type = assignment_type
        self.attendant = attendant


class Administrator(Base):
    __tablename__ = 'administrator'
    username = Column(Text, nullable=False, primary_key=True)

    def __init__(self, username):
        self.username = username


class RootFactory(object):
    __acl__ = [(Allow, 'group:edit', 'edit')]

    def __init__(self, request):
        pass
