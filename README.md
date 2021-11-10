# **Task 10 - SQL**

### Requirements:
* Python ver - 3.8
* Postgres db and role with priveleges to create and modify db
* see requirements.txt

### Description:
The data is generated according to the task: tables are created and filled with students, groups, courses and their relations.

DB queries are implemented in db.py for required functionality - this is also available via APIs:
* /api/v1/students - list students
* /api/v1/student(s)/[id] (get and delete methods) - get or delete a student
* /api/v1/students/add (post) - add a student
* /api/v1/groups_le/[number] - get groups with fewer or equal number of members
* /api/v1/students/add_course/[course_name] (post) - add student to the course
* /api/v1/students/from_course/[course_name] (delete) - remove student from the course




Testing is done on the separate test db. Data generation, all functions and APIs are tested.

