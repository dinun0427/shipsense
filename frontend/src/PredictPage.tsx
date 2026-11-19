import { useState } from "react";
import { predictDelay, type DelayResponse } from "./api";

const initial = {
  purchase_timestamp: "2018-05-10T10:00",
  approved_timestamp: "2018-05-10T10:30",
  estimated_delivery_date: "2018-05-25T00:00",
  customer_state: "AL",
  seller_state: "SP",
  category: "bed_bath_table",
  price_sum: 120,
  freight_sum: 25,
  weight_g: 1500,
  volume_cm3: 9000,
  distance_km: 2200,
};

type Field = keyof typeof initial;

export default function PredictPage() {
  const [form, setForm] = useState(initial);
  const [result, setResult] = useState<DelayResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const set = (k: Field, v: string) =>
    setForm((f) => ({ ...f, [k]: typeof initial[k] === "number" ? Number(v) : v }));

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(await predictDelay(form));
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h2>Predict delivery delay</h2>
      <form onSubmit={submit} className="form">
        {(Object.keys(form) as Field[]).map((k) => (
          <label key={k}>
            {k}
            <input
              value={form[k]}
              type={
                k.includes("timestamp") || k.includes("date")
                  ? "datetime-local"
                  : typeof initial[k] === "number"
                    ? "number"
                    : "text"
              }
              onChange={(e) => set(k, e.target.value)}
            />
          </label>
        ))}
        <button disabled={loading}>{loading ? "Predicting..." : "Predict"}</button>
      </form>
      {error && <p role="alert">Something went wrong: {error}</p>}
      {result && (
        <div className="card">
          <h3>Risk: {result.risk_label}</h3>
          <p>
            Risk score: {(result.late_probability * 100).toFixed(0)} / 100
            <br />
            <small>A ranking score, not a true probability of delay.</small>
          </p>
          <ul>
            {result.top_factors.map((f) => (
              <li key={f.feature}>
                {f.feature}: {f.direction}
              </li>
            ))}
          </ul>
          <small>Model {result.model_version}</small>
        </div>
      )}
    </section>
  );
}
