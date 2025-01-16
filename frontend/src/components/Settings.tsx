import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";

interface SettingsProps {}

const Settings: React.FC<SettingsProps> = () => {
  const [settings, setSettings] = React.useState({
    notifications: true,
    darkMode: false,
    language: "en",
    timezone: "UTC",
  });

  const handleSave = () => {
    // TODO: Implement settings save logic
    console.log("Settings saved:", settings);
  };

  return (
    <div className="container mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.notifications}
                  onChange={(e) =>
                    setSettings({
                      ...settings,
                      notifications: e.target.checked,
                    })
                  }
                />
                <span>Enable Notifications</span>
              </label>
            </div>

            <div>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={settings.darkMode}
                  onChange={(e) =>
                    setSettings({ ...settings, darkMode: e.target.checked })
                  }
                />
                <span>Dark Mode</span>
              </label>
            </div>

            <div>
              <label>Language</label>
              <select
                value={settings.language}
                onChange={(e) =>
                  setSettings({ ...settings, language: e.target.value })
                }
                className="block w-full mt-1 rounded-md border-gray-300"
              >
                <option value="en">English</option>
                <option value="es">Español</option>
              </select>
            </div>

            <div>
              <label>Timezone</label>
              <select
                value={settings.timezone}
                onChange={(e) =>
                  setSettings({ ...settings, timezone: e.target.value })
                }
                className="block w-full mt-1 rounded-md border-gray-300"
              >
                <option value="UTC">UTC</option>
                <option value="EST">EST</option>
                <option value="PST">PST</option>
              </select>
            </div>

            <Button onClick={handleSave}>Save Settings</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Settings;
