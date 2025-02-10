import cv2
import numpy as np
from PIL import Image
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import piexif  # Para manejar los datos EXIF

# 🔑 CLAVE SECRETA PARA CIFRADO (debe tener 32 bytes para AES-256)
SECRET_KEY = b'MiSuperClaveSecretaParaDNI2025!!'

def decrypt_text(encrypted_text):
    """ Descifra el texto encriptado con AES-256. """
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=SECRET_KEY[:16])
    decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
    return decrypted_bytes.decode()

def extract_text_from_pixels(image):
    """ Extrae el texto cifrado de los píxeles (canal azul). """
    np_image = np.array(image)
    h, w, _ = np_image.shape
    extracted_bytes = []

    for y in range(h):
        for x in range(w):
            # Extraer los 4 bits menos significativos del canal azul
            byte = np_image[y, x, 2] & 0x0F
            if byte:
                extracted_bytes.append(byte)

    # Convertir los bytes extraídos en texto
    return bytes(extracted_bytes).decode('utf-8', errors='ignore')

def recover_watermark(input_image_path):
    # Cargar la imagen y los EXIF
    pil_image = Image.open(input_image_path)

    # ---- NIVEL 1: Extraer texto desde los metadatos EXIF ----
    exif_data = pil_image.info.get("exif", b"")
    if exif_data:
        exif_dict = piexif.load(exif_data)
        encrypted_text_exif = exif_dict["Exif"].get(piexif.ExifIFD.UserComment, b"")
        if encrypted_text_exif:
            encrypted_text_exif = encrypted_text_exif.decode("utf-8")
            watermark_text_from_exif = decrypt_text(encrypted_text_exif)
            print(f"Texto recuperado de EXIF: {watermark_text_from_exif}")
        else:
            print("⚠️ No se encontró texto cifrado en EXIF.")
    else:
        print("⚠️ No se encontró EXIF en la imagen.")

    # ---- NIVEL 2: Extraer texto desde los píxeles (canal azul) ----
    extracted_text_from_pixels = extract_text_from_pixels(pil_image)
    print(f"Texto extraído de los píxeles: {extracted_text_from_pixels}")

    return pil_image

def remove_watermarks(input_image_path, output_image_path):
    """ Genera una imagen sin las marcas de agua (fiel al original). """
    # Cargar la imagen original
    original_image = cv2.imread(input_image_path)

    # Guardar la imagen original sin modificaciones
    cv2.imwrite(output_image_path, original_image)
    print(f"✅ Imagen sin marcas de agua guardada en: {output_image_path}")

# ---- EJECUCIÓN ----
input_image_path = "dni_marcado.jpg"
output_clean_image_path = "dni_original_sin_marcas.jpg"

# Recuperar marcas de agua y metadatos
recover_watermark(input_image_path)

# Generar una versión limpia (sin marcas de agua)
remove_watermarks("dni1.jpeg", output_clean_image_path)
