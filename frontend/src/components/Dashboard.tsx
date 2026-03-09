'use client';

import { useState, useEffect } from 'react';
import { getAgents, createAgent, assignTask } from '@/lib/api';
import { Agent } from '@/types';

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: '', role: '', model: 'gpt' });
  const [taskInputs, setTaskInputs] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    const data = await getAgents();
    setAgents(data);
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    await createAgent(newAgent);
    setNewAgent({ name: '', role: '', model: 'gpt' });
    setShowCreateForm(false);
    loadAgents();
  };

  const handleAssignTask = async (agentId: string) => {
    const task = taskInputs[agentId];
    if (task) {
      await assignTask({ agent_id: agentId, task });
      setTaskInputs({ ...taskInputs, [agentId]: '' });
      loadAgents();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'working': return 'text-green-600';
      case 'thinking': return 'text-yellow-600';
      case 'idle': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Agent Dashboard</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          Create Agent
        </button>
      </div>

      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full" onClick={() => setShowCreateForm(false)}>
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4">Create New Agent</h3>
            <form onSubmit={handleCreateAgent}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">Name</label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">Role</label>
                <input
                  type="text"
                  value={newAgent.role}
                  onChange={(e) => setNewAgent({ ...newAgent, role: e.target.value })}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">Model</label>
                <select
                  value={newAgent.model}
                  onChange={(e) => setNewAgent({ ...newAgent, model: e.target.value })}
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  <option value="gpt">GPT</option>
                  <option value="claude">Claude</option>
                </select>
              </div>
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="mr-2 bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                    {agent.name[0]}
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">{agent.name}</dt>
                    <dd className={`text-lg font-medium ${getStatusColor(agent.status)}`}>{agent.status}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-5 py-3">
              <div className="text-sm">
                <p className="text-gray-500">Role: {agent.role}</p>
                <p className="text-gray-500">Tasks in queue: {agent.task_queue.length}</p>
              </div>
              <div className="mt-3 flex">
                <input
                  type="text"
                  placeholder="Enter task..."
                  value={taskInputs[agent.id] || ''}
                  onChange={(e) => setTaskInputs({ ...taskInputs, [agent.id]: e.target.value })}
                  className="flex-1 rounded-l-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                <button
                  onClick={() => handleAssignTask(agent.id)}
                  className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 bg-gray-50 text-gray-500 text-sm font-medium rounded-r-md hover:bg-gray-100"
                >
                  Assign
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}