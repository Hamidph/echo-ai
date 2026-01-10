"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { brandApi } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { useAuth } from "@/hooks/useAuth";
import { toast } from "react-hot-toast";
import Link from "next/link";

export default function BrandProfilePage() {
    const { user } = useAuth();
    const queryClient = useQueryClient();
    const [isEditing, setIsEditing] = useState(false);
    const [newCompetitor, setNewCompetitor] = useState("");

    // Form state
    const [formData, setFormData] = useState({
        brand_name: "",
        brand_description: "",
        brand_website: "",
        brand_industry: "",
        brand_target_keywords: [] as string[],
    });

    // Fetch brand profile
    const { data: profile, isLoading } = useQuery({
        queryKey: ["brandProfile"],
        queryFn: brandApi.getProfile,
        enabled: !!user,
    });

    // Initialize form when profile loads
    useEffect(() => {
        if (profile) {
            setFormData({
                brand_name: profile.brand_name || "",
                brand_description: profile.brand_description || "",
                brand_website: profile.brand_website || "",
                brand_industry: profile.brand_industry || "",
                brand_target_keywords: profile.brand_target_keywords || [],
            });
        }
    }, [profile]);

    // Update profile mutation
    const updateMutation = useMutation({
        mutationFn: brandApi.updateProfile,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["brandProfile"] });
            setIsEditing(false);
            toast.success("Brand profile updated!");
        },
        onError: (error: Error) => {
            toast.error(error.message || "Failed to update brand profile");
        },
    });

    // Add competitor mutation
    const addCompetitorMutation = useMutation({
        mutationFn: brandApi.addCompetitor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["brandProfile"] });
            setNewCompetitor("");
            toast.success("Competitor added!");
        },
        onError: (error: Error) => {
            toast.error(error.message || "Failed to add competitor");
        },
    });

    // Remove competitor mutation
    const removeCompetitorMutation = useMutation({
        mutationFn: brandApi.removeCompetitor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["brandProfile"] });
            toast.success("Competitor removed");
        },
        onError: (error: Error) => {
            toast.error(error.message || "Failed to remove competitor");
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        updateMutation.mutate({
            ...formData,
            brand_competitors: profile?.brand_competitors || [],
        });
    };

    const handleAddCompetitor = () => {
        if (newCompetitor.trim()) {
            addCompetitorMutation.mutate(newCompetitor.trim());
        }
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#030712]">
                <Navbar />
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
                    <div className="flex items-center justify-center h-64">
                        <div className="relative">
                            <div className="w-16 h-16 border-4 border-cyan-500/20 rounded-full" />
                            <div className="w-16 h-16 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin absolute inset-0" />
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#030712]">
            <Navbar />

            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
                {/* Breadcrumb */}
                <div className="mb-6">
                    <Link
                        href="/dashboard"
                        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-white transition-colors"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                        </svg>
                        Back to Dashboard
                    </Link>
                </div>

                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Brand Profile</h1>
                    <p className="text-gray-400">
                        Manage your brand information and competitors. Your brand name will be used in all experiments.
                    </p>
                </div>

                {/* Brand Information Card */}
                <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6 mb-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-white">Brand Information</h2>
                        {!isEditing && (
                            <button
                                onClick={() => setIsEditing(true)}
                                className="px-4 py-2 text-sm font-medium text-cyan-400 border border-cyan-500/30 rounded-lg hover:bg-cyan-500/10 transition-colors"
                            >
                                Edit
                            </button>
                        )}
                    </div>

                    {isEditing ? (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Brand Name <span className="text-rose-400">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={formData.brand_name}
                                    onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
                                    placeholder="e.g., Salesforce"
                                    required
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={formData.brand_description}
                                    onChange={(e) => setFormData({ ...formData, brand_description: e.target.value })}
                                    placeholder="What does your company do?"
                                    rows={3}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 resize-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Website
                                </label>
                                <input
                                    type="url"
                                    value={formData.brand_website}
                                    onChange={(e) => setFormData({ ...formData, brand_website: e.target.value })}
                                    placeholder="https://yourcompany.com"
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Industry
                                </label>
                                <select
                                    value={formData.brand_industry}
                                    onChange={(e) => setFormData({ ...formData, brand_industry: e.target.value })}
                                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-cyan-500/50 appearance-none"
                                >
                                    <option value="" className="bg-[#0a0f1a]">Select industry</option>
                                    <option value="SaaS" className="bg-[#0a0f1a]">SaaS</option>
                                    <option value="E-commerce" className="bg-[#0a0f1a]">E-commerce</option>
                                    <option value="Healthcare" className="bg-[#0a0f1a]">Healthcare</option>
                                    <option value="Finance" className="bg-[#0a0f1a]">Finance</option>
                                    <option value="Education" className="bg-[#0a0f1a]">Education</option>
                                    <option value="Marketing" className="bg-[#0a0f1a]">Marketing</option>
                                    <option value="Technology" className="bg-[#0a0f1a]">Technology</option>
                                    <option value="Other" className="bg-[#0a0f1a]">Other</option>
                                </select>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="submit"
                                    disabled={updateMutation.isPending || !formData.brand_name}
                                    className="px-6 py-2.5 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                                >
                                    {updateMutation.isPending ? "Saving..." : "Save Changes"}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setIsEditing(false)}
                                    className="px-6 py-2.5 text-sm font-medium text-gray-400 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            <div>
                                <div className="text-sm text-gray-500 mb-1">Brand Name</div>
                                <div className="text-lg text-white font-medium">
                                    {profile?.brand_name || (
                                        <span className="text-gray-500 italic">Not set - Click Edit to add your brand</span>
                                    )}
                                </div>
                            </div>
                            {profile?.brand_description && (
                                <div>
                                    <div className="text-sm text-gray-500 mb-1">Description</div>
                                    <div className="text-white">{profile.brand_description}</div>
                                </div>
                            )}
                            {profile?.brand_website && (
                                <div>
                                    <div className="text-sm text-gray-500 mb-1">Website</div>
                                    <a
                                        href={profile.brand_website}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-cyan-400 hover:text-cyan-300 transition-colors"
                                    >
                                        {profile.brand_website}
                                    </a>
                                </div>
                            )}
                            {profile?.brand_industry && (
                                <div>
                                    <div className="text-sm text-gray-500 mb-1">Industry</div>
                                    <div className="text-white">{profile.brand_industry}</div>
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Competitors Card */}
                <div className="bg-[#0a0f1a] border border-white/10 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-2">Competitors</h2>
                    <p className="text-gray-400 text-sm mb-6">
                        Add competitors to track in your experiments. You can add up to 10 competitors.
                    </p>

                    {/* Add Competitor */}
                    <div className="flex gap-3 mb-6">
                        <input
                            type="text"
                            value={newCompetitor}
                            onChange={(e) => setNewCompetitor(e.target.value)}
                            placeholder="e.g., HubSpot"
                            onKeyPress={(e) => e.key === "Enter" && (e.preventDefault(), handleAddCompetitor())}
                            className="flex-1 px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                        />
                        <button
                            onClick={handleAddCompetitor}
                            disabled={!newCompetitor.trim() || addCompetitorMutation.isPending || (profile?.brand_competitors?.length ?? 0) >= 10}
                            className="px-6 py-3 text-sm font-semibold text-white bg-gradient-to-r from-cyan-500 to-violet-500 rounded-lg hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                        >
                            {addCompetitorMutation.isPending ? "Adding..." : "Add"}
                        </button>
                    </div>

                    {/* Competitors List */}
                    <div className="space-y-2">
                        {!profile?.brand_competitors?.length ? (
                            <div className="text-gray-500 text-sm py-4 text-center border border-dashed border-white/10 rounded-lg">
                                No competitors added yet. Add your first competitor above.
                            </div>
                        ) : (
                            profile.brand_competitors.map((competitor: string) => (
                                <div
                                    key={competitor}
                                    className="flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 hover:border-white/10 transition-colors"
                                >
                                    <span className="text-white font-medium">{competitor}</span>
                                    <button
                                        onClick={() => removeCompetitorMutation.mutate(competitor)}
                                        disabled={removeCompetitorMutation.isPending}
                                        className="text-sm text-rose-400 hover:text-rose-300 transition-colors disabled:opacity-50"
                                    >
                                        Remove
                                    </button>
                                </div>
                            ))
                        )}
                    </div>

                    {(profile?.brand_competitors?.length ?? 0) >= 10 && (
                        <p className="mt-4 text-sm text-amber-400">
                            Maximum 10 competitors reached. Remove one to add more.
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
}
