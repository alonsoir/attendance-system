import matplotlib.pyplot as plt
from textblob import TextBlob
from deep_translator import GoogleTranslator

# Lista de textos para análisis de sentimientos
texts = [
    "I love programming!",
    "Python is an amazing language.",
    "I hate bugs in my code.",
    "Debugging is fun but challenging."
]

# Análisis de sentimientos
polaridades = [TextBlob(text).sentiment.polarity for text in texts]

# Texto original en español
texto_original = "Me encanta programar, pero a veces es frustrante."

# Análisis de sentimientos con TextBlob
blob = TextBlob(texto_original)
sentimiento = blob.sentiment
print(f"Sentimiento: Polaridad = {sentimiento.polarity}, Subjetividad = {sentimiento.subjectivity}")

# Traducción usando deep-translator
traduccion = GoogleTranslator(source='auto', target='en').translate(texto_original)
print(f"Traducción al inglés: {traduccion}")

# Análisis de sentimientos en el texto traducido
blob_traducido = TextBlob(traduccion)
sentimiento_traducido = blob_traducido.sentiment
print(f"Sentimiento del texto traducido: Polaridad = {sentimiento_traducido.polarity}, Subjetividad = {sentimiento_traducido.subjectivity}")

# Corrección ortográfica
texto_erroneo = "El cambió climatico es un problema global."
blob_erroneo = TextBlob(texto_erroneo)
print("Corrección:", blob_erroneo.correct())

# Extracción de frases nominales
print("Frases nominales:", blob.noun_phrases)

# Visualización del análisis de sentimientos
plt.barh(texts, polaridades, color='skyblue')
plt.xlabel('Polaridad')
plt.title('Análisis de Sentimientos')
plt.axvline(0, color='red', linestyle='--')  # Línea para indicar neutralidad
plt.show()
