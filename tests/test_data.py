from src import data
import re


def test_generate_groups():
    """Test group names (required format: XX-dd) and their count. Groups are lists inside a dict of group names"""
    g10 = data.generate_groups()
    g11 = data.generate_groups(11)

    assert len(g10) == 10
    assert len(g11) == 11

    for g in g10:
        assert isinstance(g10[g], list)
        assert re.fullmatch(r'[A-Z]{2}-\d{2}', g)


def test_generate_students():
    """Test that students are generated as a list of tuples (name, surname), without duplicates, capitalized"""
    assert len(data.generate_students()) == 200
    s100 = data.generate_students(100)
    assert len(s100) == 100

    known = set()
    for s in s100:
        assert len(s) == 2
        assert re.fullmatch(r'[A-Z][a-z]+', s[0])
        assert re.fullmatch(r'[A-Z][a-z]+', s[1])
        if s in known:
            assert False, 'duplicate found'
        else:
            known.add(s)


def test_assign_students_to_groups():
    """Test that groups are between 10 and 30 members each (task requirement)."""
    groups = data.assign_students_to_groups(data.generate_students(200), data.generate_groups(10))
    for g in groups:
        assert 10 <= len(groups[g]) <= 30


def test_generate_student_courses():
    """Test that each student has 0 to 3 courses with ids from 1 to n_courses."""
    nstudents, ncourses = 200, 10
    courses = data.generate_student_courses(ncourses, nstudents)
    assert len(courses) == nstudents
    for c in courses:
        assert 0 <= len(c) <= 3
        for id in c:
            assert 1 <= id <= ncourses
