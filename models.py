import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy_utils.functions import database_exists, create_database

ROLE = 'fox'
PSW = os.getenv('FOXPASS')
DB = 'students'
URL = f'postgresql://{ROLE}:{PSW}@localhost/{DB}'

engine = create_engine(URL, echo=True, future=True)
metadata_obj = MetaData()

group = Table('group', metadata_obj,
              Column('id', Integer, primary_key=True),
              Column('name', String(255), nullable=False),
              )

student = Table('student', metadata_obj,
                Column('id', Integer, primary_key=True),
                Column('first_name', String(255), nullable=False),
                Column('last_name', String(255), nullable=False),
                Column('group', ForeignKey('group.id'), nullable=True)
                )

course = Table('course', metadata_obj,
               Column('id', Integer, primary_key=True),
               Column('name', String(255), nullable=False),
               Column('description', String, nullable=False),
               )

student_course = Table('student_course', metadata_obj,
                       Column('id', Integer, primary_key=True),
                       Column('student', ForeignKey('student.id'), nullable=False),
                       Column('course', ForeignKey('course.id'), nullable=False)
                       )


if not database_exists(URL):
    metadata_obj.create_all(engine)
