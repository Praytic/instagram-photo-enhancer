import core
import os

from functools import wraps
from requests_oauthlib import OAuth2Session
from flask import Flask, request, redirect, session, url_for
from flask.json import jsonify
from dotenv import load_dotenv


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
    instagram = OAuth2Session(client_id, client_secret, scope='user_profile', redirect_uri=redirect_uri)
    authorization_url, state = instagram.authorization_url(authorization_base_url)

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

    instagram = OAuth2Session(client_id, state=session['oauth_state'])
    if access_token:
        token = access_token
    else:
        token = instagram.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    # At this point we can fetch protected resources but lets save
    # the token and show how this is done from a persisted token
    # in /profile.
    session['oauth_token'] = token

    return redirect(url_for('.profile'))


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        if session['oauth_token']:
            token = session['oauth_token']
        if not token: # throw error if no token provided
            return redirect(url_for('.'))
         # Return the user information attached to the token
        return f(token, *args, **kwargs)
    return decorator
    

@app.route("/profile", methods=["GET"])
@token_required
def profile(token):
    """Fetching a protected resource using an OAuth 2 token.
    """
    instagram = OAuth2Session(client_id, token=token)
    return jsonify(instagram.get(user_url).json())


@app.route('/submit', methods=['POST'])
@token_required
def submit():
    img = request.files.get('img', '')
    selectionRect = request.files.get('selectionRect', '')
    core.VideoProcessor(img)
    return SubmitResponse()


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authorization_base_url = 'https://api.instagram.com/oauth/authorize'
    token_url = 'https://api.instagram.com/login/oauth/access_token'
    user_url = 'https://graph.instagram.com/me?fields=id,username'
    redirect_uri = os.getenv("REDIRECT_URI", 'http://localhost:5000/callback')
    access_token = os.getenv("ACCESS_TOKEN")
    port = int(os.environ.get("PORT", 5000))
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = "1"

    app.secret_key = os.urandom(24)
    app.run(host='0.0.0.0', port=port, debug=True)