import axios from 'axios';

const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';

export async function getGpt5MiniSummary(apiKey: string, lastMatch: any): Promise<string> {
  const systemPrompt = `You are an expert CS2 analyst. Summarize the following match in a concise, insightful way for a dashboard. Highlight key moments, player performance, and outcome.`;
  const userPrompt = `Match info: ${JSON.stringify(lastMatch)}`;

  const response = await axios.post(
    OPENAI_API_URL,
    {
      model: 'gpt-5-mini',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 200
    },
    {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      }
    }
  );
  return response.data.choices[0].message.content.trim();
}
// (Removed by request)

