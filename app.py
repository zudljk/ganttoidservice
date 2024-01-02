import sqlite3
from flask import Flask, request, Response, redirect, url_for, session
from flask_oauthlib.client import OAuth

from ganttoid import ganttoid


# Replace these values with your OAuth provider's configuration
CLIENT_ID = 'your_client_id'
CLIENT_SECRET = 'your_client_secret'
AUTHORIZATION_URL = 'https://app.clickup.com/api?client_id={client_id}&redirect_uri={redirect_uri}'
TOKEN_URL = 'https://api.clickup.com/api/v2/oauth/token'
REDIRECT_URI = 'http://localhost:5000/oauth_callback'  # Update with your redirect URI

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

# TBD
def initialize_database():
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()
    
    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (webhook_id TEXT, token TEXT);
        CREATE TABLE IF NOT EXISTS oauth2_config (client_id TEXT, client_secret TEXT);
    ''')
    
    conn.commit()
    conn.close()


def get_api_key(con, webhook_id):
    cur = con.cursor()
    return cur.execute("SELECT token FROM client WHERE webhook_id = :webhook_id", { webhook_id: webhook_id }).fetchone()
        

def store_api_key(con, webhook_id, token):
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO client (webhook_id, token) VALUES (:webhook_id, :token)", { 
        webhook_id: webhook_id,
        token: token
    })
    cur.commit()
    

def create_webhook(con, api_key):
    # TBD, use webhooks endpoint to create one, use the api_key as authorization header
    webhook_id = None # TBD get from response
    store_api_key(con, webhook_id, api_key) 


# TBD
@app.before_first_request
def before_first_request():
    initialize_database()


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
    
    # Redirect to a success page or profile page after successful authentication
    return redirect(url_for('success'))


@app.route('/success')
def success():
    # Display success message or user profile after successful authentication
    return 'Authentication successful!'


if __name__ == '__main__':
    app.run(debug=True)
