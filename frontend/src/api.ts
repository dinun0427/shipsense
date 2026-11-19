const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) throw new Error(`API error ${res.status}`);
  return res.json() as Promise<T>;
}

export type Factor = { feature: string; contribution: number; direction: string };

export type DelayResponse = {
  late_probability: number;
  risk_label: string;
  top_factors: Factor[];
  model_version: string;
};

export type ReviewResponse = { sentiment: string; confidence: number };

export type RatePoint = { key: string; late_rate: number; orders: number };

export const predictDelay = (body: object) =>
  request<DelayResponse>("/api/v1/predict-delay", {
    method: "POST",
    body: JSON.stringify(body),
  });

export const analyzeReview = (text: string) =>
  request<ReviewResponse>("/api/v1/analyze-review", {
    method: "POST",
    body: JSON.stringify({ text }),
  });

export const getLateRate = (by: "state" | "month") =>
  request<RatePoint[]>(`/api/v1/insights/late-rate?by=${by}`);
