import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_restful import Api
from src.api_resources import ListStudents, Student, AddStudent, GroupsWithFewerOrEqualStudents, StudentsFromCourse, \
    StudentToCourse, StudentRemoveCourse

API_PREFIX = '/api/v1/'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_KEY') or 'dev'

api = Api(app)

api.add_resource(ListStudents, API_PREFIX + 'students/')
api.add_resource(Student, API_PREFIX + 'students/<int:student_id>/', API_PREFIX + 'student/<int:student_id>/')
api.add_resource(AddStudent, API_PREFIX + 'students/add/', API_PREFIX + 'student/add/')
api.add_resource(GroupsWithFewerOrEqualStudents, API_PREFIX + 'groups_LE/<int:n>')
api.add_resource(StudentsFromCourse, API_PREFIX + 'students/from_course/<string:course_name>')
api.add_resource(StudentToCourse, API_PREFIX + 'students/add_course/')
api.add_resource(StudentRemoveCourse, API_PREFIX + 'students/remove_course/')

if __name__ == '__main__':
    app.run()
