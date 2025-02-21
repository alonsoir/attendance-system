estrategia completa para simular el sistema antes de invertir en hardware:
0. Establecer la configuración mínima y viable de los componentes. Tienen que hablar entre ellos:
    mosquitto. OK
    homeassistant. OK
    ollama. KO
1. Definir el modelo energético
Crear un conjunto de datos sintéticos que represente la producción y consumo de energía en una casa con placas solares y baterías.
Incluir variables como:
Radiación solar (en función de la ubicación y hora del día).
Consumo eléctrico (electrodomésticos, luces, climatización).
Carga/descarga de baterías (capacidad, eficiencia, pérdidas).
Previsión meteorológica (temperatura, nubosidad, viento, lluvias).
2. Simular sensores y dispositivos IoT
Utilizar software como Home Assistant para gestionar dispositivos simulados.
Emular sensores como:
Temperatura y humedad (para optimizar climatización).
Producción fotovoltaica (según radiación solar simulada).
Estado de las baterías (nivel de carga, capacidad disponible).
Consumo eléctrico en tiempo real (basado en hábitos de uso).
3. Implementar un modelo LLM para la toma de decisiones
Inicialmente, usar un LLM pequeño y cuantizado (por ejemplo, Mistral o Llama 3 en local).
El LLM recibiría datos de sensores y devolvería recomendaciones:
Cuándo cargar o descargar baterías.
Cuánta energía volcar a la red o almacenar.
Ajustes según previsiones meteorológicas.
Para evitar depender de modelos grandes, se podría usar RAG (Retrieval-Augmented Generation) con datos históricos de consumo y clima.
4. Simulación de escenarios
Crear scripts en Python para generar datos de producción/consumo y alimentar al LLM.
Definir escenarios de prueba:
Día soleado vs. nublado.
Consumo alto vs. bajo.
Diferentes capacidades de batería.
Impacto de la predicción meteorológica.
5. Evaluar el rendimiento y optimizar
Medir si el LLM toma decisiones acertadas en diferentes condiciones.
Ajustar el modelo con técnicas como:
Fine-tuning ligero con datos históricos.
Refuerzo con heurísticas (ej., priorizar carga en horas de más sol).
Comparación con reglas clásicas (ej., estrategias basadas en umbrales).
6. Preparación para hardware real
Identificar los requisitos mínimos de computación para ejecutar el LLM de forma eficiente.
Explorar alternativas en edge computing (como Raspberry Pi con Coral TPU o Jetson Nano).
Probar la integración con hardware real cuando sea viable.

Home Assistant en Docker → Gestiona dispositivos simulados.
Script en Python con Pandas/Dask → Carga y procesa datos climáticos históricos en CSV.
Streaming en tiempo real → MQTT (para IoT ligero) o Kafka/Redis Streams (para más volumen de datos).
LLM con Ollama → Recibe datos y devuelve decisiones optimizadas.


Cargar datos climáticos con Pandas/Dask.
Simular sensores en Home Assistant.
Crear un pequeño script para enviar datos al LLM y recibir una respuesta.

Status:

    docker-compose con el homeassistant y mosquitto up and running. OK 
    Tengo un script (mqtt_sensor_simulator.py) que envia datos a topics mqtt. OK
    Tengo que integrar ese script básico con uno que use faker (generate_syntetic_data.py) para alimentar el topic. KO
    Tengo que levantar ollama con un modelo pequeño. OK
    Tengo que conectar el modelo a homeassistant. OK
    Tengo que hacer que el modelo decida que hacer en función a lo que lee. In progress, almost there
    Tengo que hacer que el modelo mande comandos a homeassistan. In progress, almost there