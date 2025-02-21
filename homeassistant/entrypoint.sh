#!/bin/bash
# Inicia el servidor de Ollama en segundo plano
ollama serve &
# Espera unos segundos para que el servidor esté completamente iniciado
sleep 5
# Descarga el modelo mistral
ollama pull mistral
# Mantiene el contenedor en ejecución esperando a que el proceso en segundo plano termine
wait