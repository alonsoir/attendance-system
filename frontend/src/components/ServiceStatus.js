var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { CheckCircle, AlertTriangle, ExternalLink, RefreshCw, } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
const SERVICE_URLS = {
    claude: {
        status: "https://status.anthropic.com",
        twitter: "https://twitter.com/anthropic",
        docs: "https://docs.anthropic.com",
    },
    meta: {
        status: "https://developers.facebook.com/status",
        twitter: "https://twitter.com/MetaPlatform",
        docs: "https://developers.facebook.com/docs",
    },
};
const ServiceStatus = () => {
    const { t } = useTranslation();
    const [services, setServices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(new Date());
    const fetchStatus = () => __awaiter(void 0, void 0, void 0, function* () {
        try {
            setLoading(true);
            const response = yield fetch("/api/v1/services/status");
            if (!response.ok)
                throw new Error("Error fetching service status");
            const data = yield response.json();
            setServices(data);
            setLastUpdate(new Date());
            setError(null);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        }
        finally {
            setLoading(false);
        }
    });
    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 60000); // Actualizar cada minuto
        return () => clearInterval(interval);
    }, []);
    const handleRefresh = () => __awaiter(void 0, void 0, void 0, function* () {
        yield fetchStatus();
    });
    if (error) {
        return (_jsxs(Alert, { variant: "destructive", children: [_jsx(AlertTriangle, { className: "h-4 w-4" }), _jsx(AlertDescription, { children: error })] }));
    }
    return (_jsxs(Card, { children: [_jsxs(CardHeader, { className: "flex flex-row items-center justify-between", children: [_jsx(CardTitle, { children: t("services.status") }), _jsxs("div", { className: "flex items-center space-x-4", children: [_jsx("span", { className: "text-sm text-gray-500", children: t("services.lastUpdate", {
                                    time: lastUpdate.toLocaleTimeString(),
                                }) }), _jsx("button", { onClick: handleRefresh, disabled: loading, className: "p-2 hover:bg-gray-100 rounded-full", "aria-label": t("services.refresh"), children: _jsx(RefreshCw, { className: `h-4 w-4 ${loading ? "animate-spin" : ""}` }) })] })] }), _jsxs(CardContent, { children: [_jsx("div", { className: "grid grid-cols-1 md:grid-cols-2 gap-4", children: services.map((service) => (_jsxs("div", { className: "flex items-center justify-between p-4 bg-white rounded-lg border", children: [_jsxs("div", { className: "flex items-center space-x-4", children: [service.status ? (_jsx(CheckCircle, { className: "h-5 w-5 text-green-500" })) : (_jsx(AlertTriangle, { className: "h-5 w-5 text-red-500" })), _jsxs("div", { children: [_jsx("h3", { className: "font-semibold", children: t(`services.names.${service.name}`) }), _jsx("p", { className: `text-sm ${service.status ? "text-green-600" : "text-red-600"}`, children: t(service.status
                                                        ? "services.operational"
                                                        : "services.issues") })] })] }), _jsxs("div", { className: "flex items-center space-x-2", children: [_jsx("a", { href: SERVICE_URLS[service.name].status, target: "_blank", rel: "noopener noreferrer", className: "p-2 hover:bg-gray-100 rounded-full", "aria-label": t("services.viewStatus"), children: _jsx(ExternalLink, { className: "h-4 w-4" }) }), _jsx("a", { href: SERVICE_URLS[service.name].twitter, target: "_blank", rel: "noopener noreferrer", className: "text-blue-500 hover:text-blue-600", children: t("services.twitter") })] })] }, service.name))) }), services.some((s) => !s.status) && (_jsxs(Alert, { className: "mt-4", children: [_jsx(AlertTriangle, { className: "h-4 w-4" }), _jsx(AlertDescription, { children: t("services.issuesDetected") })] }))] })] }));
};
export default ServiceStatus;
