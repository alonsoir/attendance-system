import React, { Suspense, useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Loader2, Bell, Menu, X } from 'lucide-react';
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Alert, AlertDescription } from "@/components/ui/Alert";

// Lazy loading de componentes
const Dashboard = React.lazy(() => import('./components/Dashboard'));
const ServiceStatus = React.lazy(() => import('./components/ServiceStatus'));
const Settings = React.lazy(() => import('./components/Settings'));
const Profile = React.lazy(() => import('./components/Profile'));

interface Notification {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: Date;
}

const App = () => {
  const { t, i18n } = useTranslation();
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Verificar conexión con el backend
    const checkBackendStatus = async () => {
      try {
        const response = await fetch('/api/v1/health'); // Ruta de health-check en el backend
        if (response.ok) {
          setIsOnline(true); // Backend está online
          const ws = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws`
          );

          ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'notification') {
              setNotifications((prev) => [
                { id: crypto.randomUUID(), ...data.payload, timestamp: new Date() },
                ...prev,
              ].slice(0, 5)); // Mantener solo las 5 notificaciones más recientes
            }
          };

          ws.onerror = () => setIsOnline(false); // Si hay error en WebSocket, marcar offline

          // Cerrar WebSocket cuando el componente se desmonte
          return () => ws.close();
        } else {
          setIsOnline(false); // Si el backend no responde correctamente
        }
      } catch (error) {
        setIsOnline(false); // Si falla el fetch, marcar offline
      }
    };

    checkBackendStatus();

    // Configurar eventos de cambio de conexión de red
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Simular carga inicial
    setTimeout(() => setIsLoading(false), 1000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        {/* Barra de navegación superior */}
        <nav className="bg-white dark:bg-gray-800 shadow-sm fixed w-full z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setSidebarOpen(!isSidebarOpen)}
                  className="md:hidden"
                >
                  {isSidebarOpen ? <X /> : <Menu />}
                </Button>
                <div className="flex-shrink-0 flex items-center">
                  <span className="text-xl font-bold">{t('app.title')}</span>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Selector de idioma */}
                <select
                  value={i18n.language}
                  onChange={(e) => i18n.changeLanguage(e.target.value)}
                  className="form-select rounded-md border-gray-300 shadow-sm"
                >
                  <option value="es-ES">Español</option>
                  <option value="en-US">English</option>
                </select>

                {/* Campana de notificaciones */}
                <div className="relative">
                  <Button variant="ghost" size="icon" className="relative">
                    <Bell />
                    {notifications.length > 0 && (
                      <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Barra lateral */}
        <div className={`fixed inset-y-0 left-0 transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 transition duration-200 ease-in-out z-30 w-64 bg-white dark:bg-gray-800 shadow-lg`}>
          <div className="h-full flex flex-col">
            <div className="flex-1 py-4 overflow-y-auto">
              <nav className="px-2 space-y-1">
                {/* Enlaces de navegación */}
                {[
                  { name: 'dashboard', path: '/', icon: 'Home' },
                  { name: 'settings', path: '/settings', icon: 'Settings' },
                  { name: 'profile', path: '/profile', icon: 'User' }
                ].map(item => (
                  <Button
                    key={item.name}
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={() => {
                      // Implementar navegación
                      setSidebarOpen(false);
                    }}
                  >
                    {t(`navigation.${item.name}`)}
                  </Button>
                ))}
              </nav>
            </div>
          </div>
        </div>

        {/* Overlay para cerrar sidebar en móvil */}
        {isSidebarOpen && (
          <div
            className="fixed inset-0 bg-gray-600 bg-opacity-50 z-20 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Contenido principal */}
        <main className={`md:ml-64 pt-16 min-h-screen`}>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Alerta de estado offline */}
            {!isOnline && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>
                  {t('errors.offline')}
                </AlertDescription>
              </Alert>
            )}

            {/* Notificaciones */}
            <div className="fixed top-20 right-4 z-50 space-y-2 max-w-sm">
              {notifications.map(notification => (
                <Card key={notification.id} className="p-4 shadow-lg">
                  <h4 className="font-semibold">
                    {t(`notifications.${notification.type}`)}
                  </h4>
                  <p className="text-sm">{notification.message}</p>
                  <span className="text-xs text-gray-500">
                    {notification.timestamp.toLocaleTimeString()}
                  </span>
                </Card>
              ))}
            </div>

            {/* Rutas */}
            <Suspense fallback={
              <div className="flex justify-center items-center h-64">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
              </div>
            }>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/status" element={<ServiceStatus />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </div>
        </main>
      </div>
    </Router>
  );
};

export default App;
