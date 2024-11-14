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
import { AlertCircle, CheckCircle, Clock, UserX, RefreshCw, ChevronLeft, ChevronRight, } from "lucide-react";
import { ServiceStatus } from "./ServiceStatus";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, } from "@/components/ui/table";
const Dashboard = () => {
    const { t } = useTranslation();
    const [interactions, setInteractions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const itemsPerPage = 10;
    const fetchData = () => __awaiter(void 0, void 0, void 0, function* () {
        try {
            setLoading(true);
            const response = yield fetch(`/api/v1/interactions?page=${currentPage}&limit=${itemsPerPage}`);
            if (!response.ok)
                throw new Error("Error fetching data");
            const data = yield response.json();
            setInteractions(data.items);
            setTotalPages(Math.ceil(data.total / itemsPerPage));
        }
        catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error");
        }
        finally {
            setLoading(false);
        }
    });
    useEffect(() => {
        fetchData();
        // Configurar WebSocket
        const ws = new WebSocket(`${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/api/v1/ws`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === "update") {
                fetchData();
            }
        };
        return () => ws.close();
    }, [currentPage]);
    const getSensitivityColor = (score) => {
        if (score >= 8)
            return "text-red-500 bg-red-50";
        if (score >= 5)
            return "text-yellow-500 bg-yellow-50";
        return "text-green-500 bg-green-50";
    };
    const getStatusIcon = (status) => {
        switch (status) {
            case "active":
                return _jsx(Clock, { className: "h-5 w-5 text-yellow-500" });
            case "resolved":
                return _jsx(CheckCircle, { className: "h-5 w-5 text-green-500" });
            case "critical":
                return _jsx(AlertCircle, { className: "h-5 w-5 text-red-500" });
            default:
                return _jsx(UserX, { className: "h-5 w-5 text-gray-500" });
        }
    };
    if (loading) {
        return (_jsx("div", { className: "flex justify-center items-center h-screen", children: _jsx(RefreshCw, { className: "h-8 w-8 animate-spin text-blue-500" }) }));
    }
    if (error) {
        return (_jsxs("div", { className: "p-4 bg-red-50 text-red-700 rounded-lg", children: [_jsx(AlertCircle, { className: "h-5 w-5 inline mr-2" }), error] }));
    }
    return (_jsxs("div", { className: "container mx-auto p-4 space-y-6", children: [_jsx("h1", { className: "text-3xl font-bold mb-8", children: t("dashboard.title") }), _jsxs("div", { className: "grid grid-cols-1 md:grid-cols-3 gap-4 mb-6", children: [_jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: t("dashboard.activeAbsences") }) }), _jsx(CardContent, { children: _jsx("div", { className: "text-2xl font-bold", children: interactions.filter((i) => i.status === "active").length }) })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: t("dashboard.criticalCases") }) }), _jsx(CardContent, { children: _jsx("div", { className: "text-2xl font-bold text-red-600", children: interactions.filter((i) => i.sensitivity_score >= 8).length }) })] }), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: t("dashboard.followUps") }) }), _jsx(CardContent, { children: _jsx("div", { className: "text-2xl font-bold text-yellow-600", children: interactions.filter((i) => i.follow_up_required).length }) })] })] }), _jsx(ServiceStatus, {}), _jsxs(Card, { children: [_jsx(CardHeader, { children: _jsx(CardTitle, { children: t("dashboard.recentInteractions") }) }), _jsxs(CardContent, { children: [_jsxs(Table, { children: [_jsx(TableHeader, { children: _jsxs(TableRow, { children: [_jsx(TableHead, { children: t("dashboard.table.status") }), _jsx(TableHead, { children: t("dashboard.table.student") }), _jsx(TableHead, { children: t("dashboard.table.sensitivity") }), _jsx(TableHead, { children: t("dashboard.table.time") }), _jsx(TableHead, { children: t("dashboard.table.actions") })] }) }), _jsx(TableBody, { children: interactions.map((interaction) => (_jsxs(TableRow, { children: [_jsx(TableCell, { children: _jsxs("div", { className: "flex items-center", children: [getStatusIcon(interaction.status), _jsx("span", { className: "ml-2", children: t(`status.${interaction.status}`) })] }) }), _jsx(TableCell, { children: interaction.student_name }), _jsx(TableCell, { children: _jsx("span", { className: `px-2 py-1 rounded-full text-sm ${getSensitivityColor(interaction.sensitivity_score)}`, children: interaction.sensitivity_score }) }), _jsx(TableCell, { children: new Date(interaction.timestamp).toLocaleString() }), _jsx(TableCell, { children: _jsx("button", { className: "text-blue-600 hover:text-blue-800", onClick: () => {
                                                            /* Implementar vista detalle */
                                                        }, children: t("actions.viewDetails") }) })] }, interaction.id))) })] }), _jsxs("div", { className: "flex items-center justify-between mt-4", children: [_jsxs("button", { onClick: () => setCurrentPage((p) => Math.max(1, p - 1)), disabled: currentPage === 1, className: "flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50", children: [_jsx(ChevronLeft, { className: "h-4 w-4 mr-2" }), t("pagination.previous")] }), _jsx("span", { children: t("pagination.page", {
                                            current: currentPage,
                                            total: totalPages,
                                        }) }), _jsxs("button", { onClick: () => setCurrentPage((p) => Math.min(totalPages, p + 1)), disabled: currentPage === totalPages, className: "flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50", children: [t("pagination.next"), _jsx(ChevronRight, { className: "h-4 w-4 ml-2" })] })] })] })] })] }));
};
export default Dashboard;
