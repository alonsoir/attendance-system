# Añadir marca de agua oculta con metadatos

    (attendance-system-py3.10) ┌<▸> ~/g/a/watermark 
    └➤ poetry run python command_tool.py add dni1.png output.png --type hidden --owner "Empresa SA" --purpose "Documento confidencial"
    
    Introduce la clave secreta (32 bytes): 
    ❌ La clave secreta debe tener exactamente 32 bytes.
    Introduce la clave secreta (32 bytes): 
    ✅ Clave válida
    Introduce el texto de la marca de agua: alonso
    ✅ Imagen procesada guardada como output.png
    
    Metadatos añadidos:
    text: alonso
    owner: Empresa SA
    purpose: Documento confidencial
    timestamp: 2025-02-10T13:01:48.192865
    hostname: MacBook-Pro-de-Alonso.local
    platform: Darwin
    username: root
    original_hash: d8df41615f3506287ea25a9a40663ca1025f903b5573a7013f3eec1025918def
    (attendance-system-py3.10) ┌<▸> ~/g/a/watermark 
    └➤ 
    
    Usé algo como MiSuperClaveSecretaParaDNI2025!!

# Añadir marca visible personalizada

    (attendance-system-py3.10) ┌<▸> ~/g/a/watermark 
    └➤ poetry run python command_tool.py add dni1.png output_visible.png --type visible --position top --pattern tile --opacity 0.3
    
    Introduce la clave secreta (32 bytes): 
    ✅ Clave válida
    Introduce el texto de la marca de agua: alonso
    ✅ Imagen procesada guardada como output_visible.png
    
    Metadatos añadidos:
    text: alonso
    owner: root
    purpose: 
    timestamp: 2025-02-10T13:05:34.503054
    hostname: MacBook-Pro-de-Alonso.local
    platform: Darwin
    username: root
    original_hash: d8df41615f3506287ea25a9a40663ca1025f903b5573a7013f3eec1025918def
    (attendance-system-py3.10) ┌<▸> ~/g/a/watermark 
    └➤ 
    

# Recuperar marca de agua y verificar integridad

Aquí hay algo raro, hay que mirarlo

    (attendance-system-py3.10) ┌<▸> ~/g/a/watermark 
    └➤ poetry run python command_tool.py recover output_visible.png output_recovered.png
    Introduce la clave secreta (32 bytes): 
    ✅ Clave válida
    Traceback (most recent call last):
      File "/Users/aironman/git/attendance_system/watermark/command_tool.py", line 316, in <module>
        main()
      File "/Users/aironman/git/attendance_system/watermark/command_tool.py", line 305, in main
        metadata = recover_watermark(args.input_image, secret_key)
      File "/Users/aironman/git/attendance_system/watermark/command_tool.py", line 225, in recover_watermark
        extracted_text = extract_text_from_pixels(image)
    NameError: name 'extract_text_from_pixels' is not defined
    (attendance-system-py3.10) ┌<▪> ~/g/a/watermark 
    └➤ 
    
