import core
import os

from functools import wraps
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for, logging
from flask.json import jsonify
from dotenv import load_dotenv
from logging.config import dictConfig

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

class SubmitResponse(object):
     def __init__(self, **kwargs):
         self.renderingInProgress = True

@app.route("/")
def login():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider 
    using an URL with a few key OAuth parameters.
    """
    app.logger.debug("Login the client.")
    instagram = OAuth2Session(app.config['client_id'], scope='user_profile', redirect_uri=app.config['REDIRECT_URI'])
    authorization_url, state = instagram.authorization_url(app.config['authorization_base_url'])

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@app.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    app.logger.debug("Callback func. Request params: %s", request.args)
    instagram = OAuth2Session(app.config['client_id'], state=session['oauth_state'])
    if app.config['access_token']:
        token = app.config['access_token']
    else:
        token = instagram.fetch_token(app.config['token_url'], client_secret=app.config['client_secret'], authorization_response=request.url)

    # At this point we can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        app.logger.debug("Checking oauth_token...")
        # ensure the jwt-token is passed with the headers
        if session['oauth_token']:
            app.logger.debug("oauth_token: %s", session['oauth_token'])
            token = session['oauth_token']
        if not token: # throw error if no token provided
            app.logger.debug("oauth_token doesn't exist, redirecting to /")
            return redirect(url_for('.'))
         # Return the user information attached to the token
        return f(token, *args, **kwargs)
    return decorator
    

@app.route("/profile", methods=["GET"])
@token_required
def profile(token):
    """Fetching a protected resource using an OAuth 2 token.
    """
    app.logger.debug("Returning user profile")
    instagram = OAuth2Session(app.config['client_id'], token=token)
    return jsonify(instagram.get(app.config['user_url']).json())


@app.route('/submit', methods=['POST'])
@token_required
def submit():
    app.logger.debug("Submit image processing")
    img = request.files.get('img', '')
    selectionRect = request.files.get('selectionRect', '')
    core.VideoProcessor(img)
    return SubmitResponse()


if __name__ == "__main__":
    app.logger.debug("Starting the app")
    load_dotenv()
    app.config.update(
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        authorization_base_url='https://api.instagram.com/oauth/authorize',
        token_url='https://api.instagram.com/login/oauth/access_token',
        USER_URL='https://graph.instagram.com/me?fields=id,username',
        REDIRECT_URI=os.getenv("REDIRECT_URI", 'http://localhost:5000/callback'),
        access_token = os.getenv("ACCESS_TOKEN")
    )
    port = int(os.environ.get("PORT", 5000))
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=port, debug=True)