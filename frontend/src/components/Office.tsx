'use client';

import { useEffect, useRef, useState } from 'react';
import { getAgents } from '@/lib/api';
import { Agent } from '@/types';

interface OfficeAgent {
  id: string;
  name: string;
  role: string;
  status: string;
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  room: string;
  completedTasks?: number;
  taskDuration?: number;
}

interface Room {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
}

const CANVAS_WIDTH = 1400;
const CANVAS_HEIGHT = 700;
const AGENT_SIZE = 20;

const ROOMS: Room[] = [
  { id: 'main', name: 'Main Office', x: 50, y: 50, width: 500, height: 300, color: '#f3f4f6' },
  { id: 'meeting', name: 'Meeting Room', x: 600, y: 50, width: 350, height: 150, color: '#dbeafe' },
  { id: 'research', name: 'Research Lib', x: 1000, y: 50, width: 350, height: 150, color: '#fce7f3' },
  { id: 'lounge', name: 'Break Room', x: 50, y: 400, width: 350, height: 250, color: '#dcfce7' },
  { id: 'delivery', name: 'Telegram Hub', x: 450, y: 400, width: 350, height: 250, color: '#fef3c7' },
  { id: 'metrics', name: 'Performance', x: 850, y: 400, width: 500, height: 250, color: '#e0e7ff' },
];

export default function Office() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [agents, setAgents] = useState<OfficeAgent[]>([]);
  const [activeRoom, setActiveRoom] = useState('main');
  const [showMetrics, setShowMetrics] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState<OfficeAgent | null>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    const loadAgents = async () => {
      const data = await getAgents();
      const newAgents: OfficeAgent[] = data.map((agent: Agent) => ({
        id: agent.id,
        name: agent.name,
        role: agent.role,
        status: agent.status || 'idle',
        x: Math.random() * 400 + 100,
        y: Math.random() * 250 + 100,
        targetX: Math.random() * 400 + 100,
        targetY: Math.random() * 250 + 100,
        room: 'main',
        completedTasks: 0,
        taskDuration: 0,
      }));
      setAgents(newAgents);
    };
    loadAgents();
  }, []);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/office');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'task_assigned') {
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === data.agent_id
              ? { ...agent, status: 'working', room: 'main', targetX: 200, targetY: 150 }
              : agent
          )
        );
      } else if (data.event === 'agent_created') {
        const newAgent = data.agent;
        setAgents((prev) => [
          ...prev,
          {
            id: newAgent.id,
            name: newAgent.name,
            role: newAgent.role,
            status: 'idle',
            x: Math.random() * 400 + 100,
            y: Math.random() * 250 + 100,
            targetX: Math.random() * 400 + 100,
            targetY: Math.random() * 250 + 100,
            room: 'main',
            completedTasks: 0,
            taskDuration: 0,
          },
        ]);
      } else if (data.event === 'agent_deleted') {
        setAgents((prev) => prev.filter((a) => a.id !== data.agent_id));
      }
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      ROOMS.forEach((room) => {
        ctx.fillStyle = room.color;
        ctx.fillRect(room.x, room.y, room.width, room.height);
        ctx.strokeStyle = '#333333';
        ctx.lineWidth = 2;
        ctx.strokeRect(room.x, room.y, room.width, room.height);
        ctx.fillStyle = '#374151';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(room.name, room.x + 10, room.y + 25);
      });

      const mainRoom = ROOMS[0];
      [0, 1, 2, 3, 4].forEach((i) => {
        const x = mainRoom.x + 80 + i * 90;
        const y = mainRoom.y + 80;
        ctx.fillStyle = '#fcd34d';
        ctx.fillRect(x - 25, y - 15, 50, 30);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2;
        ctx.strokeRect(x - 25, y - 15, 50, 30);
      });

      setAgents((prevAgents) =>
        prevAgents.map((agent) => {
          let targetRoom = agent.room;
          if (agent.status === 'working') {
            targetRoom = 'main';
          } else if (agent.status === 'idle') {
            targetRoom = 'lounge';
          } else if (agent.status === 'thinking') {
            targetRoom = 'research';
          }
          agent.room = targetRoom;

          const dx = agent.targetX - agent.x;
          const dy = agent.targetY - agent.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          if (distance > 2) {
            const speed = 1.5;
            agent.x += (dx / distance) * speed;
            agent.y += (dy / distance) * speed;
          } else if (agent.status === 'idle') {
            if (distance < 10) {
              const lounge = ROOMS[3];
              agent.targetX = Math.random() * (lounge.width - 60) + lounge.x + 30;
              agent.targetY = Math.random() * (lounge.height - 60) + lounge.y + 30;
            }
          }

          return agent;
        })
      );

      agents.forEach((agent) => {
        const colorMap: { [key: string]: string } = {
          working: '#ef4444',
          thinking: '#f59e0b',
          idle: '#10b981',
          complete: '#6366f1',
        };

        const color = colorMap[agent.status] || '#6b7280';
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, AGENT_SIZE / 2, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(agent.status[0].toUpperCase(), agent.x, agent.y + 3);

        ctx.fillStyle = '#374151';
        ctx.font = '9px Arial';
        ctx.fillText(agent.name, agent.x, agent.y + 20);
      });

      if (showMetrics) {
        drawMetricsOverlay(ctx, agents);
      }

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [agents, showMetrics]);

  const drawMetricsOverlay = (ctx: CanvasRenderingContext2D, agentList: OfficeAgent[]) => {
    const metricsRoom = ROOMS[5];
    const padding = 10;
    const x = metricsRoom.x + padding;
    const y = metricsRoom.y + padding;

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText('Performance Metrics', x + 5, y + 20);

    ctx.font = '10px Arial';
    ctx.fillStyle = '#4b5563';

    let lineY = y + 40;
    const lineHeight = 20;

    agentList.slice(0, 5).forEach((agent) => {
      const statusColor = {
        working: '🔴',
        thinking: '🟡',
        idle: '🟢',
        complete: '🟣',
      }[agent.status] || '⚪';

      ctx.fillText(`${statusColor} ${agent.name}`, x + 5, lineY);
      ctx.fillText(`${agent.role}`, x + 150, lineY);
      ctx.fillText(`Tasks: ${agent.completedTasks || 0}`, x + 270, lineY);

      lineY += lineHeight;
    });
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Pixel Office - Multi-Room</h2>
          <button
            onClick={() => setShowMetrics(!showMetrics)}
            className="px-3 py-1 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700"
          >
            {showMetrics ? '📊 Hide' : '📊 Show'} Metrics
          </button>
        </div>

        <div className="grid grid-cols-3 md:grid-cols-6 gap-2 mb-4">
          {ROOMS.map((room) => (
            <button
              key={room.id}
              onClick={() => setActiveRoom(room.id)}
              className={`px-2 py-1 text-xs rounded font-medium transition ${
                activeRoom === room.id
                  ? 'bg-indigo-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {room.name}
            </button>
          ))}
        </div>

        <div className="flex gap-4 mb-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Idle</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-amber-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Thinking</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Working</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-indigo-500 rounded-full"></div>
            <span className="text-sm text-gray-600">Complete</span>
          </div>
        </div>
      </div>

      <div className="border border-gray-300 rounded-lg overflow-hidden bg-white mb-6">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="w-full"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">👥 Active Agents ({agents.length})</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => setSelectedAgent(agent)}
                className={`w-full text-left p-2 rounded text-sm transition ${
                  selectedAgent?.id === agent.id
                    ? 'bg-indigo-100 border border-indigo-500'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center gap-2">
                  <div
                    className={`w-2 h-2 rounded-full ${
                      agent.status === 'working'
                        ? 'bg-red-500'
                        : agent.status === 'thinking'
                          ? 'bg-amber-500'
                          : agent.status === 'idle'
                            ? 'bg-green-500'
                            : 'bg-indigo-500'
                    }`}
                  ></div>
                  <span className="font-medium">{agent.name}</span>
                </div>
                <div className="text-xs text-gray-500 ml-4">{agent.role}</div>
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white p-4 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-900 mb-3">🏢 Office Rooms</h3>
          <div className="space-y-2">
            {ROOMS.map((room) => {
              const roomAgents = agents.filter((a) => a.room === room.id);
              return (
                <div
                  key={room.id}
                  className="p-2 bg-gray-50 rounded text-sm cursor-pointer hover:bg-gray-100"
                  onClick={() => setActiveRoom(room.id)}
                >
                  <div className="flex justify-between items-center">
                    <div className="font-medium text-gray-900">{room.name}</div>
                    <div className="bg-indigo-600 text-white text-xs rounded-full px-2 py-0.5">
                      {roomAgents.length}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {selectedAgent && (
          <div className="bg-white p-4 border border-indigo-300 rounded-lg bg-indigo-50">
            <h3 className="font-semibold text-gray-900 mb-3">📋 Agent Details</h3>
            <div className="space-y-2 text-sm">
              <div>
                <div className="text-gray-600 text-xs">Name</div>
                <div className="font-medium text-lg">{selectedAgent.name}</div>
              </div>
              <div>
                <div className="text-gray-600 text-xs">Role</div>
                <div className="font-medium">{selectedAgent.role}</div>
              </div>
              <div className="flex gap-4">
                <div>
                  <div className="text-gray-600 text-xs">Status</div>
                  <div className="font-medium capitalize text-indigo-600">{selectedAgent.status}</div>
                </div>
                <div>
                  <div className="text-gray-600 text-xs">Room</div>
                  <div className="font-medium">
                    {ROOMS.find((r) => r.id === selectedAgent.room)?.name}
                  </div>
                </div>
              </div>
              <div>
                <div className="text-gray-600 text-xs">Position</div>
                <div className="font-mono text-xs bg-white p-1 rounded">
                  ({selectedAgent.x.toFixed(0)}, {selectedAgent.y.toFixed(0)})
                </div>
              </div>
              <div className="pt-2 border-t">
                <div className="text-gray-600 text-xs">Tasks Completed</div>
                <div className="text-2xl font-bold text-indigo-600">{selectedAgent.completedTasks || 0}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
