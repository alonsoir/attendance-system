#!/bin/bash

# Función para instalar ffmpeg
install_ffmpeg() {
    echo "Instalando ffmpeg..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Para distribuciones basadas en Debian/Ubuntu
        sudo apt update
        sudo apt install -y ffmpeg
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # Para macOS
        brew install ffmpeg
    elif [[ "$OSTYPE" == "cygwin" ]]; then
        # Para Cygwin (Windows)
        echo "Cygwin no soporta la instalación automática de ffmpeg."
        exit 1
    elif [[ "$OSTYPE" == "msys" ]]; then
        # Para Git Bash (Windows)
        echo "Por favor, instala ffmpeg manualmente en Windows."
        exit 1
    else
        echo "Sistema operativo no soportado."
        exit 1
    fi
}

# Verificar si ffmpeg está instalado
if ! command -v ffmpeg &> /dev/null; then
    install_ffmpeg
fi

# Comprobar si se ha proporcionado el archivo de video
if [ -z "$1" ]; then
    echo "Uso: $0 ruta/al/video.mp4 [nombre_del_gif]"
    exit 1
fi

# Asignar la ruta del video y el nombre del gif (si se proporciona)
VIDEO_PATH="$1"
GIF_NAME="${2:-$(basename "$VIDEO_PATH" .mp4)}.gif"

# Convertir el video a GIF usando ffmpeg
ffmpeg -i "$VIDEO_PATH" "$GIF_NAME"

echo "Conversión completada: $GIF_NAME"
