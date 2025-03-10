import requests
phone_number = "14158586273"
url = f"https://api.apilayer.com/number_verification/validate?number={phone_number}"

payload = {}
headers= {
  "apikey": "YOUR_API_KEY"
}

response = requests.request("GET", url, headers=headers, data = payload)

status_code = response.status_code
print(response.text)