import pytest

from nipo import nipo_api

# @pytest.fixture
# def client():
#     db_fd, flaskr.app.config['DATABASE'] = tempfile.mkstemp()
#     flaskr.app.config['TESTING'] = True

#     with flaskr.app.test_client() as client:
#         with flaskr.app.app_context():
#             flaskr.init_db()
#         yield client

#     os.close(db_fd)
#     os.unlink(flaskr.app.config['DATABASE'])

@pytest.fixture
def client():
	nipo_api.app.config['TESTING'] = True
	with nipo_api.app.test_client() as client:
		yield client

