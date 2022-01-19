def get_db_session():
# Strange import location is to allow bootstrapping. Need a better solution
    from flask import g
    from nipo.conf import Session
    if 'db_session' not in g:
        g.db_session = Session()

    return g.db_session