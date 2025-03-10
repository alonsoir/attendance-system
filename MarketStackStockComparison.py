import os
import logging
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
API_URL = "https://api.marketstack.com/v1/eod"
SYMBOLS = ["AAPL", "MSFT", "TSLA", "NVDA", "TEF.BMEX"]
DAYS_BACK = 30


def configure_plotting() -> None:
    """Configures plotting style using matplotlib and seaborn."""
    try:
        plt.style.use("default")  # Start with a clean slate
        sns.set_theme(context="notebook", style="darkgrid", palette="husl")
        logging.info("Plotting style configured successfully.")
    except Exception as e:
        logging.error(f"Error configuring plotting style: {e}", exc_info=True)


def get_api_key() -> str:
    """Retrieves the API key from the environment variables."""
    api_key = os.getenv("API_KEY")
    if not api_key:
        logging.error(
            "API_KEY environment variable is not set. Please set it before running the script."
        )
        raise ValueError(
            "API_KEY environment variable is not set. Please set it before running the script."
        )
    logging.info("API key retrieved successfully.")
    return api_key


def get_date_range(days_back: int) -> tuple[str, str]:
    """Calculates the date range based on the number of days back."""
    today: str = datetime.today().strftime("%Y-%m-%d")
    last_days: str = (datetime.today() - timedelta(days=days_back)).strftime(
        "%Y-%m-%d"
    )
    logging.info(f"Date range calculated: Today={today}, Last Days={last_days}")
    return today, last_days


def fetch_api_data(symbol: str, date_from: str, date_to: str, api_key: str) -> List[Dict]:
    """Fetches data from the Marketstack API for a given symbol and date range."""
    params = {
        "access_key": api_key,
        "symbols": symbol,
        "date_from": date_from,
        "date_to": date_to,
        "limit": DAYS_BACK,
    }
    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json().get("data", [])
        logging.info(f"API data fetched successfully for symbol {symbol}.")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed for {symbol}: {e}", exc_info=True)
        return []
    except json.JSONDecodeError as e:
        logging.error(f"Failed to decode JSON response for {symbol}: {e}", exc_info=True)
        return []
    except Exception as e:
        logging.error(f"Unexpected error fetching data for {symbol}: {e}", exc_info=True)
        return []


def process_data(data: List[Dict], symbol: str) -> List[Dict]:
    """Processes the raw data from the API into a usable format."""
    try:
        processed_data = [
            {
                "Date": datetime.strptime(item["date"][:10], "%Y-%m-%d"),
                "Stock": symbol,
                "Open": item["open"],
                "Close": item["close"],
                "Change (%)": round(((item["close"] - item["open"]) / item["open"]) * 100, 2),
            }
            for item in data
        ]
        logging.info(f"Data processed successfully for symbol {symbol}.")
        return processed_data
    except Exception as e:
        logging.error(f"Error processing data for symbol {symbol}: {e}", exc_info=True)
        return []


def generate_plots(df: pd.DataFrame) -> None:
    """Generates and displays the plots."""
    try:
        # Line plot for closing prices
        plt.figure(figsize=(14, 6))
        for symbol in df["Stock"].unique():
            stock_data = df[df["Stock"] == symbol]
            plt.plot(stock_data["Date"], stock_data["Close"], marker="o", linestyle="-", label=symbol)

        plt.title("Evolución de Precios de Cierre (Últimos 30 días)", fontsize=14)
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Precio de Cierre ($)", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig("closing_prices.png") # Save the figure as a PNG
        logging.info("Line plot for closing prices generated successfully.")

        # Bar plot for percentage changes
        plt.figure(figsize=(14, 6))
        sns.barplot(x="Date", y="Change (%)", hue="Stock", data=df)
        plt.title("Variación Porcentual Diaria", fontsize=14)
        plt.xlabel("Fecha", fontsize=12)
        plt.ylabel("Cambio (%)", fontsize=12)
        plt.xticks(rotation=45)
        plt.axhline(0, color="black", linewidth=0.8)  # Reference line at 0%
        plt.tight_layout()
        plt.savefig("percentage_changes.png") # Save the figure as a PNG
        logging.info("Bar plot for percentage changes generated successfully.")

        plt.show() # Display the plots
    except Exception as e:
        logging.error(f"Error generating plots: {e}", exc_info=True)


def main() -> None:
    """Main function to orchestrate data fetching, processing, and plotting."""
    configure_plotting()
    api_key = get_api_key()
    today, last_days = get_date_range(DAYS_BACK)
    all_data = []

    for symbol in SYMBOLS:
        data = fetch_api_data(symbol, last_days, today, api_key)
        if data:
            processed_data = process_data(data, symbol)
            all_data.extend(processed_data)

    if all_data:
        df = pd.DataFrame(all_data).sort_values(by=["Date", "Stock"], ascending=[True, True])
        generate_plots(df)
    else:
        logging.warning("No data to generate plots.")
        print("❌ No se pudieron obtener datos para generar gráficos")


if __name__ == "__main__":
    main()
