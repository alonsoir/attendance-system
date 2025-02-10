from PIL import Image, ImageDraw, ImageFont

# Crear una imagen en blanco
width, height = 300, 100
image = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(image)

# Dibujar un rectángulo como fondo del logo
draw.rectangle([0, 0, width, height], fill="lightgray", outline="black")

# Intentar usar una fuente más llamativa, si está disponible
try:
    font = ImageFont.truetype("arial.ttf", 40)
except IOError:
    font = ImageFont.load_default()

# Agregar texto al logo
text = "LOGO"
bbox = draw.textbbox((0, 0), text, font=font)  # Obtener el tamaño del texto
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
text_x = (width - text_width) // 2
text_y = (height - text_height) // 2
draw.text((text_x, text_y), text, fill="black", font=font)

# Guardar el logo
image.save("logo.png")
print("✅ Logo generado: logo.png")
