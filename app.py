import sqlite3
from flask import Flask, request, Response, redirect, url_for, session
from flask_oauthlib.client import OAuth

from ganttoid import ganttoid
from db import read_from_db, update_to_db, write_to_db, init_db


# Replace these values with your OAuth provider's configuration
CLIENT_ID = '49BSSGGQ1EDAOHUMRUP5AMLW63KZ9071'
CLIENT_SECRET = '33PF3HK4F51VMPYODPILU0LSUKUZHS2CV9P4K984E9AZ8B3KZRIMOHVX97RMHYHD'
AUTHORIZATION_URL = 'https://app.clickup.com/api'
TOKEN_URL = 'https://api.clickup.com/api/v2/oauth/token'
REDIRECT_URI = 'http://alpheratz.zudljk.dynv6.net/oauth_callback'  # Update with your redirect URI

app = Flask(__name__)

app.secret_key = 'super_secret_key'

# TBD
oauth = OAuth(app)
oauth_provider = oauth.remote_app(
    'ClickUp',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    request_token_params={},
    base_url=None,
    request_token_url=None,
    access_token_method='POST',
    access_token_url=TOKEN_URL,
    authorize_url=AUTHORIZATION_URL
)


def get_api_key(webhook_id):
    return read_from_db(app, 'client', 'token', 'webhook_id', webhook_id)


def store_api_key(con, webhook_id, token):
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO client (webhook_id, token) VALUES (:webhook_id, :token)", { 
        webhook_id: webhook_id,
        token: token
    })
    cur.commit()
    

def create_webhook(client_id, team_id):
    # TBD, use webhooks endpoint to create one, use the api_key as authorization header
    webhook_id = None # TBD get from response
    update_to_db(app, 'client_data', { 'webhook_id': webhook_id }, 'client_id', client_id)
    store_api_key(con, webhook_id, api_key) 


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(app, '_database', None)
    if db is not None:
        db.close()


@app.route('/save-credentials', methods=['POST'])
def save_credentials():
    data = request.get_json()

    if 'client_id' not in data or 'client_secret' not in data:
        return jsonify({'error': 'Invalid JSON data'}), 400

    client_id = data['client_id']
    client_secret = data['client_secret']

    # Save data to SQLite database
    write_to_db(app, 'client_data', ["client_id", "client_secret"], [client_id, client_secret])
    
    create_webhook(client_id)
    
    return jsonify({'message': 'Credentials saved successfully'}), 201


# TBD
@app.before_first_request
def before_first_request():
    init_db(app)    
    

@app.route('/clickup-webhook', methods=['POST'])
def clickup_webhook():
    # Get the JSON data from the request
    data = request.json
    
    con = sqlite3.connect('example.db')
    
    api_key = get_api_key(con, data["webhook_id"])
    
    # Pass the received data to ganttoid library for processing
    ganttoid(api_key, task=data["task_id"])

    # Process the result from ganttoid (if needed)
    # For example, you might want to log or handle the result

    # Return a response (you can customize this based on your needs)
    return Response(status=202, content_type="application/json")


@app.route('/login')
def login():
    callback_url = url_for('oauth_callback', _external=True)
    return oauth_provider.authorize(callback=callback_url)


@app.route('/oauth_callback')
def oauth_callback():
    response = oauth_provider.authorized_response()
    if response is None or isinstance(response, Exception):
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    
    # Handle the authenticated user data received in 'response'
    # Example: access_token = response['access_token']
    # Perform actions like storing user info in session or database
    access_token = response['access_token']
    #store_api_key(None, )
    
    # Redirect to a success page or profile page after successful authentication
    return redirect(url_for('success'))


@app.route('/success')
def success():
    # Display success message or user profile after successful authentication
    return 'Authentication successful!'


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
