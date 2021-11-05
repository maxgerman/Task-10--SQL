import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, insert, select, bindparam
from sqlalchemy_utils.functions import database_exists, create_database

import src.data as data

ROLE = 'fox'
PSW = os.getenv('FOXPASS')
DB = 'students'
URL = f'postgresql://{ROLE}:{PSW}@localhost/{DB}'

engine = create_engine(URL, echo=True, future=True)
metadata_obj = MetaData()

group = Table('group', metadata_obj,
              Column('id', Integer, primary_key=True),
              Column('name', String(255), nullable=False, unique=True),
              )

student = Table('student', metadata_obj,
                Column('id', Integer, primary_key=True),
                Column('first_name', String(255), nullable=False),
                Column('last_name', String(255), nullable=False),
                Column('group', ForeignKey('group.id'), nullable=False)
                )

course = Table('course', metadata_obj,
               Column('id', Integer, primary_key=True),
               Column('name', String(255), nullable=False, unique=True),
               Column('description', String, nullable=False),
               )

student_course = Table('student_course', metadata_obj,
                       Column('id', Integer, primary_key=True),
                       Column('student', ForeignKey('student.id'), nullable=False),
                       Column('course', ForeignKey('course.id'), nullable=False)
                       )


def create_params_for_student_course():
    """Return params for student-course many-to-many relation for executemany insertion.
    Every student will have varying number of rows (courses)"""

    student_courses = data.generate_student_courses()

    with engine.connect() as conn:
        student_ids = conn.execute(select(student.c.id)).all()

    return [{'student': id[0], 'course': c} for id, courses in zip(student_ids, student_courses) for c in courses]


def insert_initial_data():
    metadata_obj.drop_all(engine, checkfirst=True)
    metadata_obj.create_all(engine)

    groups_dic = data.assign_students_to_groups(data.generate_students(200), data.generate_groups(10))

    insert_groups = insert(group), [{'name': g} for g in groups_dic]
    insert_courses = insert(course), \
                     [{'name': c,
                       'description': f'Everything there is to know about {c.capitalize()}'}
                      for c in data.COURSES]

    scalar_subq = select(group.c.id).where(group.c.name == bindparam('group_name')).scalar_subquery()
    insert_students = insert(student).values(group=scalar_subq), \
                      [{'first_name': s[0], 'last_name': s[1], 'group_name': g} for g in groups_dic for s in
                       groups_dic[g]]

    with engine.connect() as conn:
        conn.execute(*insert_groups)
        conn.execute(*insert_courses)
        conn.execute(*insert_students)
        conn.commit()
        insert_student_courses = insert(student_course), create_params_for_student_course()
        conn.execute(*insert_student_courses)
        conn.commit()
