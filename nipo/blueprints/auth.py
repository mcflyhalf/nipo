from flask import Blueprint, redirect, g, url_for
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from nipo.forms import LoginForm
from werkzeug.urls import url_parse


bp = Blueprint('auth', __name__, url_prefix='')

login_manager = LoginManager(bp)
login_manager.init_app(bp)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return g.db_session.query(schema.User).filter(schema.User.id==int(user_id)).one_or_none()

@bp.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('landing'))
	form = LoginForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		user = g.db_session.query(schema.User).\
					  filter(schema.User.username == username.lower()).\
									  one_or_none()

		if user is None or not user.check_password(password):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		
		login_user(user, remember=form.remember_me.data)
		#Not sure if it is necessary to commit/persist after every login
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('landing')
		return redirect(next_page)
	return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('landing'))

#The following registration flow has several steps
#But makes the most sense for an academic institution
#Will only be corrected if some academic institution is interested
#Only an admin should register students. 
#Current implementation idea, admin registers email via admin landing
#(creates a passwordless account that cannot login)
#Then student is notified that they can register on this page (including a token)
#They present the token and the email already provided by admin
#They now set their password
@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('landing'))
	flash("registration page is disabled. Contact admin")
	return redirect(url_for('login'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = schema.User(username=form.username.data.lower(), email=form.email.data,authenticated=False,active=True)
		user.set_password(form.password.data)
		g.db_session.add(user)
		g.db_session.commit()		
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

