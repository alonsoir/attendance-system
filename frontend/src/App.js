import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { Suspense, useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Loader2, Bell, Menu, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
// Lazy loading de componentes
const Dashboard = React.lazy(() => import("./components/Dashboard"));
const ServiceStatus = React.lazy(() => import("./components/ServiceStatus"));
const Settings = React.lazy(() => import("./components/Settings"));
const Profile = React.lazy(() => import("./components/Profile"));
const App = () => {
    const { t, i18n } = useTranslation();
    const [isSidebarOpen, setSidebarOpen] = useState(false);
    const [notifications, setNotifications] = useState([]);
    const [isOnline, setIsOnline] = useState(navigator.onLine);
    const [isLoading, setIsLoading] = useState(true);
    useEffect(() => {
        // Verificar el estado de la conexión
        const handleOnline = () => setIsOnline(true);
        const handleOffline = () => setIsOnline(false);
        window.addEventListener("online", handleOnline);
        window.addEventListener("offline", handleOffline);
        // Configurar WebSocket para notificaciones
        const ws = new WebSocket(`${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/v1/ws`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "notification") {
                setNotifications((prev) => [
                    Object.assign(Object.assign({ id: crypto.randomUUID() }, data.payload), { timestamp: new Date() }),
                    ...prev,
                ].slice(0, 5)); // Mantener solo las 5 notificaciones más recientes
            }
        };
        // Simular carga inicial
        setTimeout(() => setIsLoading(false), 1000);
        return () => {
            window.removeEventListener("online", handleOnline);
            window.removeEventListener("offline", handleOffline);
            ws.close();
        };
    }, []);
    if (isLoading) {
        return (_jsx("div", { className: "flex h-screen items-center justify-center", children: _jsx(Loader2, { className: "h-8 w-8 animate-spin text-blue-500" }) }));
    }
    return (_jsx(Router, { children: _jsxs("div", { className: "min-h-screen bg-gray-50 dark:bg-gray-900", children: [_jsx("nav", { className: "bg-white dark:bg-gray-800 shadow-sm fixed w-full z-10", children: _jsx("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8", children: _jsxs("div", { className: "flex justify-between h-16", children: [_jsxs("div", { className: "flex", children: [_jsx(Button, { variant: "ghost", size: "icon", onClick: () => setSidebarOpen(!isSidebarOpen), className: "md:hidden", children: isSidebarOpen ? _jsx(X, {}) : _jsx(Menu, {}) }), _jsx("div", { className: "flex-shrink-0 flex items-center", children: _jsx("span", { className: "text-xl font-bold", children: t("app.title") }) })] }), _jsxs("div", { className: "flex items-center space-x-4", children: [_jsxs("select", { value: i18n.language, onChange: (e) => i18n.changeLanguage(e.target.value), className: "form-select rounded-md border-gray-300 shadow-sm", children: [_jsx("option", { value: "es-ES", children: "Espa\u00F1ol" }), _jsx("option", { value: "en-US", children: "English" })] }), _jsx("div", { className: "relative", children: _jsxs(Button, { variant: "ghost", size: "icon", className: "relative", children: [_jsx(Bell, {}), notifications.length > 0 && (_jsx("span", { className: "absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500" }))] }) })] })] }) }) }), _jsx("div", { className: `fixed inset-y-0 left-0 transform ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"} md:translate-x-0 transition duration-200 ease-in-out z-30 w-64 bg-white dark:bg-gray-800 shadow-lg`, children: _jsx("div", { className: "h-full flex flex-col", children: _jsx("div", { className: "flex-1 py-4 overflow-y-auto", children: _jsx("nav", { className: "px-2 space-y-1", children: [
                                    { name: "dashboard", path: "/", icon: "Home" },
                                    { name: "settings", path: "/settings", icon: "Settings" },
                                    { name: "profile", path: "/profile", icon: "User" },
                                ].map((item) => (_jsx(Button, { variant: "ghost", className: "w-full justify-start", onClick: () => {
                                        // Implementar navegación
                                        setSidebarOpen(false);
                                    }, children: t(`navigation.${item.name}`) }, item.name))) }) }) }) }), isSidebarOpen && (_jsx("div", { className: "fixed inset-0 bg-gray-600 bg-opacity-50 z-20 md:hidden", onClick: () => setSidebarOpen(false) })), _jsx("main", { className: `md:ml-64 pt-16 min-h-screen`, children: _jsxs("div", { className: "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8", children: [!isOnline && (_jsx(Alert, { variant: "destructive", className: "mb-4", children: _jsx(AlertDescription, { children: t("errors.offline") }) })), _jsx("div", { className: "fixed top-20 right-4 z-50 space-y-2 max-w-sm", children: notifications.map((notification) => (_jsxs(Card, { className: "p-4 shadow-lg", children: [_jsx("h4", { className: "font-semibold", children: t(`notifications.${notification.type}`) }), _jsx("p", { className: "text-sm", children: notification.message }), _jsx("span", { className: "text-xs text-gray-500", children: notification.timestamp.toLocaleTimeString() })] }, notification.id))) }), _jsx(Suspense, { fallback: _jsx("div", { className: "flex justify-center items-center h-64", children: _jsx(Loader2, { className: "h-8 w-8 animate-spin text-blue-500" }) }), children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(Dashboard, {}) }), _jsx(Route, { path: "/status", element: _jsx(ServiceStatus, {}) }), _jsx(Route, { path: "/settings", element: _jsx(Settings, {}) }), _jsx(Route, { path: "/profile", element: _jsx(Profile, {}) }), _jsx(Route, { path: "*", element: _jsx(Navigate, { to: "/", replace: true }) })] }) })] }) })] }) }));
};
export default App;
