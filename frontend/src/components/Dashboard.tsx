import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import {
    AlertCircle,
    CheckCircle,
    Clock,
    UserX,
    RefreshCw,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { ServiceStatus } from './ServiceStatus';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface Interaction {
    id: number;
    timestamp: string;
    student_name: string;
    status: string;
    sensitivity_score: number;
    follow_up_required: boolean;
    tutor_phone: string;
}

const Dashboard = () => {
    const { t } = useTranslation();
    const [interactions, setInteractions] = useState<Interaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const itemsPerPage = 10;

    const fetchData = async () => {
        try {
            setLoading(true);
            const response = await fetch(`/api/v1/interactions?page=${currentPage}&limit=${itemsPerPage}`);
            if (!response.ok) throw new Error('Error fetching data');

            const data = await response.json();
            setInteractions(data.items);
            setTotalPages(Math.ceil(data.total / itemsPerPage));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();

        // Configurar WebSocket
        const ws = new WebSocket(
            `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1/ws`
        );

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'update') {
                fetchData();
            }
        };

        return () => ws.close();
    }, [currentPage]);

    const getSensitivityColor = (score: number): string => {
        if (score >= 8) return 'text-red-500 bg-red-50';
        if (score >= 5) return 'text-yellow-500 bg-yellow-50';
        return 'text-green-500 bg-green-50';
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'active':
                return <Clock className="h-5 w-5 text-yellow-500" />;
            case 'resolved':
                return <CheckCircle className="h-5 w-5 text-green-500" />;
            case 'critical':
                return <AlertCircle className="h-5 w-5 text-red-500" />;
            default:
                return <UserX className="h-5 w-5 text-gray-500" />;
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center h-screen">
                <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 text-red-700 rounded-lg">
                <AlertCircle className="h-5 w-5 inline mr-2" />
                {error}
            </div>
        );
    }

    return (
        <div className="container mx-auto p-4 space-y-6">
            <h1 className="text-3xl font-bold mb-8">{t('dashboard.title')}</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <Card>
                    <CardHeader>
                        <CardTitle>{t('dashboard.activeAbsences')}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            {interactions.filter(i => i.status === 'active').length}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>{t('dashboard.criticalCases')}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-600">
                            {interactions.filter(i => i.sensitivity_score >= 8).length}
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>{t('dashboard.followUps')}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-yellow-600">
                            {interactions.filter(i => i.follow_up_required).length}
                        </div>
                    </CardContent>
                </Card>
            </div>

            <ServiceStatus />

            <Card>
                <CardHeader>
                    <CardTitle>{t('dashboard.recentInteractions')}</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>{t('dashboard.table.status')}</TableHead>
                                <TableHead>{t('dashboard.table.student')}</TableHead>
                                <TableHead>{t('dashboard.table.sensitivity')}</TableHead>
                                <TableHead>{t('dashboard.table.time')}</TableHead>
                                <TableHead>{t('dashboard.table.actions')}</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {interactions.map((interaction) => (
                                <TableRow key={interaction.id}>
                                    <TableCell>
                                        <div className="flex items-center">
                                            {getStatusIcon(interaction.status)}
                                            <span className="ml-2">
                                                {t(`status.${interaction.status}`)}
                                            </span>
                                        </div>
                                    </TableCell>
                                    <TableCell>{interaction.student_name}</TableCell>
                                    <TableCell>
                                        <span className={`px-2 py-1 rounded-full text-sm ${
                                            getSensitivityColor(interaction.sensitivity_score)
                                        }`}>
                                            {interaction.sensitivity_score}
                                        </span>
                                    </TableCell>
                                    <TableCell>
                                        {new Date(interaction.timestamp).toLocaleString()}
                                    </TableCell>
                                    <TableCell>
                                        <button
                                            className="text-blue-600 hover:text-blue-800"
                                            onClick={() => {/* Implementar vista detalle */}}
                                        >
                                            {t('actions.viewDetails')}
                                        </button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>

                    <div className="flex items-center justify-between mt-4">
                        <button
                            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                            disabled={currentPage === 1}
                            className="flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50"
                        >
                            <ChevronLeft className="h-4 w-4 mr-2" />
                            {t('pagination.previous')}
                        </button>
                        <span>
                            {t('pagination.page', { current: currentPage, total: totalPages })}
                        </span>
                        <button
                            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                            disabled={currentPage === totalPages}
                            className="flex items-center px-3 py-2 rounded-md bg-white border disabled:opacity-50"
                        >
                            {t('pagination.next')}
                            <ChevronRight className="h-4 w-4 ml-2" />
                        </button>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};

export default Dashboard;