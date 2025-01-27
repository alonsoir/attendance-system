from pytrends.request import TrendReq
import matplotlib.pyplot as plt
import time
import random
from pytrends.exceptions import TooManyRequestsError, ResponseError


def get_google_trends_data(keywords, timeframe='today 3-m', geo='US', max_retries=5):
    # Configuración simplificada y compatible
    pytrends = TrendReq(
        hl='en-US',
        tz=360,
        # Eliminar parámetros que causan conflicto
        timeout=30  # Solo configurar timeout
    )

    retry_count = 0
    base_delay = 30

    while retry_count < max_retries:
        try:
            time.sleep(random.uniform(1, 3))  # Espera inicial más larga

            pytrends.build_payload(
                keywords,
                cat=0,
                timeframe=timeframe,
                geo=geo,
                gprop=''
            )
            interest_over_time_df = pytrends.interest_over_time()

            time.sleep(random.uniform(2, 5))  # Mayor espera post-request
            return interest_over_time_df

        except (TooManyRequestsError, ResponseError) as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise Exception(f"Error persistente después de {max_retries} reintentos")

            delay = (2 ** retry_count) * base_delay + random.uniform(10, 30)
            print(f"Reintento {retry_count}/{max_retries}. Esperando {delay:.1f}s...")
            time.sleep(delay)

    raise Exception("Falló después de múltiples reintentos")

# Configuración más conservadora
STOCKS = ["AMZN", "MSFT", "NVDA", "AAPL", "GOOG"]

try:
    # Intentar obtener datos
    trends_data = get_google_trends_data(STOCKS, max_retries=7)

    # Procesar y mostrar datos
    if not trends_data.empty:
        plt.figure(figsize=(20, 12))
        trends_data.plot(title='Google Trends for STOCKS')
        plt.xlabel('Date')
        plt.ylabel('Interest Over Time')
        plt.show()
    else:
        print("No se obtuvieron datos válidos")

except Exception as e:
    print(f"Error final: {str(e)}")
    print("Recomendación: Esperar varias horas antes de intentar nuevamente")