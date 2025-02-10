from PIL import Image, ImageDraw, ImageFont, ExifTags, TiffImagePlugin


def add_secure_watermark(input_image_path, output_image_path, watermark_text, logo_path):
    """Añade una marca de agua con un logo y texto, manteniendo los metadatos EXIF correctamente."""

    # Cargar la imagen original
    pil_image = Image.open(input_image_path).convert("RGB")

    # Extraer metadatos EXIF si existen
    exif_data = pil_image.info.get("exif")

    # Convertir EXIF a bytes si es un diccionario
    if isinstance(exif_data, dict):
        exif_bytes = TiffImagePlugin.ImageFileDirectory_v2()
        for key, value in exif_data.items():
            exif_bytes[key] = value
        exif_data = exif_bytes.tobytes()

    # Obtener tamaño de la imagen
    width, height = pil_image.size
    draw = ImageDraw.Draw(pil_image)

    # Cargar logo y redimensionarlo si es necesario
    logo = Image.open(logo_path).convert("RGBA")
    logo_width = width // 6  # El logo tendrá 1/6 del ancho de la imagen
    logo_height = int((logo_width / logo.width) * logo.height)
    logo = logo.resize((logo_width, logo_height))

    # Posicionar el logo en la esquina inferior derecha
    logo_x = width - logo_width - 10
    logo_y = height - logo_height - 10
    pil_image.paste(logo, (logo_x, logo_y), logo)

    # Definir fuente y tamaño del texto
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()

    # Medir el tamaño del texto y colocarlo en la parte inferior izquierda
    bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = 10
    text_y = height - text_height - 10

    # Dibujar el texto con sombra para mayor visibilidad
    shadow_offset = 2
    draw.text((text_x + shadow_offset, text_y + shadow_offset), watermark_text, font=font, fill="black")
    draw.text((text_x, text_y), watermark_text, font=font, fill="white")

    # Guardar la imagen con la marca de agua y los metadatos EXIF corregidos
    pil_image.save(output_image_path, "JPEG", exif=exif_data)

    print(f"✅ Imagen guardada con marca de agua: {output_image_path}")


# Ejemplo de uso
add_secure_watermark("dni1.jpeg", "dni_marcado.jpg", "USO PRIVADO", "logo.png")
