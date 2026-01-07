/**
 * API Client for Echo AI Backend
 *
 * This module provides typed API clients for interacting with the FastAPI backend.
 * All endpoints use the BASE_URL from environment variables.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://echo-ai-production.up.railway.app";
const API_PREFIX = "/api/v1";

/**
 * Generic fetch wrapper with authentication and error handling
 */
async function apiFetch<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;

    const headers: HeadersInit = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${BASE_URL}${API_PREFIX}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "An error occurred" }));
        throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
}

/**
 * Authentication API
 */
export const authApi = {
    /**
     * Register a new user account
     */
    async register(email: string, password: string, fullName: string) {
        return apiFetch("/auth/register", {
            method: "POST",
            body: JSON.stringify({
                email,
                password,
                full_name: fullName,
            }),
        });
    },

    /**
     * Login with email and password
     */
    async login(email: string, password: string) {
        return apiFetch<{ access_token: string; refresh_token: string; token_type: string }>(
            "/auth/login",
            {
                method: "POST",
                body: JSON.stringify({ email, password }),
            }
        );
    },

    /**
     * Get current user information
     */
    async me() {
        return apiFetch("/auth/me", {
            method: "GET",
        });
    },

    /**
     * Refresh access token
     */
    async refresh(refreshToken: string) {
        return apiFetch<{ access_token: string; refresh_token: string; token_type: string }>(
            "/auth/refresh",
            {
                method: "POST",
                body: JSON.stringify({ refresh_token: refreshToken }),
            }
        );
    },
};

/**
 * Experiments API
 */
export const experimentsApi = {
    /**
     * Create a new experiment
     */
    async create(data: {
        prompt: string;
        target_brand: string;
        provider: string;
        iterations?: number;
        temperature?: number;
        model?: string;
        competitor_brands?: string[];
        domain_whitelist?: string[];
        system_prompt?: string;
        max_concurrency?: number;
        is_recurring?: boolean;
        frequency?: string;
    }) {
        return apiFetch("/experiments", {
            method: "POST",
            body: JSON.stringify(data),
        });
    },

    /**
     * Get experiment by ID
     */
    async get(experimentId: string) {
        return apiFetch(`/experiments/${experimentId}`, {
            method: "GET",
        });
    },

    /**
     * List experiments with pagination
     */
    async list(limit: number = 10, offset: number = 0) {
        return apiFetch<{ experiments: any[]; total: number; limit: number; offset: number }>(
            `/experiments?limit=${limit}&offset=${offset}`,
            {
                method: "GET",
            }
        );
    },

    /**
     * Get detailed experiment results
     */
    async getDetails(experimentId: string) {
        return apiFetch(`/experiments/${experimentId}/detail`, {
            method: "GET",
        });
    },

    /**
     * Get visibility report for experiment
     */
    async getReport(experimentId: string) {
        return apiFetch(`/experiments/${experimentId}/report`, {
            method: "GET",
        });
    },
};

/**
 * Dashboard API
 */
export const dashboardApi = {
    /**
     * Get aggregated dashboard statistics
     */
    async getStats() {
        return apiFetch<{
            total_experiments: number;
            completed_experiments: number;
            avg_visibility_score: number;
            share_of_voice: Array<{ brand: string; percentage: number }>;
            visibility_trend: Array<{ date: string; visibility_score: number }>;
        }>("/dashboard/stats", {
            method: "GET",
        });
    },
};

/**
 * Billing API
 */
export const billingApi = {
    /**
     * Get pricing tiers
     */
    async getPricingTiers() {
        return apiFetch("/billing/pricing-tiers", {
            method: "GET",
        });
    },

    /**
     * Create checkout session
     */
    async createCheckoutSession(tierId: string) {
        return apiFetch<{ checkout_url: string }>("/billing/create-checkout-session", {
            method: "POST",
            body: JSON.stringify({ tier_id: tierId }),
        });
    },

    /**
     * Get user subscription
     */
    async getSubscription() {
        return apiFetch("/billing/subscription", {
            method: "GET",
        });
    },

    /**
     * Cancel subscription
     */
    async cancelSubscription() {
        return apiFetch("/billing/cancel-subscription", {
            method: "POST",
        });
    },

    /**
     * Get usage/quota information
     */
    async getUsage() {
        return apiFetch<{ used: number; quota: number; remaining: number }>("/billing/usage", {
            method: "GET",
        });
    },
};

/**
 * Health check API (not under /api/v1 prefix)
 */
export const healthApi = {
    /**
     * Get system health status
     */
    async check() {
        const response = await fetch(`${BASE_URL}/health`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json() as Promise<{
            status: string;
            version: string;
            environment: string;
            services: {
                redis: string;
                database: string;
            };
        }>;
    },
};
