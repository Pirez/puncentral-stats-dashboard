import { useState } from 'react';
import { getGpt5MiniSummary } from '../services/openai';
import type { LastMatch } from '../types/api';

interface Props {
  lastMatch: LastMatch | null;
  apiKey: string;
}

export function GptSummaryPanel({ lastMatch, apiKey }: Props) {
  const [summary, setSummary] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!lastMatch) return;
    setLoading(true);
    setError(null);
    try {
      const result = await getGpt5MiniSummary(apiKey, lastMatch);
      setSummary(result);
    } catch (err: any) {
      setError(err.message || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ border: '1px solid #eee', borderRadius: 8, padding: 16, margin: '16px 0' }}>
      <h3>AI Match Summary (GPT-5 mini)</h3>
      <button onClick={handleGenerate} disabled={loading || !lastMatch}>
        {loading ? 'Generating...' : 'Generate Summary'}
      </button>
      {error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
      {summary && <div style={{ marginTop: 12, whiteSpace: 'pre-line' }}>{summary}</div>}
      {!lastMatch && <div style={{ color: '#888', marginTop: 8 }}>No match data available.</div>}
    </div>
  );
}
