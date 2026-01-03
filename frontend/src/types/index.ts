/**
 * TypeScript type definitions for AI Visibility platform
 */

export interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  role: string;
  pricing_tier: string;
  monthly_prompt_quota: number;
  prompts_used_this_month: number;
  created_at: string;
  last_login_at: string | null;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface APIKey {
  id: string;
  name: string;
  prefix: string;
  key?: string; // Only returned on creation
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
}

export interface UsageResponse {
  prompts_used: number;
  monthly_quota: number;
  remaining: number;
  percentage_used: number;
  pricing_tier: string;
}

export interface CheckoutSessionResponse {
  session_id: string;
  url: string;
}

export interface Experiment {
  id: string;
  prompt: string;
  target_brand: string;
  competitor_brands: string[] | null;
  config: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface BatchRun {
  id: string;
  provider: string;
  model: string;
  status: string;
  metrics: Record<string, any> | null;
  total_iterations: number;
  successful_iterations: number;
  failed_iterations: number;
  created_at: string;
}

export interface ExperimentDetail extends Experiment {
  batch_runs: BatchRun[];
}

export interface ExperimentReport {
  experiment_id: string;
  prompt: string;
  target_brand: string;
  results: {
    [provider: string]: {
      visibility_rate: number;
      share_of_voice: number;
      consistency_score: number;
      hallucination_rate?: number;
    };
  };
}

export type PricingTier = 'free' | 'starter' | 'pro' | 'enterprise';

export interface PricingPlan {
  tier: PricingTier;
  name: string;
  price: number;
  interval: 'month' | 'year';
  quota: number;
  features: string[];
}
