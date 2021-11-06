from flask_restful import Resource, marshal_with, fields
import src.db as db

STUDENT_FIELDS = {
    'id': fields.String(attribute=lambda dic: dic['id']),
    'first_name': fields.String(attribute=lambda dic: dic['first_name']),
    'last_name': fields.String(attribute=lambda dic: dic['last_name']),
    'group': fields.String(attribute=lambda dic: dic['group']),
}


class ListStudents(Resource):
    student_fields = STUDENT_FIELDS.copy()
    student_fields.update(
        {'course_count': fields.String(attribute=lambda dic: dic['course_count'], default='wtf')}
    )

    @marshal_with(student_fields, envelope='Students')
    def get(self):
        return db.get_all_students()


class StudentDetail(Resource):
    student_fields = STUDENT_FIELDS.copy()
    student_fields.update(
        {'courses': fields.List(fields.String, attribute=lambda dic: dic['courses'], default='wtf')}
    )

    @marshal_with(student_fields, envelope='Student')
    def get(self, student_id):
        return db.get_student(student_id)
