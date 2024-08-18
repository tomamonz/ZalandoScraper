import os
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
from flask import Blueprint, redirect, url_for, session, request, render_template

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

oauth_blueprint = Blueprint('oauth', __name__)

# OAuth 2.0 configuration
CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['openid', 'https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email']

@oauth_blueprint.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    flow.redirect_uri = url_for('oauth.oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state
    return redirect(authorization_url)

@oauth_blueprint.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    
    # Ensure we have the state saved in the session
    if not state:
        return redirect(url_for('oauth.authorize'))
    
    # Initialize the flow with the state and scopes
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    
    flow.redirect_uri = url_for('oauth.oauth2callback', _external=True)

    # Fetch the token from the authorization response
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store the credentials in the session
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    # Redirect to the confirmation or dashboard page
    return redirect(url_for('oauth.confirmation'))


@oauth_blueprint.route('/confirmation')
def confirmation():
    # Check if credentials are available in the session
    if 'credentials' not in session:
        return redirect(url_for('oauth.authorize'))

    # Rebuild the credentials object from the session
    credentials = google.oauth2.credentials.Credentials(**session['credentials'])
    
    # Use the credentials to make a simple API call (Google People API in this case)
    service = googleapiclient.discovery.build('people', 'v1', credentials=credentials)

    # Fetch the user's profile information
    profile = service.people().get(resourceName='people/me', personFields='names,emailAddresses').execute()

    # Extract the user's name and email
    name = profile['names'][0]['displayName']
    email = profile['emailAddresses'][0]['value']

    # Render a template with the user's name, email, and a button to run the Zalando checker
    return render_template('confirmation.html', name=name, email=email)

# Helper function to convert credentials to dictionary
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
