from functools import wraps

from flask import redirect, request, session, url_for, Blueprint, current_app
from flask.json import jsonify, loads
from requests_oauthlib import OAuth2Session

import logging
import sys
import core

routes_blueprint = Blueprint('routes_blueprint', __name__)


class SubmitResponse(object):
    def __init__(self, **kwargs):
        self.renderingInProgress = True


@routes_blueprint.route("/",  methods=["GET"])
def login():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider 
    using an URL with a few key OAuth parameters.
    """
    current_app.logger.debug("Login the client. %s", current_app.config['CLIENT_ID'])
    instagram = OAuth2Session(
        current_app.config['CLIENT_ID'], scope='user_profile', redirect_uri=current_app.config['REDIRECT_URI'])
    authorization_url, state = instagram.authorization_url(
        current_app.config['AUTHORIZATION_BASE_URL'])

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@routes_blueprint.route("/callback", methods=["GET"])
def callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """
    current_app.logger.debug("Callback func. Request params: %s", request.args)
    instagram = OAuth2Session(
        current_app.config['CLIENT_ID'], state=session['oauth_state'], 
        redirect_uri=current_app.config['REDIRECT_URI'])
    log = logging.getLogger('requests_oauthlib')
    log.addHandler(logging.StreamHandler(sys.stdout))
    log.setLevel(logging.DEBUG)
    if current_app.config['ACCESS_TOKEN']:
        token = loads(current_app.config['ACCESS_TOKEN'])
    else:
        token = instagram.fetch_token(
            current_app.config['TOKEN_URL'], client_secret=current_app.config['CLIENT_SECRET'], 
            authorization_response=request.url, include_client_id=True)

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
            instagram = OAuth2Session(current_app.config['CLIENT_ID'], token=session['oauth_token'])
            user = instagram.get(current_app.config['USER_URL'])
        else:
            return redirect(url_for('.'))
        # Return the user information attached to the token
        return f(user, *args, **kwargs)
    return decorator


@routes_blueprint.route("/profile", methods=["GET"])
@token_required
def profile(user):
    """Fetching a protected resource using an OAuth 2 token.
    """
    return jsonify(user.json())


@routes_blueprint.route('/submit', methods=['POST'])
@token_required
def submit(user):
    current_app.logger.info("Submit image processing for user ")
    img = request.files.get('img', '')
    selectionRect = request.files.get('selectionRect', '')
    core.VideoProcessor(img)
    return SubmitResponse()
