import argparse
import os

from flask import Flask, render_template, request, redirect, url_for, session
from flask_restful import Api
from sqlalchemy_utils.functions import database_exists, create_database, get_tables

from src.api_resources import ListStudents, Student, AddStudent, GroupsWithFewerOrEqualStudents, StudentsFromCourse, \
    StudentToCourse, StudentRemoveCourse
from src import db

API_PREFIX = '/api/v1/'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_KEY') or 'dev'

api = Api(app)

api.add_resource(ListStudents, API_PREFIX + 'students/')
api.add_resource(Student, API_PREFIX + 'students/<int:student_id>/', API_PREFIX + 'student/<int:student_id>/')
api.add_resource(AddStudent, API_PREFIX + 'students/add/', API_PREFIX + 'student/add/')
api.add_resource(GroupsWithFewerOrEqualStudents, API_PREFIX + 'groups_LE/<int:n>/')
api.add_resource(StudentsFromCourse, API_PREFIX + 'students/from_course/<string:course_name>/')
api.add_resource(StudentToCourse, API_PREFIX + 'students/add_course/')
api.add_resource(StudentRemoveCourse, API_PREFIX + 'students/remove_course/')

parser = argparse.ArgumentParser('Interaction with students database')
parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuild the database with newly generated data')

if __name__ == '__main__':
    if not database_exists(db.engine.url):
        create_database(db.engine.url)
        db.insert_initial_data()
    args = parser.parse_args()
    if args.rebuild:
        db.insert_initial_data()
    app.run()
