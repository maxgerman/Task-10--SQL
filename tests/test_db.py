""" Tests for db functions. """

import pytest
from sqlalchemy import select, inspect

from src import db
from src.db import student, group, course, student_course
from src import data


def test_create_params_for_student_course(test_db):
    """Test that params for student-course many-to-many table are created.
    Every student will have varying number of rows (courses)"""
    params = db.create_params_for_student_course()
    for p in params:
        assert len(p) == 2
        assert isinstance(p['student'], int)
        assert isinstance(p['course'], int)


def test_insert_initial_data(test_db):
    """Test that inital data is inserted to the database"""
    insp = inspect(test_db)
    assert all(map(insp.has_table, ['student', 'group', 'course', 'student_course']))

    with db.engine.connect() as conn:
        st = conn.execute(select(student))
        gr = conn.execute(select(group))
        crs = conn.execute(select(course))
        st_cr = conn.execute(select(student_course))
    assert st.rowcount == 200
    for s in st:
        assert len(s) == 4
        assert s.first_name is not None
        assert s.last_name is not None
    assert gr.rowcount == 10
    assert crs.rowcount == 10
    for row in st_cr:
        assert 1 <= row.student <= 200
        assert 1 <= row.course <= 10


@pytest.mark.parametrize('count', [25, 20, 15])
def test_find_groups_with_fewer_or_equal_students(test_db, count):
    """Test that groups with fewer or equal students are returned"""
    found = db.find_groups_with_fewer_or_equal_students(count)
    for g in found:
        assert len(g.name) == 5
        assert g.count <= count
    assert len(db.find_groups_with_fewer_or_equal_students(11)) == 0


@pytest.mark.parametrize('course_name', data.COURSES)
def test_find_students_from_course(test_db, course_name):
    """Test that students from specific course are found"""
    found = db.find_students_from_course(course_name)
    assert found is not None
    for dic in found:
        assert str(dic['course']).lower() == course_name.lower()


def test_add_student(test_db):
    """Test that student is added to db by name, surname and group id"""
    id = db.add_student('Name', 'Surname', 1)
    assert id is not None
    with test_db.connect() as conn:
        res = conn.execute(
            select(student.c.id) \
                .where(student.c.first_name == 'Name') \
                .where(student.c.last_name == 'Surname')
        )
        conn.commit()
    assert res.first().id is not None


def test_delete_student(test_db):
    """Test that student is deleted"""
    with test_db.connect() as conn:
        res = conn.execute(select(student.c.id).where(student.c.id == 200))
    id = res.first().id
    assert id is not None

    rowcount = db.delete_student(id)
    assert rowcount == 1

    # try to get deleted student id after deletion
    with test_db.connect() as conn:
        res = conn.execute(select(student.c.id).where(student.c.id == 200))
    assert res.rowcount == 0


def test_add_student_to_course(test_db):
    """Test that student is added to the new course"""
    with test_db.connect() as conn:
        first, last = conn.execute(select(student.c.first_name, student.c.last_name)
                                   .where(student.c.id == 2)).first()
        courses_tup = conn.execute(select(student_course.c.course).select_from(student)
                                   .join(student_course, isouter=True)
                                   .where(student_course.c.student == 2)).all()

    # define an unattended course name
    for new_course_id in range(1, 11):
        if (new_course_id,) not in courses_tup:
            new_course_name = db.data.COURSES[new_course_id - 1]
            break
    else:
        raise ValueError('All courses already attended')

    db.add_student_to_course(first + ' ' + last, new_course_name)
    with test_db.connect() as conn:
        courses_tup = conn.execute(select(student_course.c.course).select_from(student)
                                   .join(student_course, isouter=True)
                                   .where(student_course.c.student == 2)).all()
    # check that new course is now included
    assert (new_course_id,) in courses_tup


def test_remove_student_from_course(test_db):
    """Test that student is removed from the course by ids"""
    with test_db.connect() as conn:
        course_tup = conn.execute(select(student_course.c.course).select_from(student)
                                  .join(student_course, isouter=True)
                                  .where(student_course.c.student == 2)).first()

    db.remove_student_from_course(2, course_tup.course)

    with test_db.connect() as conn:
        new_course_tup = conn.execute(select(student_course.c.course).select_from(student)
                                      .join(student_course, isouter=True)
                                      .where(student_course.c.student == 2)).all()
    assert course_tup not in new_course_tup


def test_get_all_students(test_db):
    """Test that all the students are returned"""
    students = db.get_all_students()
    assert len(students) == 200


def test_get_student(test_db):
    """Test that student is returned by id as a dict with courses number 0-3"""
    student = db.get_student(2)
    assert isinstance(student, dict)
    assert 0 <= len(student['courses']) <= 3

