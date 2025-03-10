import os

import requests
import json  # Import the JSON module
'''
“Real-Time IP Geolocation API”
'''
def obtener_ip_publica():
    try:
        ip_publica = requests.get('http://checkip.amazonaws.com').text.strip()
        return ip_publica
    except Exception as e:
        print(f"Error al obtener IP pública: {e}")
        return None

API_KEY = os.getenv("IPSTACK_API_KEY")
IP = obtener_ip_publica() ## IP You Wann Explore
print(f"Your actual public ip: {IP}")

url = f"https://api.ipstack.com/{IP}?access_key={API_KEY}&hostname=1"

response = requests.get(url)
print("From ipstack:  ")
# Pretty-print JSON response
print(json.dumps(response.json(), indent=2))