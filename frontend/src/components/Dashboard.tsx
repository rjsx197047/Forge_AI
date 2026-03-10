'use client';

import { useState, useEffect } from 'react';
import { getAgents, createAgent, assignTask } from '@/lib/api';
import { Agent } from '@/types';

export default function Dashboard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [ollamas, setOllamas] = useState<string[]>(['llama2', 'mistral', 'neural-chat']);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: '', role: '', model: 'llama2' });
  const [taskInputs, setTaskInputs] = useState<{ [key: string]: string }>({});

  useEffect(() => {
    loadAgents();
    fetchOllamaModels();
  }, []);

  const loadAgents = async () => {
    const data = await getAgents();
    setAgents(data);
  };

  const fetchOllamaModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/ollama/models');
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      if (data.models && data.models.length > 0) {
        setOllamas(data.models);
      } else {
        console.warn('No Ollama models available. Make sure Ollama is running.');
      }
    } catch (error) {
      console.warn('Could not fetch Ollama models. Using defaults.', error);
      setOllamas(['llama2', 'mistral', 'neural-chat']);
    }
  };

  const handleCreateAgent = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (!newAgent.name || !newAgent.role) {
        alert('Please fill in all fields');
        return;
      }
      await createAgent(newAgent);
      setNewAgent({ name: '', role: '', model: 'llama2' });
      setShowCreateForm(false);
      await loadAgents();
    } catch (error) {
      console.error('Failed to create agent:', error);
      alert('Failed to create agent. Make sure backend is running on port 8000.');
    }
  };

  const handleAssignTask = async (agentId: string) => {
    const task = taskInputs[agentId];
    if (task) {
      try {
        await assignTask({ agent_id: agentId, task });
        setTaskInputs({ ...taskInputs, [agentId]: '' });
        await loadAgents();
      } catch (error) {
        console.error('Failed to assign task:', error);
        alert('Failed to assign task');
      }
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
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Agent Dashboard</h2>
        <button
          onClick={() => setShowCreateForm(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors"
        >
          Create Agent
        </button>
      </div>

      {/* Ollama Info Banner */}
      <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg">
        <p className="text-sm text-blue-800 dark:text-blue-200">
          Powered by Ollama AI - Your local, open-source AI models. Available models: {ollamas.join(', ')}
        </p>
      </div>

      {showCreateForm && (
        <div className="fixed inset-0 bg-gray-600 dark:bg-gray-900 bg-opacity-50 dark:bg-opacity-70 overflow-y-auto h-full w-full" onClick={() => setShowCreateForm(false)}>
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800 dark:border-gray-700" onClick={e => e.stopPropagation()}>
            <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Create New Agent with Ollama AI</h3>
            <form onSubmit={handleCreateAgent}>
              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">Name</label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  className="shadow appearance-none border border-gray-300 dark:border-gray-600 rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">Role</label>
                <input
                  type="text"
                  value={newAgent.role}
                  onChange={(e) => setNewAgent({ ...newAgent, role: e.target.value })}
                  className="shadow appearance-none border border-gray-300 dark:border-gray-600 rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  required
                />
              </div>
              <div className="mb-4">
                <label className="block text-gray-700 dark:text-gray-300 text-sm font-bold mb-2">Ollama Model</label>
                <select
                  value={newAgent.model}
                  onChange={(e) => setNewAgent({ ...newAgent, model: e.target.value })}
                  className="shadow appearance-none border border-gray-300 dark:border-gray-600 rounded w-full py-2 px-3 text-gray-700 dark:text-white dark:bg-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                >
                  {ollamas.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="mr-2 bg-gray-300 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-md hover:bg-gray-400 dark:hover:bg-gray-600 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600 transition-colors"
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
          <div key={agent.id} className="bg-white dark:bg-gray-800 overflow-hidden shadow dark:shadow-lg rounded-lg dark:border dark:border-gray-700">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-gray-300 dark:bg-indigo-600 rounded-full flex items-center justify-center text-white dark:text-gray-100 font-bold">
                    {agent.name[0]}
                  </div>
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">{agent.name}</dt>
                    <dd className={`text-lg font-medium ${getStatusColor(agent.status)}`}>{agent.status}</dd>
                  </dl>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 px-5 py-3">
              <div className="text-sm">
                <p className="text-gray-500 dark:text-gray-400">Role: {agent.role}</p>
                <p className="text-gray-500 dark:text-gray-400">Tasks in queue: {agent.task_queue.length}</p>
              </div>
              <div className="mt-3 flex">
                <input
                  type="text"
                  placeholder="Enter task..."
                  value={taskInputs[agent.id] || ''}
                  onChange={(e) => setTaskInputs({ ...taskInputs, [agent.id]: e.target.value })}
                  className="flex-1 rounded-l-md border border-gray-300 dark:border-gray-600 dark:bg-gray-600 dark:text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                />
                <button
                  onClick={() => handleAssignTask(agent.id)}
                  className="inline-flex items-center px-3 py-2 border border-l-0 border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-sm font-medium rounded-r-md hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
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