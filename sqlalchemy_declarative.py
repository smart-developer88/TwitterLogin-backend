import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from dataclasses import dataclass
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
# from flask_marshmallow import Marshmallow

Base = declarative_base()

class Group(Base):
    __tablename__ = 'group'
    # Here we define columns for the table person
    # Notice that each column is also a normal Python instance attribute.
    id = int
    name = str
    owner = str
    retweet_all = int
    like_all = int
    follow_all = int

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(250), nullable=False)
    owner = Column(String(250), nullable=False)
    retweet_all = Column(Integer(), nullable=False)
    like_all = Column(Integer(), nullable=False)
    follow_all = Column(Integer(), nullable=False)

class GroupSchema(SQLAlchemySchema):
    class Meta:
        model = Group
        load_instance = True  # Optional: deserialize to model instances

    id = auto_field()
    name = auto_field()
    owner = auto_field()
    retweet_all = auto_field()
    like_all = auto_field()
    follow_all = auto_field()

class User(Base):
    __tablename__ = 'users'
    # Here we define columns for the table address.
    # Notice that each column is also a normal Python instance attribute.
    id = int
    username = str
    oauth_token = str
    oauth_secret = str
    email = str

    id = Column(String(250), primary_key=True)
    username = Column(String(250), nullable=False)
    oauth_token = Column(String(250), nullable=False)
    oauth_secret = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    groups = relationship("GroupMembership")

class GroupMembership(Base):
    __tablename__ = 'group_membership'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("User")

# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('sqlite:///sqlalchemy_example.db')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)