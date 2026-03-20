
import requests

url = "http://127.0.0.1:8000/admin/"

try:
    response = requests.get(url)
    print(f"Status code: {response.status_code}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
