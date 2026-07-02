// Change this to your laptop's LAN IP when using Expo Go on your phone
// Run `ip -4 addr show` to find your current IP if it changes
export const API_BASE_URL = 'http://192.168.1.5:8000';

export interface RegulatoryUpdate {
  id: string;
  source: 'RBI' | 'SEBI';
  feedKind: string;
  channelTitle: string;
  title: string;
  summary: string;
  url: string;
  rawPublishedAt: string;
  publishedAt: string;
  affected_entities: string;
  regulatory_impact: 'High' | 'Medium' | 'Low' | string;
  raw_text: string;
  created_at: string;
  score?: number;
}

export async function fetchUpdates(limit: number = 50): Promise<RegulatoryUpdate[]> {
  const res = await fetch(`${API_BASE_URL}/api/updates?limit=${limit}`);
  if (!res.ok) throw new Error(`Failed to fetch updates: ${res.status}`);
  return res.json();
}

export async function searchUpdates(query: string): Promise<RegulatoryUpdate[]> {
  const res = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error(`Search failed: ${res.status}`);
  return res.json();
}
