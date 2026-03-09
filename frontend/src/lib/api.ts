const API_BASE = 'http://localhost:8000';

export async function getAgents() {
  const res = await fetch(`${API_BASE}/agents`);
  return res.json();
}

export async function createAgent(data: { name: string; role: string; model: string }) {
  const res = await fetch(`${API_BASE}/agents`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function assignTask(data: { agent_id: string; task: string }) {
  const res = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function getOutputs(agent?: string) {
  const url = agent ? `${API_BASE}/outputs?agent_name=${agent}` : `${API_BASE}/outputs`;
  const res = await fetch(url);
  return res.json();
}

export async function getOutputContent(agent: string, filename: string) {
  const res = await fetch(`${API_BASE}/outputs/${agent}/${filename}`);
  return res.json();
}