import cv2
import numpy as np
from PIL import Image, ImageDraw, ExifTags
import random
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import piexif  # Para manejar los datos EXIF

# 🔑 CLAVE SECRETA PARA CIFRADO (debe tener 32 bytes para AES-256)
SECRET_KEY = b'MiSuperClaveSecretaParaDNI2025!!'

def encrypt_text(text):
    """ Cifra el texto con AES-256 y lo convierte en Base64. """
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=SECRET_KEY[:16])
    encrypted_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode()

def decrypt_text(encrypted_text):
    """ Descifra el texto encriptado con AES-256. """
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv=SECRET_KEY[:16])
    decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
    return decrypted_bytes.decode()

def embed_text_in_pixels(image, encrypted_text):
    """ Oculta el texto cifrado en los píxeles (canal azul). """
    np_image = np.array(image)
    h, w, _ = np_image.shape
    text_bytes = encrypted_text.encode()

    for i in range(len(text_bytes)):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        np_image[y, x, 2] = (np_image[y, x, 2] & 0xF0) | (text_bytes[i] & 0x0F)

    return Image.fromarray(np_image)

def add_secure_watermark(input_image_path, output_image_path, watermark_text="CONFIDENCIAL", logo_path="logo.png"):
    # ---- NIVEL 1, 2, 3: Marcas visibles (texto repetido + logo) ----
    image = cv2.imread(input_image_path)
    h, w, _ = image.shape
    watermark = np.zeros((h, w, 3), dtype="uint8")
    font = cv2.FONT_HERSHEY_SIMPLEX

    for i in range(0, w, 250):
        for j in range(0, h, 150):
            cv2.putText(watermark, watermark_text, (i, j), font, 1, (255, 255, 255), 2, cv2.LINE_AA)

    rotated_text = cv2.warpAffine(watermark, cv2.getRotationMatrix2D((w//2, h//2), 30, 1), (w, h))
    image_with_text = cv2.addWeighted(image, 1, rotated_text, 0.3, 0)

    pil_image = Image.fromarray(cv2.cvtColor(image_with_text, cv2.COLOR_BGR2RGB))

    try:
        logo = Image.open(logo_path).convert("RGBA").resize((w//5, h//5))
        pil_image.paste(logo, (w - logo.width - 20, h - logo.height - 20), logo)
    except:
        print("⚠️ Error cargando el logo.")

    # ---- NIVEL 4: Texto cifrado en los metadatos EXIF ----
    encrypted_text = encrypt_text(watermark_text)

    # Verificar si la imagen tiene datos EXIF
    exif_data = pil_image.info.get("exif", b"")
    if exif_data:
        # Si tiene EXIF, cargarlo
        exif_dict = piexif.load(exif_data)
    else:
        # Si no tiene EXIF, crear un diccionario EXIF vacío
        exif_dict = piexif.load(piexif.dump({}))

    # Modificar el campo 'UserComment' dentro de ExifIFD con el texto cifrado
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = encrypted_text.encode("utf-8")
    exif_bytes = piexif.dump(exif_dict)

    # ---- NIVEL 5: Texto cifrado en los píxeles ----
    pil_image = embed_text_in_pixels(pil_image, encrypted_text)

    # Guardar la imagen final con los datos EXIF
    pil_image.save(output_image_path, "JPEG", exif=exif_bytes)
    print(f"✅ Imagen protegida con cifrado y marca de agua en {output_image_path}")

# ---- EJECUCIÓN ----
add_secure_watermark("dni1.jpeg", "dni_marcado.jpg", "USO PRIVADO", "logo.png")
