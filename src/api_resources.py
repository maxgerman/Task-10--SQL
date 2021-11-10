"""Flask restful API resources are defined here"""

from flask_restful import Resource, marshal_with, fields, reqparse
import sqlalchemy.exc

import src.db as db

STUDENT_FIELDS = {
    'id': fields.String(attribute='id'),
    'first_name': fields.String(attribute='first_name'),
    'last_name': fields.String(attribute='last_name'),
    'group': fields.String(attribute='group'),
}


class ListStudents(Resource):
    """Lists students with info"""
    student_fields = STUDENT_FIELDS.copy()
    student_fields.update(
        {'course_count': fields.String(attribute='course_count')}
    )

    @marshal_with(student_fields, envelope='Students')
    def get(self):
        return db.get_all_students()


class Student(Resource):
    """Detailed info about one student. Also supports delete method for deletion"""
    student_fields = STUDENT_FIELDS.copy()
    student_fields.update(
        {'courses': fields.List(fields.String, attribute='courses')}
    )

    @marshal_with(student_fields, envelope='Student')
    def get(self, student_id):
        return db.get_student(student_id)

    def delete(self, student_id):
        """Delete student by id"""
        try:
            res = db.delete_student(student_id)
        except sqlalchemy.exc.SQLAlchemyError:
            return {'error 400': 'bad request'}, 400
        if res:
            return {'deleted student with id': student_id}, 200
        else:
            return {'error 404': f'not found student with id {student_id}'}, 404


class AddStudent(Resource):
    """Add student to db by post request with first_name, last_name, group_id"""

    def post(self):
        """Add student to db"""
        args = parser.parse_args()
        try:
            res = db.add_student(args['first_name'], args['last_name'], int(args['group_id']))
        except (sqlalchemy.exc.SQLAlchemyError, TypeError):
            return {'error 400': 'bad request'}, 400
        return {'student created with id': res[0]}, 201


class GroupsWithFewerOrEqualStudents(Resource):
    """Return groups with fewer or equal number of students"""
    group_fields = {
        'group_name': fields.String(attribute='name'),
        'student_count': fields.String(attribute='count'),
    }

    @marshal_with(group_fields, envelope='Groups')
    def get(self, n=20):
        return db.find_groups_with_fewer_or_equal_students(n)


class StudentsFromCourse(Resource):
    """Return students from the specified course name (partly and case-insensitive)"""
    student_fields = STUDENT_FIELDS.copy()
    student_fields.update({
        'course match': fields.String(attribute='course'),
    })

    @marshal_with(student_fields, envelope='Students')
    def get(self, course_name):
        return db.find_students_from_course(course_name)


class StudentToCourse(Resource):
    """Add student to course by their names (case insensitive for both, part-string for course)"""

    def post(self):
        args = parser.parse_args()
        try:
            db.add_student_to_course(args['student_name'], args['course_name'])
        except sqlalchemy.exc.SQLAlchemyError:
            return {'Error 400': 'bad request'}, 400
        return {'Success': 'Student added to the course'}, 201


class StudentRemoveCourse(Resource):
    """Remove a student from a course by ids"""

    def delete(self):
        args = parser.parse_args()
        try:
            res = db.remove_student_from_course(args['student_id'], args['course_id'])
        except sqlalchemy.exc.SQLAlchemyError:
            return {'Error 400': 'bad request'}, 400
        if res:
            return {'Success': 'Student removed from the course'}, 200
        else:
            return {'Error 404': 'Student not in the course'}, 404


parser = reqparse.RequestParser()
parser.add_argument('first_name')
parser.add_argument('last_name')
parser.add_argument('group_id')
parser.add_argument('student_name')
parser.add_argument('course_name')
parser.add_argument('student_id')
parser.add_argument('course_id')
