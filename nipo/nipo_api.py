import os
from nipo import get_db_session
from flask import Flask
from flask_login import LoginManager
from nipo.blueprints import auth, landing, api

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']
#TODO: Modify app config to expire sessions after a day 
#See https://stackoverflow.com/questions/11783025/is-there-an-easy-way-to-make-sessions-timeout-in-flask
#Max upload size = 100 kB
app.config['MAX_CONTENT_LENGTH'] = 10 * 1000 

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(api.bp)
app.register_blueprint(landing.bp)

auth.login_manager.init_app(app)
@app.teardown_appcontext
def shutdown_session(exception=None):
	session = get_db_session()
	session.close()


