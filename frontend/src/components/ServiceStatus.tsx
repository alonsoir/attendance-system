import { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Alert, AlertDescription } from "@/components/ui/Alert";

interface ServiceStatus {
  name: string;
  status: boolean;
  lastCheck: string;
  error?: string;
}

interface ServiceUrls {
  [key: string]: {
    status: string;
    twitter: string;
    docs: string;
  };
}

const SERVICE_URLS: ServiceUrls = {
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
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/v1/services/status");
      if (!response.ok) throw new Error("Error fetching service status");

      const data = await response.json();
      setServices(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 60000); // Actualizar cada minuto
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    await fetchStatus();
  };

  if (error) {
    return (
      <Alert variant="error">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>{t("services.status")}</CardTitle>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-500">
            {t("services.lastUpdate", {
              time: lastUpdate.toLocaleTimeString(),
            })}
          </span>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="p-2 hover:bg-gray-100 rounded-full"
            aria-label={t("services.refresh")}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {services.map((service) => (
            <div
              key={service.name}
              className="flex items-center justify-between p-4 bg-white rounded-lg border"
            >
              <div className="flex items-center space-x-4">
                {service.status ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                )}
                <div>
                  <h3 className="font-semibold">
                    {t(`services.names.${service.name}`)}
                  </h3>
                  <p
                    className={`text-sm ${
                      service.status ? "text-green-600" : "text-red-600"
                    }`}
                  >
                    {t(
                      service.status
                        ? "services.operational"
                        : "services.issues",
                    )}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <a
                  href={SERVICE_URLS[service.name].status}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 hover:bg-gray-100 rounded-full"
                  aria-label={t("services.viewStatus")}
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
                <a
                  href={SERVICE_URLS[service.name].twitter}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 hover:text-blue-600"
                >
                  {t("services.twitter")}
                </a>
              </div>
            </div>
          ))}
        </div>

        {services.some((s) => !s.status) && (
          <Alert className="mt-4">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{t("services.issuesDetected")}</AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
};

export default ServiceStatus;
