import pytest
from nipo.nipo_api import app, get_course_list, session


tst_client = app.test_client()

context_data = dict(studentID=7,modulecode="ETI001",status="PrESEnt",SessionDate="2029-04-30T10:30")


class TestRoutes:

	def test_route_index(self):
		tst_courses = get_course_list(session)

		for course in tst_courses:
			pass

	def test_route_module_attendance_post(self):
		resp = tst_client.post("/module/attendance",data=context_data)
		assert b'Ginesh' in resp.data
		assert b'Telecommunications' in resp.data


	def test_route_student_module_post(self):
		resp = tst_client.post("/student/module",data=context_data)
		assert b'Ginesh' in resp.data
		assert b'Telecommunications' in resp.data