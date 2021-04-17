import pytest

from nipo import nipo_api, test_session
from nipo.db.schema import Module, Student, Course, Venue, User, PrivilegeLevel
from flask_login import current_user
#Discardable test credentials
admin_uname = 'addmein'
admin_pw = 'notApassword'

staff_uname = 'megaman'
staff_pw = 'unsafePassword'

student_name = 'Dent Stu'
student_uname = 'dentstu'
student_pw = 'stillProcrastinatingAssignments'

course_name = 'Test Course'
course_uid = 'Test89'

#setup database assets
@pytest.fixture(scope='module')	#Maybe scope=session
def test_db():
	session = test_session
	#create test users (admin, staff, student)
	test_student = Student(name = student_name, course_uid =course_uid )
	test_course = Course(uid = course_uid, name = course_name)
	
	session.add(test_course)
	session.add(test_student)
	session.commit()

	test_admin_user = User(username= admin_uname,\
						 email= admin_uname+'@mail.com',\
						 name= 'Ad Min',\
						 privilege= PrivilegeLevel.admin.name,
						 active= True,\
						 authenticated= False)
	test_staff_user = User(username= staff_uname,\
						 email= staff_uname+'@mail.com',\
						 name= 'Staff, ChiefOf',\
						 privilege= PrivilegeLevel.staff.name,
						 active= True,\
						 authenticated= False)
	test_student_user = User(username= student_uname,\
						 email= student_uname+'@mail.com',\
						 name= 'Stew Dent',\
						 privilege= PrivilegeLevel.student.name,
						 active= True,\
						 authenticated= False,\
						 student_id= test_student.id)
	test_student_user.set_password(student_pw)
	test_staff_user.set_password(staff_pw)
	test_admin_user.set_password(admin_pw)
	
	session.add(test_student_user)
	session.add(test_staff_user)
	session.add(test_admin_user)

	session.commit()

	yield
	#delete test entities 
	session.delete(test_student_user)
	session.delete(test_staff_user)
	session.delete(test_admin_user)
	session.delete(test_student)
	session.delete(test_course)

	session.commit()



@pytest.fixture
def client():
	nipo_api.app.config['TESTING'] = True
	#Disable csrf protection during testing
	nipo_api.app.config['WTF_CSRF_ENABLED'] = False
	client = nipo_api.app.test_client()
	with nipo_api.app.test_client() as client:
		yield client


#after moving nipo_api into blueprints, break up this class
# into several smaller classes
@pytest.mark.usefixtures("test_db")
class TestAPI:

	def login(self, client, username, password):
		return client.post('/login', data=dict(
			username=username,
			password=password
		), follow_redirects=True)

	def logout(self, client):
		return client.get('/logout', follow_redirects=True)

	def logged_in(self,resp):
		return not b'Sign In' in resp.data

	def test_landing_not_logged_in(self,client):
		#Check for redirect
		resp = client.get('/')
		assert resp.status_code == 302

		#check that redirect is to login page
		# Dont know how to do this atm

		#Check that on arrival at login page we are asked to login
		resp = client.get('/', follow_redirects= True)
		assert resp.status_code == 200
		assert b'Sign In' in resp.data

	def test_landing_admin_logged_in(self, client):
		resp = self.login(client, admin_uname, admin_pw)
		assert b'View users' in resp.data
		assert admin_uname.encode('UTF-8') in resp.data

	def test_landing_staff_logged_in(self, client):
		resp = self.login(client, staff_uname, staff_pw)
		assert b'Contact support' in resp.data
		assert staff_uname.encode('UTF-8') in resp.data

	def test_landing_student_logged_in(self, client):
		resp = self.login(client, student_uname, student_pw)
		assert b'Student attendance Summary' in resp.data
		assert student_uname.encode('UTF-8') in resp.data

	def test_login_incorrect_uname(self,client):
		resp = self.login(client, staff_uname+'1', staff_pw)
		assert not self.logged_in(resp)

	def test_login_incorrect_password(self,client):
		resp = self.login(client, staff_uname, staff_pw+'1')
		assert not self.logged_in(resp)
		


