"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import Card, { CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Badge from "@/components/ui/Badge";

export default function SettingsPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("profile");

  const tabs = [
    { id: "profile", label: "Profile", icon: "👤" },
    { id: "security", label: "Security", icon: "🔒" },
    { id: "billing", label: "Billing", icon: "💳" },
    { id: "notifications", label: "Notifications", icon: "🔔" },
    { id: "api", label: "API Keys", icon: "🔑" },
  ];

  return (
    <div className="min-h-screen bg-[#030712] py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-display font-bold text-white mb-2">Settings</h1>
          <p className="text-gray-400">Manage your account settings and preferences</p>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <Card padding="sm">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      activeTab === tab.id
                        ? "bg-gradient-to-r from-cyan-500/10 to-violet-500/10 text-cyan-400 border border-cyan-500/20"
                        : "text-gray-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    <span className="text-lg">{tab.icon}</span>
                    {tab.label}
                  </button>
                ))}
              </nav>
            </Card>
          </div>

          {/* Content Area */}
          <div className="lg:col-span-3 space-y-6">
            {activeTab === "profile" && <ProfileSettings user={user} />}
            {activeTab === "security" && <SecuritySettings />}
            {activeTab === "billing" && <BillingSettings user={user} />}
            {activeTab === "notifications" && <NotificationSettings />}
            {activeTab === "api" && <APISettings />}
          </div>
        </div>
      </div>
    </div>
  );
}

function ProfileSettings({ user }: { user: any }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile Information</CardTitle>
        <CardDescription>Update your personal information and profile settings</CardDescription>
      </CardHeader>
      <CardContent>
        <form className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <Input
              label="Full Name"
              defaultValue={user?.full_name || ""}
              placeholder="John Doe"
            />
            <Input
              label="Email"
              type="email"
              defaultValue={user?.email || ""}
              placeholder="john@example.com"
              disabled
              helperText="Contact support to change your email"
            />
          </div>

          <Input
            label="Company"
            placeholder="Your Company Inc."
          />

          <div className="flex justify-end gap-3">
            <Button variant="secondary">Cancel</Button>
            <Button variant="primary">Save Changes</Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

function SecuritySettings() {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Change Password</CardTitle>
          <CardDescription>Ensure your account stays secure</CardDescription>
        </CardHeader>
        <CardContent>
          <form className="space-y-6">
            <Input
              label="Current Password"
              type="password"
              placeholder="••••••••"
            />
            <Input
              label="New Password"
              type="password"
              placeholder="••••••••"
              helperText="Must be at least 8 characters"
            />
            <Input
              label="Confirm New Password"
              type="password"
              placeholder="••••••••"
            />

            <div className="flex justify-end">
              <Button variant="primary">Update Password</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Two-Factor Authentication</CardTitle>
          <CardDescription>Add an extra layer of security to your account</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-white font-medium mb-1">2FA Status</p>
              <p className="text-sm text-gray-400">Not enabled</p>
            </div>
            <Button variant="outline">Enable 2FA</Button>
          </div>
        </CardContent>
      </Card>
    </>
  );
}

function BillingSettings({ user }: { user: any }) {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Manage your subscription and billing</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-start justify-between mb-6">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-2xl font-bold text-white">
                  {user?.pricing_tier || "FREE"} Plan
                </h3>
                <Badge variant="success">{user?.pricing_tier === "FREE" ? "Active" : "Premium"}</Badge>
              </div>
              <p className="text-gray-400">
                {user?.monthly_prompt_quota || 100} prompts per month
              </p>
            </div>
            {user?.pricing_tier === "FREE" && (
              <Button variant="primary">Upgrade Plan</Button>
            )}
          </div>

          {/* Usage Stats */}
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <p className="text-sm text-gray-400 mb-1">Prompts Used</p>
              <p className="text-2xl font-bold text-cyan-400">
                {user?.prompts_used_this_month || 0}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <p className="text-sm text-gray-400 mb-1">Remaining</p>
              <p className="text-2xl font-bold text-violet-400">
                {(user?.monthly_prompt_quota || 100) - (user?.prompts_used_this_month || 0)}
              </p>
            </div>
            <div className="p-4 bg-white/5 rounded-xl border border-white/10">
              <p className="text-sm text-gray-400 mb-1">Reset Date</p>
              <p className="text-lg font-medium text-white">
                {new Date(user?.quota_reset_date || Date.now()).toLocaleDateString()}
              </p>
            </div>
          </div>

          {user?.pricing_tier !== "FREE" && (
            <div className="pt-6 border-t border-white/10">
              <Button variant="danger" size="sm">Cancel Subscription</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </>
  );
}

function NotificationSettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Notification Preferences</CardTitle>
        <CardDescription>Choose what updates you want to receive</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {[
            { id: "experiments", label: "Experiment Completion", description: "Get notified when experiments finish running" },
            { id: "alerts", label: "Visibility Alerts", description: "Alerts when visibility drops significantly" },
            { id: "weekly", label: "Weekly Reports", description: "Weekly summary of your brand performance" },
            { id: "updates", label: "Product Updates", description: "News about new features and improvements" },
          ].map((setting) => (
            <div key={setting.id} className="flex items-start justify-between p-4 bg-white/5 rounded-xl border border-white/10">
              <div className="flex-1">
                <h4 className="text-white font-medium mb-1">{setting.label}</h4>
                <p className="text-sm text-gray-400">{setting.description}</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer ml-4">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-cyan-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-cyan-500"></div>
              </label>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function APISettings() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>API Keys</CardTitle>
        <CardDescription>Manage your API keys for programmatic access</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-6">
          <Button variant="primary">Generate New API Key</Button>
        </div>

        <div className="space-y-4">
          <div className="p-4 bg-white/5 rounded-xl border border-white/10">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="text-white font-medium">Production Key</h4>
                <p className="text-sm text-gray-400">Created on Jan 1, 2026</p>
              </div>
              <Badge variant="success">Active</Badge>
            </div>
            <div className="flex items-center gap-3">
              <code className="flex-1 bg-black/30 px-4 py-2 rounded-lg text-sm text-cyan-400 font-mono">
                sk_live_••••••••••••••••
              </code>
              <Button variant="ghost" size="sm">Copy</Button>
              <Button variant="danger" size="sm">Revoke</Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
