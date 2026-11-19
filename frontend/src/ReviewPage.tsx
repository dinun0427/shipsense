import { useState } from "react";
import { analyzeReview, type ReviewResponse } from "./api";

export default function ReviewPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState<ReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      setResult(await analyzeReview(text));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section>
      <h2>Analyze a review</h2>
      <form onSubmit={submit} className="form">
        <label>
          Review text (Portuguese)
          <textarea
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="muito bom, chegou antes do prazo"
          />
        </label>
        <button disabled={!text.trim()}>Analyze</button>
      </form>
      {error && <p role="alert">Something went wrong: {error}</p>}
      {result && (
        <div className="card">
          <h3>{result.sentiment}</h3>
          <p>Confidence: {(result.confidence * 100).toFixed(0)}%</p>
        </div>
      )}
    </section>
  );
}
