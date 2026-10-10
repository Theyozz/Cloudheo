import { authFetch, parseErrorDetail } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type ApiRecommendation = {
  resource_id: string;
  resource_type: "EC2" | "EBS" | "RDS" | "ELASTIC_IP" | "SAVINGS_PLAN";
  category: string;
  current_cost: number;
  estimated_optimized_cost: number;
  estimated_savings: number;
  risk: "LOW" | "MEDIUM" | "HIGH";
  confidence: number;
  title: string;
  description: string;
};

export type DashboardSummary = {
  connected: boolean;
  aws_account_id: string | null;
  monthly_spend: number;
  potential_savings: number;
  savings_percent: number;
  recommendations_count: number;
  savings_by_category: { category: string; amount: number }[];
  top_recommendations: ApiRecommendation[];
};

export async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const res = await authFetch("/dashboard/summary");
  if (!res.ok) throw new Error(await parseErrorDetail(res));
  return res.json();
}

export type MonthlySpendRange = "under_10k" | "10k_50k" | "50k_200k" | "over_200k";

export async function requestAudit(payload: {
  name: string;
  company_name: string;
  work_email: string;
  monthly_spend_range: MonthlySpendRange;
  message?: string;
}): Promise<void> {
  const res = await fetch(`${API_URL}/audit-leads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await parseErrorDetail(res));
}

export async function connectAwsAccount(params: {
  role_arn: string;
  external_id?: string;
  region?: string;
}): Promise<void> {
  const res = await authFetch("/aws/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!res.ok) throw new Error(await parseErrorDetail(res));
}

export async function disconnectAwsAccount(): Promise<void> {
  const res = await authFetch("/aws/connect", { method: "DELETE" });
  if (!res.ok) throw new Error(await parseErrorDetail(res));
}

export async function explainRecommendation(recommendation: ApiRecommendation): Promise<string> {
  const res = await authFetch("/ai/explain", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ recommendation }),
  });
  if (!res.ok) throw new Error(await parseErrorDetail(res));
  const body = await res.json();
  return body.explanation;
}
