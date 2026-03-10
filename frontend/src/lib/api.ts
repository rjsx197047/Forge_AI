const API_BASE = 'http://localhost:8000';

export async function getAgents() {
  try {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error('Error fetching agents:', error);
    return [];
  }
}

export async function createAgent(data: { name: string; role: string; model: string }) {
  try {
    const res = await fetch(`${API_BASE}/agents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error('Error creating agent:', error);
    throw error;
  }
}

export async function assignTask(data: { agent_id: string; task: string }) {
  try {
    const res = await fetch(`${API_BASE}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return await res.json();
  } catch (error) {
    console.error('Error assigning task:', error);
    throw error;
  }
}

export async function getOutputs(agent?: string) {
  try {
    const url = agent ? `${API_BASE}/outputs?agent_name=${agent}` : `${API_BASE}/outputs`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error('Error fetching outputs:', error);
    return [];
  }
}

export async function getOutputContent(agent: string, filename: string) {
  try {
    const res = await fetch(`${API_BASE}/outputs/${agent}/${filename}`);
    if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error('Error fetching output content:', error);
    return null;
  }
}