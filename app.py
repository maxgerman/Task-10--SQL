import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_restful import Api
from src.api_resources import ListStudents, StudentDetail

API_PREFIX = '/api/v1/'

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_KEY') or 'dev'

api = Api(app)

api.add_resource(ListStudents, API_PREFIX + 'students/')
api.add_resource(StudentDetail, API_PREFIX + 'students/<student_id>/')

if __name__ == '__main__':
    app.run()
