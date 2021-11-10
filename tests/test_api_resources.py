import json

import pytest
from sqlalchemy import select

from src.app import API_PREFIX
from src import data
from src.db import student_course


def test_list_students(test_client):
    r = test_client.get(API_PREFIX + 'students/')
    assert r.status_code == 200
    assert r.content_type == 'application/json'
    resp_dic = json.loads(r.data)
    assert resp_dic['Students']


def test_get_student(test_client):
    r = test_client.get(API_PREFIX + 'student/1/')
    assert r.status_code == 200
    assert r.content_type == 'application/json'
    resp_dic = json.loads(r.data)
    assert resp_dic['Student']


def test_delete_student(test_client):
    r = test_client.delete(API_PREFIX + 'student/199/')
    assert r.status_code == 200
    r = test_client.delete(API_PREFIX + 'student/199/')
    assert r.status_code == 404


def test_add_student(test_client):
    data = dict(first_name='First', last_name='Last', group_id=1)
    r = test_client.post(API_PREFIX + 'students/add/', data=data)
    assert r.status_code == 201
    r = test_client.post(API_PREFIX + 'students/add/', data={})
    assert r.status_code == 400


def test_groups_le(test_client):
    r = test_client.get(API_PREFIX + 'groups_LE/20/')
    groups_dic = json.loads(r.data)
    assert groups_dic['Groups']
    for group in groups_dic['Groups']:
        assert int(group['student_count']) <= 20


@pytest.mark.parametrize('course_name', data.COURSES)
def test_students_from_course(course_name, test_client):
    r = test_client.get(API_PREFIX + f'students/from_course/{course_name}/')
    students_dic = json.loads(r.data)
    assert students_dic['Students']
    for st in students_dic['Students']:
        assert course_name.lower() in st['course match'].lower()


def test_student_to_course(test_db, test_client):
    # find name and an unattended course
    r = test_client.get(API_PREFIX + 'students/5/')
    student_dic = json.loads(r.data)
    first, last = student_dic['Student']['first_name'], student_dic['Student']['last_name']
    courses = student_dic['Student']['courses']
    for course in data.COURSES:
        if course.lower() not in courses:
            new_course = course
            break

    # adding to new course course
    params = {'student_name': f'{first} {last}', 'course_name': new_course}
    r = test_client.post(API_PREFIX + 'students/add_course/', data=params)
    assert r.status_code == 201

    r = test_client.get(API_PREFIX + 'students/5/')
    student_dic = json.loads(r.data)
    courses = student_dic['Student']['courses']
    assert new_course.capitalize() in courses


def test_student_remove_course(test_db, test_client):
    # finding student with a course
    with test_db.connect() as conn:
        student_with_course = conn.execute(
            select(student_course.c.student, student_course.c.course)
        ).first()
    student_id, course_id = student_with_course

    # deleting by the tested API
    params = {'student_id': student_id, 'course_id': course_id}
    r = test_client.delete(API_PREFIX + 'students/remove_course/', data=params)
    assert r.status_code == 200

    # asserting that deletion succeeded
    with test_db.connect() as conn:
        res = conn.execute(
            select(student_course.c.student, student_course.c.course)
                .where(student_course.c.student == student_id)
                .where(student_course.c.course == course_id)
        )
    assert res.rowcount == 0
