"""
Interaction with database. Postgres must be up, ROLE created and granted privileges to create databases.
ROLE password (PSW) must be set (env variable).
Another db will be used for tests (with prefix test_)
"""

import os

from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    ForeignKey,
    insert,
    select,
    bindparam,
    func,
    desc,
    delete
)
from sqlalchemy.schema import UniqueConstraint

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
                Column('group', ForeignKey('group.id'), nullable=False),
                )

course = Table('course', metadata_obj,
               Column('id', Integer, primary_key=True),
               Column('name', String(255), nullable=False, unique=True),
               Column('description', String, nullable=False),
               )

student_course = Table('student_course', metadata_obj,
                       Column('id', Integer, primary_key=True),
                       Column('student', ForeignKey('student.id', ondelete='CASCADE'), nullable=False),
                       Column('course', ForeignKey('course.id', ondelete='CASCADE'), nullable=False),
                       UniqueConstraint('student', 'course'),
                       )


def create_params_for_student_course() -> list:
    """Return params for student-course many-to-many relation for executemany insertion.
    Every student will have varying number of rows (courses)"""

    student_courses = data.generate_student_courses()

    with engine.connect() as conn:
        student_ids = conn.execute(select(student.c.id)).all()

    return [{'student': id[0], 'course': c} for id, courses in zip(student_ids, student_courses) for c in courses]


def insert_initial_data() -> None:
    """Insert initial data to all db tables as per task requirements"""
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


def find_groups_with_fewer_or_equal_students(n: int = 20) -> list:
    """Return groups with fewer or equal than n students"""
    count = func.count('student.c.id').label('count')
    s = select(group.c.name, count).join(student).group_by(group.c.name).order_by(desc('count')).having(count <= n)
    with engine.connect() as conn:
        res = conn.execute(s)
    return res.all()


def find_students_from_course(course_name: str) -> list:
    """Returns a list of dicts with student info from a given course name (case insensitive and substring-searching)"""
    s = select(
        student.c.id, student.c.first_name, student.c.last_name, group.c.name.label('group'),
        course.c.name.label('course')) \
        .join(student_course, student.c.id == student_course.c.student) \
        .join(course, student_course.c.course == course.c.id) \
        .join(group, group.c.id == student.c.group) \
        .where(course.c.name.ilike(f'%{course_name}%')) \
        .order_by(course.c.name)
    with engine.connect() as conn:
        rows = conn.execute(s)
    return [r._asdict() for r in rows]


def add_student(first_name: str, last_name: str, group_id: int) -> tuple:
    """Adds a student to the db and returns its id"""
    if not all((isinstance(first_name, str), isinstance(last_name, str), isinstance(group_id, int))):
        raise ValueError
    with engine.connect() as conn:
        res = conn.execute(insert(student), {'first_name': first_name, 'last_name': last_name, 'group': group_id})
        conn.commit()
    return res.inserted_primary_key


def delete_student(student_id: int) -> int:
    """Delete student with id from db"""
    with engine.connect() as conn:
        res = conn.execute(delete(student).where(student.c.id == student_id))
        conn.commit()
    return res.rowcount


def add_student_to_course(full_name: str, course_name: str) -> int:
    """Add a student to the course given their full name and course name (case insensitive)."""
    first_name, last_name = full_name.split()
    student_id_subq = select(student.c.id) \
        .where(student.c.first_name.ilike(first_name)) \
        .where(student.c.last_name.ilike(last_name)).scalar_subquery()
    course_subq = select(course.c.id).where(course.c.name.ilike(f'%{course_name}%')).scalar_subquery()
    insert_stmt = insert(student_course).values(student=student_id_subq, course=course_subq)
    with engine.connect() as conn:
        res = conn.execute(insert_stmt)
        conn.commit()
    return res.inserted_primary_key[0]


def remove_student_from_course(student_id: int, course_id: int) -> int:
    """Remove student by id from course by id. Returns positive rowcount if succeeds"""
    del_stmt = delete(student_course) \
        .where(student_course.c.student == student_id) \
        .where(student_course.c.course == course_id)
    with engine.connect() as conn:
        res = conn.execute(del_stmt)
        conn.commit()
    return res.rowcount


def get_all_students() -> list:
    """Get all students as a list of rows"""
    count = func.count('student_course.c.course').label('course_count')
    stmt = select(student.c.id, student.c.first_name, student.c.last_name, group.c.name.label('group'), count) \
        .join(group) \
        .join(student_course, student_course.c.student == student.c.id, isouter=True) \
        .group_by(student.c.id, group.c.name) \
        .order_by(student.c.id)
    with engine.connect() as conn:
        res = conn.execute(stmt)
    return res.mappings().all()


def get_student(id: int) -> dict:
    """Return student info dict by their id"""
    sel_info = select(student.c.id, student.c.first_name, student.c.last_name, group.c.name.label('group')) \
        .join(group) \
        .join(student_course, student.c.id == student_course.c.student, isouter=True) \
        .where(student.c.id == id)

    sel_courses = select(course.c.name) \
        .select_from(student) \
        .join(student_course, student_course.c.student == student.c.id) \
        .join(course, course.c.id == student_course.c.course) \
        .where(student.c.id == id)

    with engine.connect() as conn:
        info = conn.execute(sel_info)
        sel_courses = conn.execute(sel_courses)

    info = info.first()._asdict()
    info.update(
        {'courses':
             [course[0] for course in sel_courses.all()]
         }
    )
    return info
