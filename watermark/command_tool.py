import cv2
import numpy as np
from PIL import Image
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import SHA256
import getpass
import argparse
import json
from datetime import datetime
import socket
import os
import platform
import hashlib
from typing import Dict, Any, Optional


class WatermarkMetadata:
    def __init__(self, text: str, owner: str, purpose: str = ""):
        self.text = text
        self.owner = owner
        self.purpose = purpose
        self.timestamp = datetime.now().isoformat()
        self.hostname = socket.gethostname()
        self.platform = platform.system()
        self.username = os.getlogin()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "owner": self.owner,
            "purpose": self.purpose,
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "platform": self.platform,
            "username": self.username
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(json_str: str) -> 'WatermarkMetadata':
        data = json.loads(json_str)
        metadata = WatermarkMetadata(data["text"], data["owner"], data["purpose"])
        metadata.timestamp = data["timestamp"]
        metadata.hostname = data["hostname"]
        metadata.platform = data["platform"]
        metadata.username = data["username"]
        return metadata


class WatermarkStyle:
    def __init__(self,
                 font: int = cv2.FONT_HERSHEY_DUPLEX,
                 color: tuple = (255, 255, 255),
                 opacity: float = 0.4,
                 font_scale: Optional[float] = None,
                 thickness: Optional[int] = None,
                 position: str = "center",
                 pattern: str = "diagonal",
                 border_color: tuple = (0, 0, 0)):
        self.font = font
        self.color = color
        self.opacity = opacity
        self.font_scale = font_scale
        self.thickness = thickness
        self.position = position
        self.pattern = pattern
        self.border_color = border_color


def calculate_image_hash(image: Image.Image) -> str:
    """Calcula un hash SHA-256 de la imagen."""
    img_array = np.array(image)
    return hashlib.sha256(img_array.tobytes()).hexdigest()


def validate_secret_key(key: bytes) -> bytes:
    if len(key) != 32:
        raise ValueError("La clave secreta debe tener exactamente 32 bytes.")
    return key


def encrypt_text(text: str, secret_key: bytes) -> str:
    cipher = AES.new(secret_key, AES.MODE_CBC, iv=secret_key[:16])
    encrypted_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
    return base64.b64encode(encrypted_bytes).decode()


def decrypt_text(encrypted_text: str, secret_key: bytes) -> Optional[str]:
    cipher = AES.new(secret_key, AES.MODE_CBC, iv=secret_key[:16])
    try:
        decrypted_bytes = unpad(cipher.decrypt(base64.b64decode(encrypted_text)), AES.block_size)
        return decrypted_bytes.decode()
    except ValueError as e:
        print(f"Error al desencriptar el texto: {e}")
        return None


def create_visible_watermark(image_shape: tuple, text: str, style: WatermarkStyle) -> np.ndarray:
    """Crea una marca de agua visible con estilo personalizado."""
    watermark = np.zeros(image_shape, dtype="uint8")
    height = image_shape[0]

    # Calcular escala de fuente y grosor si no se especifican
    font_scale = style.font_scale if style.font_scale else height / 500
    thickness = style.thickness if style.thickness else max(2, int(font_scale * 2))

    # Calcular tamaño y posición del texto
    (text_width, text_height), baseline = cv2.getTextSize(text, style.font, font_scale, thickness)

    # Determinar posición según la configuración
    if style.position == "center":
        x = (image_shape[1] - text_width) // 2
        y = (image_shape[0] + text_height) // 2
    elif style.position == "top":
        x = (image_shape[1] - text_width) // 2
        y = text_height + 20
    elif style.position == "bottom":
        x = (image_shape[1] - text_width) // 2
        y = image_shape[0] - 20

    # Dibujar borde del texto
    for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
        cv2.putText(watermark, text,
                    (x + dx, y + dy),
                    style.font, font_scale,
                    style.border_color,
                    thickness + 2,
                    cv2.LINE_AA)

    # Dibujar texto principal
    cv2.putText(watermark, text,
                (x, y),
                style.font, font_scale,
                style.color,
                thickness,
                cv2.LINE_AA)

    # Aplicar patrón si está especificado
    if style.pattern == "diagonal":
        angle = 30
        rows, cols = watermark.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
        rotated = cv2.warpAffine(watermark.copy(), M, (cols, rows))
        watermark = cv2.addWeighted(watermark, 1, rotated, 0.5, 0)
    elif style.pattern == "tile":
        # Crear patrón en mosaico
        for i in range(0, image_shape[0], text_height * 4):
            for j in range(0, image_shape[1], text_width * 2):
                cv2.putText(watermark, text,
                            (j, i + text_height),
                            style.font, font_scale * 0.5,
                            style.color,
                            thickness,
                            cv2.LINE_AA)

    return watermark


def add_watermark(input_image_path: str,
                  output_image_path: str,
                  metadata: WatermarkMetadata,
                  secret_key: bytes,
                  watermark_type: str = 'hidden',
                  style: Optional[WatermarkStyle] = None):
    """Añade marca de agua a la imagen con metadatos y verificación de integridad."""
    if not input_image_path.lower().endswith('.png'):
        raise ValueError("El archivo de entrada debe ser PNG")

    # Cargar imagen original
    original_image = Image.open(input_image_path)

    # Calcular hash de la imagen original
    original_hash = calculate_image_hash(original_image)

    # Añadir hash a los metadatos
    metadata_dict = metadata.to_dict()
    metadata_dict["original_hash"] = original_hash
    metadata_json = json.dumps(metadata_dict)

    if watermark_type in ['hidden', 'both']:
        # Aplicar marca de agua oculta con metadatos
        encrypted_text = encrypt_text(metadata_json, secret_key)
        processed_image = embed_text_in_pixels(original_image, encrypted_text)
    else:
        processed_image = original_image.copy()

    if watermark_type in ['visible', 'both']:
        # Aplicar marca de agua visible
        cv_image = cv2.cvtColor(np.array(processed_image), cv2.COLOR_RGB2BGR)
        style = style or WatermarkStyle()  # Usar estilo por defecto si no se proporciona
        watermark = create_visible_watermark(cv_image.shape, metadata.text, style)
        image_with_watermark = cv2.addWeighted(cv_image, 1, watermark, style.opacity, 0)
        processed_image = Image.fromarray(cv2.cvtColor(image_with_watermark, cv2.COLOR_BGR2RGB))

    # Guardar imagen procesada
    processed_image.save(output_image_path, 'PNG')
    print(f"✅ Imagen procesada guardada como {output_image_path}")
    return metadata_dict

def embed_text_in_pixels(image, encrypted_text):
    """ Oculta el texto cifrado en los píxeles (canal azul). """
    np_image = np.array(image)
    h, w, _ = np_image.shape
    text_bytes = encrypted_text.encode()

    for i in range(len(text_bytes)):
        x, y = random.randint(0, w - 1), random.randint(0, h - 1)
        np_image[y, x, 2] = (np_image[y, x, 2] & 0xF0) | (text_bytes[i] & 0x0F)

    return Image.fromarray(np_image)

def recover_watermark(input_image_path: str, secret_key: bytes) -> Optional[Dict[str, Any]]:
    """Recupera y verifica la marca de agua y los metadatos."""
    if not input_image_path.lower().endswith('.png'):
        raise ValueError("El archivo de entrada debe ser PNG")

    # Cargar imagen y extraer texto oculto
    image = Image.open(input_image_path)
    extracted_text = extract_text_from_pixels(image)
    decrypted_text = decrypt_text(extracted_text, secret_key)

    if not decrypted_text:
        return None

    # Recuperar metadatos
    try:
        metadata = json.loads(decrypted_text)
        original_hash = metadata.pop("original_hash", None)

        # Verificar integridad si existe el hash original
        if original_hash:
            current_hash = calculate_image_hash(image)
            metadata["integrity_verified"] = (original_hash == current_hash)

        return metadata
    except json.JSONDecodeError:
        print("❌ Error al decodificar los metadatos")
        return None


def main():
    parser = argparse.ArgumentParser(description="Herramienta avanzada para marcas de agua en imágenes PNG.")
    parser.add_argument('action', choices=['add', 'recover'],
                        help="Acción a realizar: 'add' para agregar marca de agua, 'recover' para recuperar.")
    parser.add_argument('input_image', help="Ruta del archivo de imagen PNG de entrada.")
    parser.add_argument('output_image', help="Ruta del archivo de imagen PNG de salida.")
    parser.add_argument('--type', choices=['hidden', 'visible', 'both'], default='hidden',
                        help="Tipo de marca de agua: 'hidden' (oculta), 'visible', o 'both' (ambas)")
    parser.add_argument('--owner', help="Propietario del documento", default=os.getlogin())
    parser.add_argument('--purpose', help="Propósito del documento", default="")
    parser.add_argument('--position', choices=['center', 'top', 'bottom'], default='center',
                        help="Posición de la marca de agua visible")
    parser.add_argument('--pattern', choices=['diagonal', 'tile', 'none'], default='diagonal',
                        help="Patrón de la marca de agua visible")
    parser.add_argument('--opacity', type=float, default=0.4,
                        help="Opacidad de la marca de agua visible (0.0 a 1.0)")
    args = parser.parse_args()

    # Solicitar clave secreta
    while True:
        secret_key = getpass.getpass("Introduce la clave secreta (32 bytes): ").encode('utf-8')
        try:
            validate_secret_key(secret_key)
            print("✅ Clave válida")
            break
        except ValueError as e:
            print(f"❌ {e}")

    if args.action == 'add':
        # Solicitar texto de la marca de agua
        watermark_text = input("Introduce el texto de la marca de agua: ")

        # Crear metadatos
        metadata = WatermarkMetadata(watermark_text, args.owner, args.purpose)

        # Crear estilo para marca de agua visible
        style = WatermarkStyle(
            opacity=args.opacity,
            position=args.position,
            pattern=args.pattern
        )

        # Añadir marca de agua
        result = add_watermark(
            args.input_image,
            args.output_image,
            metadata,
            secret_key,
            args.type,
            style
        )

        print("\nMetadatos añadidos:")
        for key, value in result.items():
            print(f"{key}: {value}")

    elif args.action == 'recover':
        # Recuperar marca de agua
        metadata = recover_watermark(args.input_image, secret_key)

        if metadata:
            print("\nMetadatos recuperados:")
            for key, value in metadata.items():
                print(f"{key}: {value}")
        else:
            print("❌ No se pudo recuperar la marca de agua")


if __name__ == "__main__":
    main()