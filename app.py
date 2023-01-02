import os
import sys

import logging
from logging.config import dictConfig
from flask import Flask
from routes import routes_blueprint


dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.logger.info("Starting the app...")
app.register_blueprint(routes_blueprint)

app.config.update(CLIENT_ID=os.getenv("CLIENT_ID"),
                  CLIENT_SECRET=os.getenv("CLIENT_SECRET"),
                  REDIRECT_URI=os.getenv("REDIRECT_URI"),
                  AUTHORIZATION_BASE_URL='https://api.instagram.com/oauth/authorize',
                  USER_URL='https://graph.instagram.com/me?fields=id,username',
                  TOKEN_URL='https://api.instagram.com/login/oauth/access_token',
                  ACCESS_TOKEN=os.getenv("ACCESS_TOKEN"),
                  PORT=int(os.getenv("PORT", 5000)))
app.secret_key = os.urandom(24)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)
