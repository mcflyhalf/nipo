from flask import g
from nipo.conf import Session #import may need to be moved just before line 6

def get_db_session():
    if 'db_session' not in g:
        g.db_session = Session()

    return g.db_session