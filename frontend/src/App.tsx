import { useState } from "react";
import InsightsPage from "./InsightsPage";
import PredictPage from "./PredictPage";
import ReviewPage from "./ReviewPage";

type Tab = "predict" | "reviews" | "insights";

export default function App() {
  const [tab, setTab] = useState<Tab>("predict");
  return (
    <main>
      <h1>ShipSense</h1>
      <nav>
        <button onClick={() => setTab("predict")} disabled={tab === "predict"}>Predict</button>
        <button onClick={() => setTab("reviews")} disabled={tab === "reviews"}>Reviews</button>
        <button onClick={() => setTab("insights")} disabled={tab === "insights"}>Insights</button>
      </nav>
      {tab === "predict" && <PredictPage />}
      {tab === "reviews" && <ReviewPage />}
      {tab === "insights" && <InsightsPage />}
    </main>
  );
}
