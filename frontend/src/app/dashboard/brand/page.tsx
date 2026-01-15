"use client";

import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { brandApi } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import Link from "next/link";
import { Button, Input, Card } from "@/components/ui";

export default function BrandProfilePage() {
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
        },
    });

    // Add competitor mutation
    const addCompetitorMutation = useMutation({
        mutationFn: brandApi.addCompetitor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["brandProfile"] });
            setNewCompetitor("");
        },
    });

    // Remove competitor mutation
    const removeCompetitorMutation = useMutation({
        mutationFn: brandApi.removeCompetitor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["brandProfile"] });
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
            <div className="min-h-screen bg-[#FDFCF8]">
                <Navbar />
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-24">
                    <div className="text-slate-900">Loading...</div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-[#FDFCF8]">
            <Navbar />

            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 pt-28">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-4 mb-4">
                        <Link href="/experiments" className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-900 transition-colors">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                            </svg>
                            Back to Dashboard
                        </Link>
                    </div>
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">Brand Profile</h1>
                    <p className="text-slate-500">
                        Manage your brand information and competitors. Your brand name will be used in all experiments.
                    </p>
                </div>

                {/* Brand Information Card */}
                <Card className="bg-white border-stone-200 p-6 mb-6">
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-xl font-semibold text-slate-900">Brand Information</h2>
                        {!isEditing && (
                            <Button onClick={() => setIsEditing(true)} variant="outline">
                                Edit
                            </Button>
                        )}
                    </div>

                    {isEditing ? (
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Brand Name *
                                </label>
                                <Input
                                    value={formData.brand_name}
                                    onChange={(e) => setFormData({ ...formData, brand_name: e.target.value })}
                                    placeholder="e.g., Salesforce"
                                    required
                                    className="bg-white border-stone-200 !text-slate-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={formData.brand_description}
                                    onChange={(e) => setFormData({ ...formData, brand_description: e.target.value })}
                                    placeholder="What does your company do?"
                                    rows={3}
                                    className="w-full px-4 py-2 bg-white border border-stone-200 rounded-lg text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Website
                                </label>
                                <Input
                                    value={formData.brand_website}
                                    onChange={(e) => setFormData({ ...formData, brand_website: e.target.value })}
                                    placeholder="https://yourcompany.com"
                                    type="url"
                                    className="bg-white border-stone-200 !text-slate-900"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-2">
                                    Industry
                                </label>
                                <select
                                    value={formData.brand_industry}
                                    onChange={(e) => setFormData({ ...formData, brand_industry: e.target.value })}
                                    className="w-full px-4 py-2 bg-white border border-stone-200 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    <option value="">Select industry</option>
                                    <option value="SaaS">SaaS</option>
                                    <option value="E-commerce">E-commerce</option>
                                    <option value="Healthcare">Healthcare</option>
                                    <option value="Finance">Finance</option>
                                    <option value="Education">Education</option>
                                    <option value="Marketing">Marketing</option>
                                    <option value="Technology">Technology</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>

                            <div className="flex gap-3 pt-4">
                                <Button type="submit" disabled={updateMutation.isPending}>
                                    {updateMutation.isPending ? "Saving..." : "Save Changes"}
                                </Button>
                                <Button
                                    type="button"
                                    variant="outline"
                                    onClick={() => setIsEditing(false)}
                                >
                                    Cancel
                                </Button>
                            </div>
                        </form>
                    ) : (
                        <div className="space-y-4">
                            <div>
                                <div className="text-sm text-slate-500">Brand Name</div>
                                <div className="text-lg text-slate-900 font-medium">
                                    {profile?.brand_name || "Not set"}
                                </div>
                            </div>

                            {profile?.brand_description && (
                                <div>
                                    <div className="text-sm text-slate-500">Description</div>
                                    <div className="text-slate-900">{profile.brand_description}</div>
                                </div>
                            )}

                            {profile?.brand_website && (
                                <div>
                                    <div className="text-sm text-slate-500">Website</div>
                                    <a
                                        href={profile.brand_website}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-blue-600 hover:text-blue-700"
                                    >
                                        {profile.brand_website}
                                    </a>
                                </div>
                            )}

                            {profile?.brand_industry && (
                                <div>
                                    <div className="text-sm text-slate-500">Industry</div>
                                    <div className="text-slate-900">{profile.brand_industry}</div>
                                </div>
                            )}
                        </div>
                    )}
                </Card>

                {/* Competitors Card */}
                <Card className="bg-white border-stone-200 p-6">
                    <h2 className="text-xl font-semibold text-slate-900 mb-4">Competitors</h2>
                    <p className="text-slate-500 text-sm mb-4">
                        Add competitors to track in your experiments. You can add up to 10 competitors.
                    </p>

                    {/* Add Competitor */}
                    <div className="flex gap-3 mb-6">
                        <Input
                            value={newCompetitor}
                            onChange={(e) => setNewCompetitor(e.target.value)}
                            placeholder="e.g., HubSpot"
                            onKeyPress={(e) => e.key === "Enter" && handleAddCompetitor()}
                            className="bg-white border-stone-200 !text-slate-900 flex-1"
                        />
                        <Button
                            onClick={handleAddCompetitor}
                            disabled={!newCompetitor.trim() || addCompetitorMutation.isPending}
                        >
                            Add
                        </Button>
                    </div>

                    {/* Competitors List */}
                    <div className="space-y-2">
                        {profile?.brand_competitors?.length === 0 ? (
                            <div className="text-slate-400 text-sm">No competitors added yet</div>
                        ) : (
                            profile?.brand_competitors?.map((competitor: string) => (
                                <div
                                    key={competitor}
                                    className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-stone-200"
                                >
                                    <span className="text-slate-900">{competitor}</span>
                                    <button
                                        onClick={() => removeCompetitorMutation.mutate(competitor)}
                                        className="text-red-600 hover:text-red-700 text-sm"
                                    >
                                        Remove
                                    </button>
                                </div>
                            ))
                        )}
                    </div>
                </Card>
            </div>
        </div>
    );
}
