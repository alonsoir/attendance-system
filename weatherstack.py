import requests
import json
import os

# API key de OpenWeatherMap (reemplaza con tu API key)
API_KEY = os.environ.get("OPENWEATHERMAP_API_KEY", "YOUR_OPENWEATHERMAP_API_KEY")

def get_weather(city, api_key):
    """Obtiene el clima actual de una ciudad usando la API de OpenWeatherMap."""
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",  # Para obtener la temperatura en grados Celsius
        "lang": "es"        # Para obtener las descripciones en español
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Lanza una excepción para códigos de error HTTP

        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el clima: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

def display_weather(weather_data):
    """Muestra la información del clima en la terminal."""
    if weather_data:
        city = weather_data["name"]
        country = weather_data["sys"]["country"]
        temperature = weather_data["main"]["temp"]
        description = weather_data["weather"][0]["description"]
        humidity = weather_data["main"]["humidity"]
        wind_speed = weather_data["wind"]["speed"]

        print(f"📍 Localización: {city}, {country}")
        print(f"🌡️ Temperatura: {temperature}°C")
        print(f"☀️ Condición: {description}")
        print(f"💨 Velocidad del viento: {wind_speed} m/s")
        print(f"💧 Humedad: {humidity}%")
    else:
        print("No se pudo obtener la información del clima.")

if __name__ == "__main__":
    city = "Madrid"  # Ciudad para obtener el clima
    weather_data = get_weather(city, API_KEY)
    display_weather(weather_data)
