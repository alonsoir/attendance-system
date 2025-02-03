Para obtener el `GOOGLE_CSE_ID` (ID del motor de búsqueda personalizado de Google) y el `GOOGLE_API_KEY` (clave de API de Google), debes seguir estos pasos:

### 1. Crear una cuenta en la Consola de Google Cloud:
   - Ve a la [Google Cloud Console](https://console.cloud.google.com/).
   - Si no tienes una cuenta, crea una.
   - Una vez dentro, crea un proyecto nuevo.

### 2. Obtener la `GOOGLE_API_KEY`:
   - En la Consola de Google Cloud, en tu proyecto, ve a **APIs & Services > Credentials** (Credenciales).
   - Haz clic en **Create Credentials** (Crear credenciales) y selecciona **API key** (Clave de API).
   - Se generará una clave de API. Copia y guarda esta clave en un lugar seguro.

### 3. Crear un motor de búsqueda personalizado de Google:
   - Ve a [Google Custom Search Engine](https://cse.google.com/cse/).
   - Haz clic en **Create a custom search engine** (Crear un motor de búsqueda personalizado).
   - En el campo "Sites to search" (Sitios para buscar), puedes ingresar el dominio de tu sitio web o dejarlo en blanco para que busque en toda la web.
   - Completa los pasos y haz clic en **Create** (Crear).
   - Una vez creado el motor de búsqueda, ve a la **Control Panel** (Panel de control) de tu motor de búsqueda y copia el `CSE ID` (ID del motor de búsqueda personalizado), que será algo como `XXXXXXXXXXXXXXX:XXXXXXXXXXX`.

### 4. Configuración adicional (si es necesario):
   Si planeas usar el motor de búsqueda de Google con la API de búsqueda personalizada de Google (Custom Search JSON API), asegúrate de habilitar esa API en tu consola de Google Cloud:
   - Ve a **APIs & Services > Library** (Biblioteca).
   - Busca "Custom Search API" y habilítala.

### Resumen:
- **GOOGLE_API_KEY**: Generada desde la Consola de Google Cloud en la sección de credenciales.
- **GOOGLE_CSE_ID**: Copiado desde el panel de control del motor de búsqueda personalizado en la página de Google Custom Search.

¡Y listo! Con estos dos elementos, podrás hacer consultas de búsqueda utilizando la API de Google.