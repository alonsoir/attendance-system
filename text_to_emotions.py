import os

import requests

url = "https://api.apilayer.com/text_to_emotion"
review = '''
HTTP con estado no fue diseñado para ser escalable, al igual que las bases de datos CP, por lo que, tratar de hacerlas escalables en lecturas y escrituras teniendo consistencia de datos en todos los nodos es una quimera, simplemente no funcionan así y necesitas usar otro tipo de tecnología. 
Hay más mundo aparte de Spring para construir aplicaciones RESTful de la JVM, simplemente hay que conocerlas y saber usarlas, y es normal que si se encuentra un CVE, se trate de arreglar cuanto antes, y es normal tener que subir de versión. Preocúpate más bien de los bugs que no están documentados, porque un CVE es uno conocido hace mucho tiempo y probablemente ha estado haciendo daño bastante tiempo, pero uno indocumentado va a hacer potencialmente mucho más daño.

Obviamente, tiene margen de mejora, no es perfecto, puede ser hasta lento y no estar optimizado para ser usado junto con contenedores, en mi opinión, tiene margen de mejora por ahí, crear un matrimonio de conveniencia con la tecnología de contenedores para ser más rápido y seguro al acceder a los recursos de la maquina anfitrion.'''

payload = f"{review}".encode("utf-8")
headers= {
  "apikey": os.getenv("APIKEY_APILAYER")
}

response = requests.request("POST", url, headers=headers, data = payload)

status_code = response.status_code
result = response.text
print(result)