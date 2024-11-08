// Gestor de internacionalización
class I18nManager {
    constructor(config) {
        this.defaultLocale = config.defaultLocale;
        this.supportedLocales = config.supportedLocales;
        this.fallbackLocale = config.fallbackLocale;
        this.currentLocale = this.getInitialLocale();
    }

    getInitialLocale() {
        // Intentar obtener el idioma guardado
        const saved = localStorage.getItem('locale');
        if (saved && this.supportedLocales.includes(saved)) {
            return saved;
        }

        // Intentar usar el idioma del navegador
        const browser = navigator.language;
        if (this.supportedLocales.includes(browser)) {
            return browser;
        }

        // Intentar encontrar una coincidencia parcial (ej: 'es' para 'es-ES')
        const partial = this.supportedLocales.find(locale =>
            locale.startsWith(browser.split('-')[0])
        );
        if (partial) {
            return partial;
        }

        // Usar el idioma por defecto
        return this.defaultLocale;
    }

    setLocale(locale) {
        if (!this.supportedLocales.includes(locale)) {
            console.warn(`Locale ${locale} not supported, falling back to ${this.fallbackLocale}`);
            locale = this.fallbackLocale;
        }

        this.currentLocale = locale;
        document.documentElement.lang = locale;
        localStorage.setItem('locale', locale);
        this.updatePageTranslations();
    }

    t(key) {
        const keys = key.split('.');
        let value = window.i18n[this.currentLocale];

        for (const k of keys) {
            value = value?.[k];
        }

        if (value === undefined) {
            console.warn(`Translation key "${key}" not found for locale ${this.currentLocale}`);
            // Intentar en el idioma de fallback
            value = this.getFromFallback(key);
        }

        return value || key;
    }

    getFromFallback(key) {
        const keys = key.split('.');
        let value = window.i18n[this.fallbackLocale];

        for (const k of keys) {
            value = value?.[k];
        }

        return value;
    }

    updatePageTranslations() {
        document.querySelectorAll('[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.textContent = this.t(key);
        });

        // Actualizar meta tags
        document.querySelectorAll('meta[data-i18n]').forEach(element => {
            const key = element.getAttribute('data-i18n');
            element.setAttribute('content', this.t(key));
        });

        // Disparar evento de cambio de idioma
        window.dispatchEvent(new CustomEvent('localeChanged', {
            detail: { locale: this.currentLocale }
        }));
    }
}

// Inicializar el gestor de i18n
window.i18nManager = new I18nManager(window.i18nConfig);