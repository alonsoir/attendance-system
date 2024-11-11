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
const card_1 = require("@/components/ui/card");
const alert_1 = require("@/components/ui/alert");
const SERVICE_URLS = {
    claude: {
        status: 'https://status.anthropic.com',
        twitter: 'https://twitter.com/anthropic',
        docs: 'https://docs.anthropic.com',
    },
    meta: {
        status: 'https://developers.facebook.com/status',
        twitter: 'https://twitter.com/MetaPlatform',
        docs: 'https://developers.facebook.com/docs',
    }
};
const ServiceStatus = () => {
    const { t } = (0, react_i18next_1.useTranslation)();
    const [services, setServices] = (0, react_1.useState)([]);
    const [loading, setLoading] = (0, react_1.useState)(true);
    const [error, setError] = (0, react_1.useState)(null);
    const [lastUpdate, setLastUpdate] = (0, react_1.useState)(new Date());
    const fetchStatus = () => __awaiter(void 0, void 0, void 0, function* () {
        try {
            setLoading(true);
            const response = yield fetch('/api/v1/services/status');
            if (!response.ok)
                throw new Error('Error fetching service status');
            const data = yield response.json();
            setServices(data);
            setLastUpdate(new Date());
            setError(null);
        }
        catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
        finally {
            setLoading(false);
        }
    });
    (0, react_1.useEffect)(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 60000); // Actualizar cada minuto
        return () => clearInterval(interval);
    }, []);
    const handleRefresh = () => __awaiter(void 0, void 0, void 0, function* () {
        yield fetchStatus();
    });
    if (error) {
        return (<alert_1.Alert variant="destructive">
                <lucide_react_1.AlertTriangle className="h-4 w-4"/>
                <alert_1.AlertDescription>{error}</alert_1.AlertDescription>
            </alert_1.Alert>);
    }
    return (<card_1.Card>
            <card_1.CardHeader className="flex flex-row items-center justify-between">
                <card_1.CardTitle>{t('services.status')}</card_1.CardTitle>
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-gray-500">
                        {t('services.lastUpdate', {
            time: lastUpdate.toLocaleTimeString()
        })}
                    </span>
                    <button onClick={handleRefresh} disabled={loading} className="p-2 hover:bg-gray-100 rounded-full" aria-label={t('services.refresh')}>
                        <lucide_react_1.RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`}/>
                    </button>
                </div>
            </card_1.CardHeader>
            <card_1.CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {services.map((service) => (<div key={service.name} className="flex items-center justify-between p-4 bg-white rounded-lg border">
                            <div className="flex items-center space-x-4">
                                {service.status ? (<lucide_react_1.CheckCircle className="h-5 w-5 text-green-500"/>) : (<lucide_react_1.AlertTriangle className="h-5 w-5 text-red-500"/>)}
                                <div>
                                    <h3 className="font-semibold">
                                        {t(`services.names.${service.name}`)}
                                    </h3>
                                    <p className={`text-sm ${service.status ? 'text-green-600' : 'text-red-600'}`}>
                                        {t(service.status ? 'services.operational' : 'services.issues')}
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center space-x-2">
                                <a href={SERVICE_URLS[service.name].status} target="_blank" rel="noopener noreferrer" className="p-2 hover:bg-gray-100 rounded-full" aria-label={t('services.viewStatus')}>
                                    <lucide_react_1.ExternalLink className="h-4 w-4"/>
                                </a>
                                <a href={SERVICE_URLS[service.name].twitter} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:text-blue-600">
                                    {t('services.twitter')}
                                </a>
                            </div>
                        </div>))}
                </div>

                {services.some(s => !s.status) && (<alert_1.Alert className="mt-4">
                        <lucide_react_1.AlertTriangle className="h-4 w-4"/>
                        <alert_1.AlertDescription>
                            {t('services.issuesDetected')}
                        </alert_1.AlertDescription>
                    </alert_1.Alert>)}
            </card_1.CardContent>
        </card_1.Card>);
};
exports.default = ServiceStatus;
