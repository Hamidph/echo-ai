"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Navbar } from "@/components/Navbar";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "react-hot-toast";
import { useRouter } from "next/navigation";

// Admin API client
const adminApi = {
  async getConfig() {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/admin/config`, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("Failed to fetch config");
    return response.json();
  },

  async updateConfig(config: any) {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/admin/config`, {
      method: "PUT",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(config),
    });
    if (!response.ok) throw new Error("Failed to update config");
    return response.json();
  },

  async getStats() {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/admin/stats`, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("Failed to fetch stats");
    return response.json();
  },

  async getUsers(limit = 50, offset = 0) {
    const token = localStorage.getItem("token");
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ""}/api/v1/admin/users?limit=${limit}&offset=${offset}`, {
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("Failed to fetch users");
    return response.json();
  },
};

export default function AdminPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"config" | "stats" | "users">("config");

  // Check if user is admin
  if (user && (user as any).role !== "admin") {
    router.push("/dashboard");
    return null;
  }

  const { data: config, isLoading: configLoading } = useQuery({
    queryKey: ["adminConfig"],
    queryFn: adminApi.getConfig,
    enabled: !!user,
  });

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["adminStats"],
    queryFn: adminApi.getStats,
    enabled: !!user && activeTab === "stats",
  });

  const { data: users, isLoading: usersLoading } = useQuery({
    queryKey: ["adminUsers"],
    queryFn: () => adminApi.getUsers(),
    enabled: !!user && activeTab === "users",
  });

  const updateConfigMutation = useMutation({
    mutationFn: adminApi.updateConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["adminConfig"] });
      toast.success("Configuration updated successfully!");
    },
    onError: () => {
      toast.error("Failed to update configuration");
    },
  });

  const [editedConfig, setEditedConfig] = useState<any>(null);

  const handleSaveConfig = () => {
    if (editedConfig) {
      updateConfigMutation.mutate(editedConfig);
    }
  };

  if (!user || (user as any).role !== "admin") {
    return (
      <div className="min-h-screen bg-[#030712] flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Access Denied</h1>
          <p className="text-gray-400">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#030712]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
        {/* Header */}
        <div className="mb-8">
          <h1 className="font-display text-3xl font-bold text-white mb-2">
            Admin Dashboard
          </h1>
          <p className="text-gray-400">
            Manage system configuration, users, and platform settings
          </p>
        </div>

        {/* Tabs */}
        <div className="flex items-center gap-4 mb-8 border-b border-white/10">
          <button
            onClick={() => setActiveTab("config")}
            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === "config"
                ? "text-cyan-400 border-cyan-400"
                : "text-gray-400 border-transparent hover:text-white"
            }`}
          >
            System Configuration
          </button>
          <button
            onClick={() => setActiveTab("stats")}
            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === "stats"
                ? "text-cyan-400 border-cyan-400"
                : "text-gray-400 border-transparent hover:text-white"
            }`}
          >
            Platform Statistics
          </button>
          <button
            onClick={() => setActiveTab("users")}
            className={`px-4 py-3 text-sm font-medium transition-colors border-b-2 ${
              activeTab === "users"
                ? "text-cyan-400 border-cyan-400"
                : "text-gray-400 border-transparent hover:text-white"
            }`}
          >
            User Management
          </button>
        </div>

        {/* System Configuration Tab */}
        {activeTab === "config" && (
          <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">System Configuration</h2>
              <button
                onClick={handleSaveConfig}
                disabled={!editedConfig || updateConfigMutation.isPending}
                className="px-4 py-2 bg-cyan-500 text-white rounded-lg hover:bg-cyan-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {updateConfigMutation.isPending ? "Saving..." : "Save Changes"}
              </button>
            </div>

            {configLoading ? (
              <div className="flex justify-center py-8">
                <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
              </div>
            ) : config ? (
              <div className="space-y-6">
                {/* Default Iterations */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Default Iterations
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={editedConfig?.default_iterations ?? config.default_iterations}
                    onChange={(e) => setEditedConfig({ ...config, ...editedConfig, default_iterations: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500/50"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Default number of iterations for new experiments (1-100)
                  </p>
                </div>

                {/* Default Frequency */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Default Recurring Frequency
                  </label>
                  <select
                    value={editedConfig?.default_frequency ?? config.default_frequency}
                    onChange={(e) => setEditedConfig({ ...config, ...editedConfig, default_frequency: e.target.value })}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500/50"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                  <p className="mt-1 text-xs text-gray-500">
                    Default frequency for recurring experiments
                  </p>
                </div>

                {/* Default Recurring */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Enable Recurring by Default
                    </label>
                    <p className="text-xs text-gray-500">
                      Whether new experiments should be recurring by default
                    </p>
                  </div>
                  <button
                    onClick={() => setEditedConfig({ ...config, ...editedConfig, default_recurring: !(editedConfig?.default_recurring ?? config.default_recurring) })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      (editedConfig?.default_recurring ?? config.default_recurring) ? "bg-cyan-500" : "bg-gray-600"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        (editedConfig?.default_recurring ?? config.default_recurring) ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>

                {/* Max Iterations */}
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Maximum Iterations Per Experiment
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="1000"
                    value={editedConfig?.max_iterations_per_experiment ?? config.max_iterations_per_experiment}
                    onChange={(e) => setEditedConfig({ ...config, ...editedConfig, max_iterations_per_experiment: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500/50"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Maximum allowed iterations per experiment (1-1000)
                  </p>
                </div>

                {/* Enable Recurring Experiments */}
                <div className="flex items-center justify-between">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-1">
                      Enable Recurring Experiments
                    </label>
                    <p className="text-xs text-gray-500">
                      Allow users to create recurring experiments platform-wide
                    </p>
                  </div>
                  <button
                    onClick={() => setEditedConfig({ ...config, ...editedConfig, enable_recurring_experiments: !(editedConfig?.enable_recurring_experiments ?? config.enable_recurring_experiments) })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      (editedConfig?.enable_recurring_experiments ?? config.enable_recurring_experiments) ? "bg-cyan-500" : "bg-gray-600"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        (editedConfig?.enable_recurring_experiments ?? config.enable_recurring_experiments) ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>

                {/* Maintenance Mode */}
                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <div>
                    <label className="block text-sm font-medium text-rose-400 mb-1">
                      Maintenance Mode
                    </label>
                    <p className="text-xs text-gray-500">
                      Put the platform in maintenance mode (blocks all non-admin access)
                    </p>
                  </div>
                  <button
                    onClick={() => setEditedConfig({ ...config, ...editedConfig, maintenance_mode: !(editedConfig?.maintenance_mode ?? config.maintenance_mode) })}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      (editedConfig?.maintenance_mode ?? config.maintenance_mode) ? "bg-rose-500" : "bg-gray-600"
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        (editedConfig?.maintenance_mode ?? config.maintenance_mode) ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        )}

        {/* Platform Statistics Tab */}
        {activeTab === "stats" && (
          <div className="space-y-6">
            {statsLoading ? (
              <div className="flex justify-center py-8">
                <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
              </div>
            ) : stats ? (
              <>
                {/* Stats Grid */}
                <div className="grid md:grid-cols-4 gap-4">
                  <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-1">Total Users</p>
                    <p className="text-3xl font-bold text-white">{stats.total_users}</p>
                    <p className="text-xs text-emerald-400 mt-1">{stats.active_users} active</p>
                  </div>
                  <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-1">Total Experiments</p>
                    <p className="text-3xl font-bold text-white">{stats.total_experiments}</p>
                    <p className="text-xs text-cyan-400 mt-1">{stats.completed_experiments} completed</p>
                  </div>
                  <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-1">Running Now</p>
                    <p className="text-3xl font-bold text-white">{stats.running_experiments}</p>
                    <p className="text-xs text-amber-400 mt-1">In progress</p>
                  </div>
                  <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                    <p className="text-sm text-gray-400 mb-1">Recurring</p>
                    <p className="text-3xl font-bold text-white">{stats.recurring_experiments}</p>
                    <p className="text-xs text-violet-400 mt-1">{stats.active_recurring_experiments} active</p>
                  </div>
                </div>

                {/* Current Config Display */}
                <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Current Configuration</h3>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-400">Default Iterations:</span>
                      <span className="text-white ml-2 font-medium">{stats.system_config.default_iterations}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Default Frequency:</span>
                      <span className="text-white ml-2 font-medium capitalize">{stats.system_config.default_frequency}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Max Iterations:</span>
                      <span className="text-white ml-2 font-medium">{stats.system_config.max_iterations_per_experiment}</span>
                    </div>
                    <div>
                      <span className="text-gray-400">Recurring Enabled:</span>
                      <span className={`ml-2 font-medium ${stats.system_config.enable_recurring_experiments ? "text-emerald-400" : "text-rose-400"}`}>
                        {stats.system_config.enable_recurring_experiments ? "Yes" : "No"}
                      </span>
                    </div>
                  </div>
                </div>
              </>
            ) : null}
          </div>
        )}

        {/* User Management Tab */}
        {activeTab === "users" && (
          <div className="bg-[#0a0f1a] border border-white/10 rounded-xl overflow-hidden">
            {usersLoading ? (
              <div className="flex justify-center py-8">
                <div className="w-8 h-8 border-4 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin" />
              </div>
            ) : users && users.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Email</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Tier</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Quota</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {users.map((user: any) => (
                      <tr key={user.id} className="hover:bg-white/5">
                        <td className="px-6 py-4 text-sm text-white">{user.email}</td>
                        <td className="px-6 py-4 text-sm text-gray-400">{user.full_name || "-"}</td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            user.role === "admin" ? "bg-rose-500/20 text-rose-400" :
                            user.role === "user" ? "bg-cyan-500/20 text-cyan-400" :
                            "bg-gray-500/20 text-gray-400"
                          }`}>
                            {user.role}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-400 capitalize">{user.pricing_tier}</td>
                        <td className="px-6 py-4 text-sm text-gray-400">
                          {user.prompts_used_this_month} / {user.monthly_prompt_quota}
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            user.is_active ? "bg-emerald-500/20 text-emerald-400" : "bg-rose-500/20 text-rose-400"
                          }`}>
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">No users found</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
