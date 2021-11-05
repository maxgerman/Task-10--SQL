import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, insert, select, bindparam, \
    func, desc, delete
from sqlalchemy.schema import UniqueConstraint
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
                       Column('course', ForeignKey('course.id'), nullable=False),
                       UniqueConstraint('student', 'course'),
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


def find_groups_with_less_or_equal_students(n=20) -> list:
    count = func.count('student.c.id').label('count')
    s = select(group.c.name, count).join(student).group_by(group.c.name).order_by(desc('count')).having(count <= n)
    with engine.connect() as conn:
        res = conn.execute(s)
    return res.all()


def find_students_from_course(course_name) -> list:
    """Returns a list of student names with a given course name (case insensitive and substring-searching)"""
    s = select(student.c.first_name, student.c.last_name, course.c.name) \
        .join(student_course, student.c.id == student_course.c.student) \
        .join(course, student_course.c.course == course.c.id).where(course.c.name.ilike(f'%{course_name}%')).order_by(
        course.c.name)
    with engine.connect() as conn:
        res = conn.execute(s)
    return res.all()


def add_student(first_name, last_name, group_id) -> tuple:
    """Adds a student to the db and returns its id"""
    if not all((isinstance(first_name, str), isinstance(last_name, str), isinstance(group_id, int))):
        return ValueError
    with engine.connect() as conn:
        res = conn.execute(insert(student), {'first_name': first_name, 'last_name': last_name, 'group': group_id})
        conn.commit()
    return res.inserted_primary_key


def delete_student(student_id):
    with engine.connect() as conn:
        res = conn.execute(delete(student).where(student.c.id == student_id))
        conn.commit()
    return res.rowcount


def add_student_to_course(full_name, course_name):
    """Add a student to the course given their full name and course name (case insensitive)"""
    first_name, last_name = full_name.split()
    student_id_subq = select(student.c.id) \
        .where(student.c.first_name.ilike(first_name)) \
        .where(student.c.last_name.ilike(last_name)).scalar_subquery()
    course_subq = select(course.c.id).where(course.c.name.ilike(course_name)).scalar_subquery()
    insert_stmt = insert(student_course).values(student=student_id_subq, course=course_subq)
    with engine.connect() as conn:
        res = conn.execute(insert_stmt)
        conn.commit()
    return res.inserted_primary_key


def remove_student_from_course(student_id, course_id):
    del_stmt = delete(student_course) \
        .where(student_course.c.student == student_id) \
        .where(student_course.c.course == course_id)
    with engine.connect() as conn:
        res = conn.execute(del_stmt)
        conn.commit()
    return res.rowcount
