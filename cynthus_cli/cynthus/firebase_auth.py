import os
import requests
import json
from datetime import datetime, timedelta
# It shouldn't actually matter if this key is public but just in case
FIREBASE_API_KEY = "AIzaSyA9YPNJUo9Z6OIxgACbSLB-VUQDaaXxdMQ"
FIREBASE_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
FIREBASE_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
TOKEN_FILE_PATH = "auth_token.json"


def sign_up_user():
    '''Signup the user to Firebase, should be executed at the very beginning to ensure login'''
    email = input("Enter your email: ")
    password = input("Enter your password: ")
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(FIREBASE_SIGNUP_URL, data=json.dumps(
            payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        auth_data = response.json()
        print("Sign-up successful")
        store_token(auth_data["idToken"],
                    auth_data["localId"], auth_data["expiresIn"])
        # Return token and UID for cloud ops
        return auth_data["idToken"], auth_data["localId"]
    except requests.exceptions.RequestException as error:
        print(
            f"Sign-up error: {error.response.json().get('error', {}).get('message', 'Unknown error')}")
        raise


def login_user(email, password):
    '''Login the user to Firebase and store their auth_token'''
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(FIREBASE_SIGNIN_URL, data=json.dumps(
            payload), headers={"Content-Type": "application/json"})
        response.raise_for_status()
        auth_data = response.json()
        store_token(auth_data["idToken"],
                    auth_data["localId"], auth_data["expiresIn"])
        return auth_data["idToken"], auth_data["localId"]
    except requests.exceptions.RequestException as error:
        print(
            f"Authentication error: {error.response.json().get('error', {}).get('message', 'Unknown error')}")
        raise


def store_token(id_token, uid, expires_in):
    '''Store the user's token so they don't need to relog'''
    expiration_time = datetime.now() + timedelta(seconds=int(expires_in))
    token_data = {
        "id_token": id_token,
        "uid": uid,
        "expires_at": expiration_time.isoformat()
    }
    with open(TOKEN_FILE_PATH, "w") as token_file:
        json.dump(token_data, token_file)


def load_token():
    '''Load the token from the auth_token file'''
    if not os.path.exists(TOKEN_FILE_PATH):
        return None, None

    with open(TOKEN_FILE_PATH, "r") as token_file:
        token_data = json.load(token_file)

    expiration_time = datetime.fromisoformat(token_data["expires_at"])
    if datetime.now() < expiration_time:
        return token_data["id_token"], token_data["uid"]
    else:
        print("Token expired. Please log in again.")
        return None, None


def check_authentication():
    '''Check if a user is authenticated, to be used in cloud op commands'''
    token, uid = load_token()
    if token:
        return token, uid

    email = input("Enter your email: ")
    password = input("Enter your password: ")
    try:
        token, uid = login_user(email, password)
        return token, uid
    except Exception as e:
        print("Login failed. Please try again.")
        raise
