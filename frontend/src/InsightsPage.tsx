import { useEffect, useState } from "react";
import {
  Bar, BarChart, CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from "recharts";
import { getLateRate, type RatePoint } from "./api";

const MIN_ORDERS = 100; // ignore groups too small to trust

export default function InsightsPage() {
  const [byState, setByState] = useState<RatePoint[]>([]);
  const [byMonth, setByMonth] = useState<RatePoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getLateRate("state"), getLateRate("month")])
      .then(([s, m]) => {
        setByState(
          s.filter((p) => p.orders >= MIN_ORDERS).sort((a, b) => b.late_rate - a.late_rate),
        );
        setByMonth(m.filter((p) => p.orders >= MIN_ORDERS));
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  const pct = (v: number) => `${(v * 100).toFixed(1)}%`;

  if (error) return <p role="alert">Could not load insights: {error}</p>;
  return (
    <section>
      <h2>Late-delivery rate by customer state</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={byState}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="key" />
          <YAxis tickFormatter={(v: number) => pct(v)} />
          <Tooltip formatter={(v) => pct(Number(v))} />
          <Bar dataKey="late_rate" fill="#4f46e5" />
        </BarChart>
      </ResponsiveContainer>
      <h2>Late-delivery rate by month</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={byMonth}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="key" />
          <YAxis tickFormatter={(v: number) => pct(v)} />
          <Tooltip formatter={(v) => pct(Number(v))} />
          <Line dataKey="late_rate" stroke="#dc2626" dot={false} />
        </LineChart>
      </ResponsiveContainer>
      <small>Groups with fewer than {MIN_ORDERS} orders are hidden.</small>
    </section>
  );
}
