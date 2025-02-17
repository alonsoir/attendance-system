import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta

# Configuración
fake = Faker()
np.random.seed(42)  # Para reproducibilidad
Faker.seed(42)

# Parámetros
num_days = 30  # Simulación de 30 días
samples_per_day = 24  # Datos por hora
start_date = datetime(2024, 2, 1)


# Función para generar datos de sensores climáticos (Badajoz)
def generate_climate_data():
    data = []
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        for hour in range(samples_per_day):
            timestamp = datetime(date.year, date.month, date.day, hour, 0, 0)
            temperature = np.random.normal(15 + 10 * np.sin(hour * np.pi / 12), 3)  # Patrón diurno
            humidity = np.random.uniform(40, 80)
            solar_radiation = max(0, np.random.normal(500 * np.sin(hour * np.pi / 12), 100))
            wind_speed = np.random.uniform(0, 20)
            precipitation = np.random.choice([0, 0, 0, 1, 2, 5], p=[0.8, 0.1, 0.05, 0.025, 0.02, 0.005])

            data.append([timestamp, temperature, humidity, solar_radiation, wind_speed, precipitation])

    df = pd.DataFrame(data, columns=["timestamp", "temperature", "humidity", "solar_radiation", "wind_speed",
                                     "precipitation"])
    df.to_csv("climate_sensors.csv", index=False)


# Función para generar datos de sensores de energía
def generate_energy_data():
    data = []
    for day in range(num_days):
        date = start_date + timedelta(days=day)
        battery_charge = np.random.uniform(20, 100)  # Estado inicial aleatorio de la batería
        for hour in range(samples_per_day):
            timestamp = datetime(date.year, date.month, date.day, hour, 0, 0)
            solar_production = max(0, np.random.normal(4 * np.sin(hour * np.pi / 12), 1))  # kWh
            consumption = np.random.normal(1.5, 0.5)  # kWh
            battery_charge = min(100, max(0, battery_charge + solar_production - consumption))  # Actualizar estado
            battery_discharge = max(0, consumption - solar_production)

            data.append([timestamp, solar_production, consumption, battery_charge, battery_discharge])

    df = pd.DataFrame(data,
                      columns=["timestamp", "solar_production", "consumption", "battery_charge", "battery_discharge"])
    df.to_csv("energy_sensors.csv", index=False)


# Generar datos
generate_climate_data()
generate_energy_data()

print("Datos generados y guardados en archivos CSV.")
