import functions_framework
import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from firebase_admin import initialize_app, credentials, auth
from python_http_client.exceptions import HTTPError


credentials_json = os.environ.get("FIREBASE_KEY")
if credentials_json != None:
    firebase_credentials_dict = json.loads(credentials_json)
    cred = credentials.Certificate(firebase_credentials_dict)
    initialize_app(cred)


@functions_framework.http
def email(request):
    # Validate request
    request_json = request.get_json(silent=True)
    if not request_json or 'uid' not in request_json:
        return 'UID is required in the request', 400
    firebase_uid = request_json['uid']
    # Get user email from Firebase
    try:
        user = auth.get_user(firebase_uid)
        user_email = user.email
        if not user_email:
            return 'User has no email address', 400
    except auth.AuthError as e:
        return f"Error fetching user: {str(e)}", 500
    # Prepare and send email
    try:
        sg = SendGridAPIClient(os.environ.get('EMAIL_API_KEY'))
        message = Mail(
            to_emails=user_email,
            from_email=Email("cynthusgcp@gmail.com", "Cynthus"),
            subject="Cynthus - Workload Finished",
            html_content="""
            <p>Your Cynthus workload has finished running!</p>
            <p>You can pull the outputs with the following command:</p>
            <p><code>cynthus pull [RUN_ID]</code></p>
            """
        )
        response = sg.send(message)
        return {
            'success': True,
            'status_code': response.status_code,
            'message': 'Email sent successfully!'
        }, 200
    except HTTPError as e:
        return {
            'success': False,
            'error': str(e)
        }, 500
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }, 500
