import os

import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Configuración de estilo para los gráficos
# Configuración de estilo actualizada
plt.style.use('default')
sns.set(context='notebook', style='darkgrid', palette='husl')

# Configuración API
API_KEY = os.getenv("API_KEY")
API_URL = "https://api.marketstack.com/v1/eod"
SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA", "TEF.BMEX"]
DAYS_BACK = 30


def get_date_range(days_back):
    today = datetime.today().strftime('%Y-%m-%d')
    last_days = (datetime.today() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    return today, last_days


def fetch_api_data(symbol, date_from, date_to):
    params = {
        "access_key": API_KEY,
        "symbols": symbol,
        "date_from": date_from,
        "date_to": date_to,
        "limit": DAYS_BACK
    }
    response = requests.get(API_URL, params=params)
    return response.json().get("data", []) if response.status_code == 200 else []


def process_data(data, symbol):
    return [{
        "Date": datetime.strptime(item["date"][:10], "%Y-%m-%d"),
        "Stock": symbol,
        "Open": item["open"],
        "Close": item["close"],
        "Change (%)": round(((item["close"] - item["open"]) / item["open"]) * 100, 2)
    } for item in data]


def generate_plots(df):
    # Gráfico de líneas para precios de cierre
    plt.figure(figsize=(14, 6))
    for symbol in df['Stock'].unique():
        stock_data = df[df['Stock'] == symbol]
        plt.plot(stock_data['Date'], stock_data['Close'],
                 marker='o', linestyle='-', label=symbol)

    plt.title('Evolución de Precios de Cierre (Últimos 30 días)', fontsize=14)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Precio de Cierre ($)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Gráfico de barras para variaciones porcentuales
    plt.figure(figsize=(14, 6))
    sns.barplot(x='Date', y='Change (%)', hue='Stock', data=df)
    plt.title('Variación Porcentual Diaria', fontsize=14)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Cambio (%)', fontsize=12)
    plt.xticks(rotation=45)
    plt.axhline(0, color='black', linewidth=0.8)  # Línea de referencia en 0%
    plt.tight_layout()

    plt.show()


if __name__ == "__main__":
    today, last_days = get_date_range(DAYS_BACK)
    all_data = []

    for symbol in SYMBOLS:
        if data := fetch_api_data(symbol, last_days, today):
            all_data.extend(process_data(data, symbol))

    if all_data:
        df = pd.DataFrame(all_data).sort_values(by=['Date', 'Stock'], ascending=[True, True])
        generate_plots(df)
    else:
        print("❌ No se pudieron obtener datos para generar gráficos")
