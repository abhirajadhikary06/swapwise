import os

SECRET_KEY = os.urandom(24)
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = False