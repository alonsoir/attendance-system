<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title data-i18n="app.title">Sistema de Gestión de Asistencia</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
    <!-- Cargar traducciones -->
    <script src="/static/js/translations/en-US.js"></script>
    <script src="/static/js/translations/es-ES.js"></script>
    <script src="/static/js/i18n.js"></script>
    <style>
        .loading-spinner {
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        /* ... (resto de estilos) ... */
    </style>
</head>
<body class="bg-gray-100">
    <!-- Selector de idioma -->
    <div class="fixed top-4 right-4 z-50">
        <select id="language-selector" class="rounded-md border-gray-300 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50">
            <option value="es-ES" data-i18n="language.es">Español</option>
            <option value="en-US" data-i18n="language.en">English</option>
        </select>
    </div>

    <div id="root">
        <div class="flex justify-center items-center h-screen">
            <div class="text-center">
                <div class="loading-spinner text-4xl text-blue-500">
                    <i class="fas fa-circle-notch"></i>
                </div>
                <p class="mt-4" data-i18n="app.loading">Cargando...</p>
            </div>
        </div>
    </div>

    <!-- Overlay para notificaciones -->
    <div id="notification-overlay" class="fixed top-0 right-0 m-4"></div>

    <!-- Modal container -->
    <div id="modal-root"></div>

    <script>
        // Configuración inicial
        window.CONFIG = {
            API_URL: window.location.origin + '/api/v1',
            WS_URL: (window.location.protocol === 'https:' ? 'wss://' : 'ws://') + window.location.host + '/api/v1/ws',
            REFRESH_INTERVAL: 5000,
            DEFAULT_LANGUAGE: 'es-ES',
            SUPPORTED_LANGUAGES: ['en-US', 'es-ES']
        };

        // Inicializar i18n y actualizar textos
        function updatePageTexts() {
            document.querySelectorAll('[data-i18n]').forEach(element => {
                const key = element.getAttribute('data-i18n');
                element.textContent = window.i18n.t(key);
            });
        }

        // Configurar selector de idioma
        document.getElementById('language-selector').addEventListener('change', (e) => {
            window.i18n.setLanguage(e.target.value);
            updatePageTexts();
        });

        // Detectar idioma inicial y actualizar selector
        document.getElementById('language-selector').value = window.i18n.getCurrentLanguage();
        updatePageTexts();

        // Detector de estado de conexión
        function updateOnlineStatus() {
            const statusElement = document.getElementById('connection-status');
            if (statusElement) {
                const status = navigator.onLine ? 'status.online' : 'status.offline';
                statusElement.className = navigator.onLine ? 
                    'text-green-500' : 'text-red-500 notification-badge';
                statusElement.innerHTML = `<i class="fas fa-wifi"></i> ${window.i18n.t(status)}`;
            }
        }

        window.addEventListener('online', updateOnlineStatus);
        window.addEventListener('offline', updateOnlineStatus);

        // Manejador de errores global
        window.onerror = function(message, source, lineno, colno, error) {
            console.error('Error global:', { message, source, lineno, colno, error });
            // Mostrar notificación de error en el idioma actual
            showNotification(window.i18n.t('notifications.error'), message);
            return false;
        };

        // Mostrar notificación
        function showNotification(title, message) {
            const notification = document.createElement('div');
            notification.className = 'bg-white shadow-lg rounded-lg p-4 mb-4 border-l-4 border-red-500';
            notification.innerHTML = `
                <h4 class="font-bold">${title}</h4>
                <p>${message}</p>
            `;
            document.getElementById('notification-overlay').appendChild(notification);
            setTimeout(() => notification.remove(), 5000);
        }

        // Noscript fallback y mensaje de navegador no compatible se manejan dinámicamente
        if (![].includes) {
            document.getElementById('root').innerHTML = `
                <div class="flex justify-center items-center h-screen">
                    <div class="text-center p-4">
                        <h1 class="text-2xl font-bold mb-4">${window.i18n.t('errors.browserNotSupported')}</h1>
                        <p>${window.i18n.t('errors.browserUpdateMessage')}</p>
                    </div>
                </div>
            `;
        }
    </script>

    <!-- Scripts de la aplicación -->
    <script type="text/javascript" src="/static/js/app.js" defer></script>

    <!-- Portales para componentes flotantes -->
    <div id="tooltip-root"></div>
    <div id="dropdown-root"></div>
    <div id="dialog-root"></div>

    <!-- Noscript fallback -->
    <noscript>
        <div class="flex justify-center items-center h-screen">
            <div class="text-center p-4">
                <h1 class="text-2xl font-bold mb-4" data-i18n="errors.javascriptRequired">JavaScript es Necesario</h1>
                <p data-i18n="errors.javascriptMessage">Por favor, habilite JavaScript para utilizar esta aplicación.</p>
            </div>
        </div>
    </noscript>
</body>
</html>