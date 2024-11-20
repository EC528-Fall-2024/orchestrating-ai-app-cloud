import pyrebase

configs_to_test = [
    # Test 1: Full config
    {
        "apiKey": "AIzaSyA9YPNJUo9Z6OIxgACbSLB-VUQDaaXxdMQ",
        "authDomain": "cynthusgcp-438617.firebaseapp.com",
        "databaseURL": "",
        "storageBucket": "cynthusgcp-438617.firebasestorage.app"
    },
    # Test 2: Without databaseURL
    {
        "apiKey": "AIzaSyA9YPNJUo9Z6OIxgACbSLB-VUQDaaXxdMQ",
        "authDomain": "cynthusgcp-438617.firebaseapp.com",
        "storageBucket": "cynthusgcp-438617.firebasestorage.app"
    }
]

for config in configs_to_test:
    try:
        print(f"\nTesting config: {config}")
        firebase = pyrebase.initialize_app(config)
        auth = firebase.auth()
        # Try to get basic auth functionality
        print("Auth initialization successful")
    except Exception as e:
        print(f"Error: {e}")