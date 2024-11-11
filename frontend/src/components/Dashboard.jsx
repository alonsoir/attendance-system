"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const react_1 = __importStar(require("react"));
const react_i18next_1 = require("react-i18next");
const lucide_react_1 = require("lucide-react");
const ServiceStatus_1 = require("./ServiceStatus");
const card_1 = require("@/components/ui/card");
const table_1 = require("@/components/ui/table");
const Dashboard = () => {
    const { t } = (0, react_i18next_1.useTranslation)();
    const [interactions, setInteractions] = (0, react_1.useState)([]);
    const [loading, setLoading] = (0, react_1.useState)(true);
    const [error, setError] = (0, react_1.useState)(null);
    const [currentPage, setCurrentPage] = (0, react_1.useState)(1);
    const [totalPages, setTotalPages] = (0, react_1.useState)(1);
    const itemsPerPage = 10;
    const fetchData = () => __awaiter(void 0, void 0, void 0, function* () {
        try {
            setLoading(true);
            const response = yield fetch(`/api/v1/interactions?page=${currentPage}&limit=${itemsPerPage}`);
            if (!response.ok)
                throw new Error('Error fetching data');
            const data = yield response.json();
            setInteractions(data.items);
            setTotalPages(Math.ceil(data.total / itemsPerPage));
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
        finally {
            setLoading(false);
        }
    });
    (0, react_1.useEffect)(() => {
        fetchData();
        // Configurar WebSocket
        const ws = new WebSocket(`${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws`);
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'update') {
                fetchData();
            }
        };
        return () => ws.close();
    }, [currentPage]);
    const getSensitivityColor = (score) => {
        if (score >= 8)
            return 'text-red-500 bg-red-50';
        if (score >= 5)
            return 'text-yellow-500 bg-yellow-50';
        return 'text-green-500 bg-green-50';
    };
    const getStatusIcon = (status) => {
        switch (status) {
            case 'active':
                return <lucide_react_1.Clock className="h-5 w-5 text-yellow-500"/>;
            case 'resolved':
                return <lucide_react_1.CheckCircle className="h-5 w-5 text-green-500"/>;
            case 'critical':
                return <lucide_react_1.AlertCircle className="h-5 w-5 text-red-500"/>;
            default:
                return <lucide_react_1.UserX className="h-5 w-5 text-gray-500"/>;
        }
    };
    if (loading) {
        return (<div className="flex justify-center items-center h-screen">
                <lucide_react_1.RefreshCw className="h-8 w-8 animate-spin text-blue-500"/>
            </div>);
    }
    if (error) {
        return (<div className="p-4 bg-red-50 text-red-700 rounded-lg">
                <lucide_react_1.AlertCircle className="h-5 w-5 inline mr-2"/>
                {error}
            </div>);
    }
    return (<div className="container mx-auto p-4 space-y-6">
            <h1 className="text-3xl font-bold mb-8">{t('dashboard.title')}</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <card_1.Card>
                    <card_1.CardHeader>
                        <card_1.CardTitle>{t('dashboard.activeAbsences')}</card_1.CardTitle>
                    </card_1.CardHeader>
                    <card_1.CardContent>
                        <div className="text-2xl font-bold">
                            {interactions.filter(i => i.status === 'active').length}
                        </div>
                    </card_1.CardContent>
                </card_1.Card>

                <card_1.Card>
                    <card_1.CardHeader>
                        <card_1.CardTitle>{t('dashboard.criticalCases')}</card_1.CardTitle>
                    </card_1.CardHeader>
                    <card_1.CardContent>
                        <div className="text-2xl font-bold text-red-600">
                            {interactions.filter(i => i.sensitivity_score >= 8).length}
                        </div>
                    </card_1.CardContent>
                </card_1.Card>

                <card_1.Card>
                    <card_1.CardHeader>
                        <card_1.CardTitle>{t('dashboard.followUps')}</card_1.CardTitle>
                    </card_1.CardHeader>
                    <card_1.CardContent>
                        <div className="text-2xl font-bold text-yellow-600">
                            {interactions.filter(i => i.follow_up_required).length}
                        </div>
                    </card_1.CardContent>
                </card_1.Card>
            </div>

            <ServiceStatus_1.ServiceStatus />

            <card_1.Card>
                <card_1.CardHeader>
                    <card_1.CardTitle>{t('dashboard.recentInteractions')}</card_1.CardTitle>
                </card_1.CardHeader>
                <card_1.CardContent>
                    <table_1.Table>
                        <table_1.TableHeader>
                            <table_1.TableRow>
                                <table_1.TableHead>{t('dashboard.table.status')}</table_1.TableHead>
                                <table_1.TableHead>{t('dashboard.table.student')}</table_1.TableHead>
                                <table_1.TableHead>{t('dashboard.table.sensitivity')}</table_1.TableHead>
                                <table_1.TableHead>{t('dashboard.table.time')}</table_1.TableHead>
                                <table_1.TableHead>{t('dashboard.table.actions')}</table_1.TableHead>
                            </table_1.TableRow>
                        </table_1.TableHeader>
                        <table_1.TableBody>
                            {interactions.map((interaction) => (<table_1.TableRow key={interaction.id}>
                                    <table_1.TableCell>
                                        <div className="flex items-center">
                                            {getStatusIcon(interaction.status)}
                                            <span className="ml-2">
                                                {t(`status.${interaction.status}`)}
                                            </span>
                                        </div>
                                    </table_1.TableCell>
                                    <table_1.TableCell>{interaction.student_name}</table_1.TableCell>
                                    <table_1.TableCell>
                                        <span className={`px-2 py-1 rounded-full text-sm ${getSensitivityColor(interaction.sensitivity_score)}`}>
                                            {interaction.sensitivity_score}
                                        </span>
                                    </table_1.TableCell>
                                    <table_1.TableCell>
                                        {new Date(interaction.timestamp).toLocaleString()}
                                    </table_1.TableCell>
                                    <table_1.TableCell>
                                        <button className="text-blue-600 hover:text-blue-800" onClick={() => { }}>
                                            {t('actions.viewDetails')}
                                        </button>
                                    </table_1.TableCell>
                                </table_1.TableRow>))}
                        </table_1.TableBody>
                    </table_1.Table>

                    <div className="flex items-center justify-between mt-4">
                        <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1} className="flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50">
                            <lucide_react_1.ChevronLeft className="h-4 w-4 mr-2"/>
                            {t('pagination.previous')}
                        </button>
                        <span>
                            {t('pagination.page', { current: currentPage, total: totalPages })}
                        </span>
                        <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages} className="flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50">
                            {t('pagination.next')}
                            <lucide_react_1.ChevronRight className="h-4 w-4 ml-2"/>
                        </button>
                    </div>
                </card_1.CardContent>
            </card_1.Card>
        </div>);
};
exports.default = Dashboard;
