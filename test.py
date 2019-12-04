import json
import requests
from bs4 import BeautifulSoup

CLIENT_ID = "42c4049a52e248018671e8d055815d79"
CLIENT_SECRET = "33ec3f3cddae456ea02fad2666ff92a6"

grant_type = "client_credentials"
body_params = {"grant_type": grant_type}

url = "https://accounts.spotify.com/api/token"
response = requests.post(url, data=body_params, auth=(CLIENT_ID, CLIENT_SECRET))

token_raw = json.loads(response.text)
token = token_raw["access_token"]
url = "https://api.spotify.com/v1/audio-features/06AKEBrKUckW0KREUWRnvT"

response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
print(type(json.loads(response.text)))
