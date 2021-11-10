"""
Data generation for database as per requirements (10 groups, 200 students, etc)

"""
import random
import string

COURSES = [
    'Aviation',
    'Art',
    'Chemistry',
    'Economics',
    'Engineering',
    'Journalism',
    'Music',
    'Oceanography',
    'Maths',
    'Computer Science',
]

FIRST_NAMES = [
    'Noel',
    'Joel',
    'Mateo',
    'Ergi',
    'Luis',
    'Anna',
    'Hannah',
    'Sophia',
    'Emma',
    'Marie',
    'Sam',
    'David',
    'Max',
    'Alice',
    'Maria',
    'Bob',
    'George',
    'Marina',
    'Alex',
    'Jason',
]

LAST_NAMES = [
    'Collymore',
    'Stoll',
    'Verlice',
    'Adler',
    'Huxley',
    'Ledger',
    'Hayes',
    'Ford',
    'Finnegan',
    'Beckett',
    'Phillips',
    'Rogers',
    'Hetfield',
    'Fafara',
    'Friden',
    'Stanne',
    'Hammet',
    'Sweigart',
    'Rhinehart',
    'Dickens',

]


def generate_groups(n=10) -> dict:
    """Generate specified number of groups as a dict (keys - group names, values  - empty lists)"""
    groups = {}
    while len(groups) < n:
        group_name = (random.choice(string.ascii_letters).upper() +
                      random.choice(string.ascii_letters).upper() +
                      '-' +
                      str(random.randint(10, 99))
                      )
        if group_name not in groups:
            groups[group_name] = []
    return groups


def generate_students(n=200) -> list:
    """... Avoid duplicate names"""
    if n > len(FIRST_NAMES) * len(LAST_NAMES):
        raise ValueError

    random.shuffle(FIRST_NAMES)
    random.shuffle(LAST_NAMES)

    students = []
    for first in FIRST_NAMES:
        for last in LAST_NAMES:
            students.append((first, last))
            if len(students) >= n:
                random.shuffle(students)
                return students


def assign_students_to_groups(students: list, groups: dict) -> dict:
    """Put students into groups giving priority to the least populated groups.

    Members limit is 10-30 students per group."""
    for student in students:
        least_populated_groups = sorted([name for name in groups], key=lambda name: len(groups[name]))
        weights = [30 - len(groups[name]) for name in least_populated_groups]
        group = random.choice(random.choices(least_populated_groups, weights=weights, k=3))
        if len(groups[group]) < 30:
            groups[group].append(student)
    return groups


def generate_student_courses(n_courses=10, n_students=200) -> list:
    """Return a list of lists of course ids for each student.

    Len = n_students, values = list of their courses ids (0-3 courses for each), course_id - from 1 to n_courses"""

    courses = []
    for _ in range(n_students):
        courses.append(random.sample(range(1, n_courses + 1), random.randint(0, 3)))
    return courses
