import datetime
from flask import Blueprint, request
from flask_login import LoginManager, login_required, current_user
from nipo import db
from nipo.db import get_db_sessin
from nipo.db.utils import get_student_list, get_module_list, get_course_list
from nipo.attendance import ModuleAttendance

bp = Blueprint('landing', __name__, url_prefix='')

@bp.route('/')
@bp.route('/index/')
@login_required
def landing():
	'''Display landing page for student, staff(instructor) or admin'''
	session = get_db_session()
	if current_user.privilege == schema.PrivilegeLevel.student.name:
		modules = get_module_list(session)	#TODO: This function currently gets all modules in the system. Need to modify so that it only gets the modules a student is enrolled to. Nipo challenge??
		return render_template('student_dashboard.html',modules = modules)

		courses = get_course_list(session)
		return render_template('list_courses.html', courses = courses)

	elif current_user.privilege == schema.PrivilegeLevel.staff.name:
		#Use query strings to pass name of module in url and refresh whenever module is changed
		#The refreshed page will contain dates of the selected module (from query string)
		#Remember to check that staff member has access to module.
		#Optionally, use post request and have javascript refresh the page (too much work!!!)
		#TODO: For each module, only show valid dates. Nipo challenge?
		modules = current_user.modules
		dates = []
		formatted_dates = []
		
		mod_code = request.args.get('mod_code')
		session_date = request.args.get('session_date')
		#Each of the options below needs to set:
		# 1. selectedModule
		# 2. dates
		# 3. selectedDate
		if mod_code is not None and session_date is None:
			# module changed
			mod_attendance = ModuleAttendance(mod_code, session)
			selectedModule = mod_attendance.module
			if selectedModule not in current_user.modules:
				# User not enrolled in this module
				flash("Invalid module selection")
				return redirect(url_for('landing'))

			dates += mod_attendance.dates
			if len(dates) == 0:
				flash("selected module has no registered class sessions")
				return redirect(url_for('landing'))
			selectedDate = dates[0]

		elif mod_code is not None and session_date is not None:
			# Date changed
			mod_attendance = ModuleAttendance(mod_code, session)
			selectedModule = mod_attendance.module
			dates += mod_attendance.dates
			selectedDate = datetime.datetime.fromisoformat(session_date)
			if selectedModule not in current_user.modules or selectedDate not in dates:
				# User not enrolled in this module or module has no session on this date
				flash("Invalid module or date selection")
				return redirect(url_for('landing'))

		else:
			#Default scenario, fresh login
			if len(modules) == 0:
				flash("You are currently not assigned to any modules. Contact admin to correct this. Showing dummy module.")
				# TODO: Create test module for showing when 
				# staff is not assigned to any modules
				# modules = [test_module]
				modules = get_module_list(session)

			selectedModule = modules[0]
			dates += ModuleAttendance(selectedModule.code, session).dates
			selectedDate = dates[0]
		
		#move selected options to the top of list to make them 
		#the ones selected by default
		if selectedDate != dates[0]:
			dates.remove(selectedDate)
			dates.insert(0, selectedDate)
		
		if selectedModule != modules[0]:
			modules.remove(selectedModule)
			modules.insert(0, selectedModule)
		# raise
		for date in dates:
			human_friendly_format = date.strftime('%a %d %b %H:%M')
			iso_format = date.strftime('%Y-%m-%dT%H:%M')
			combined_format = {"human friendly format": human_friendly_format,
								"iso format": iso_format}

			formatted_dates.append(combined_format)

		students = selectedModule.students
		for student in students:
			student_attendance = StudentAttendance(student.id, session)
			session_attendance = student_attendance.get_session_attendance(selectedModule.code, selectedDate)

			if session_attendance['attendance']:
				student.status= "student-present"
			else:
				student.status= "student-absent"

		return render_template('staff_dashboard.html',\
								dates=formatted_dates,students=students,modules=modules)

	elif current_user.privilege == schema.PrivilegeLevel.admin.name:
		tables = db.utils.get_tables_data(session)
		return render_template('admin_dashboard/admin_dashboard.html',\
								tables=tables, form=add_entity_forms(), attach_to_module_forms=attach_to_module_forms())