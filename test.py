import requests


payload = {
    'username': 'Register1234',
    'password': 'Register1234',
    'remember': 'on',
}

r = requests.post('http://127.0.0.1:8000/login', data=payload)

print(r)
