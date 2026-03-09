'use client';

import { useEffect, useRef, useState } from 'react';
import { getAgents } from '@/lib/api';

interface OfficeAgent {
  id: string;
  name: string;
  role: string;
  status: string;
  x: number;
  y: number;
  targetX: number;
  targetY: number;
}

interface DeskPosition {
  id: number;
  x: number;
  y: number;
  occupied: boolean;
}

const CANVAS_WIDTH = 1200;
const CANVAS_HEIGHT = 600;
const DESK_COUNT = 5;
const AGENT_SIZE = 20;

export default function Office() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [agents, setAgents] = useState<OfficeAgent[]>([]);
  const [desks] = useState<DeskPosition[]>(
    Array.from({ length: DESK_COUNT }, (_, i) => ({
      id: i,
      x: 150 + i * 200,
      y: 300,
      occupied: false,
    }))
  );
  const animationFrameRef = useRef<number>();

  // Load agents from API
  useEffect(() => {
    const loadAgents = async () => {
      const data = await getAgents();
      const newAgents = data.map((agent: any, index: number) => {
        // Random starting position
        const startX = Math.random() * (CANVAS_WIDTH - 100) + 50;
        const startY = Math.random() * (CANVAS_HEIGHT - 100) + 50;
        return {
          id: agent.id,
          name: agent.name,
          role: agent.role,
          status: agent.status || 'idle',
          x: startX,
          y: startY,
          targetX: startX,
          targetY: startY,
        };
      });
      setAgents(newAgents);
    };
    loadAgents();
  }, []);

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/office');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'task_assigned') {
        // Update agent status to working
        setAgents((prev) =>
          prev.map((agent) =>
            agent.id === data.agent_id
              ? { ...agent, status: 'working', targetX: desks[0]?.x || 300, targetY: desks[0]?.y || 300 }
              : agent
          )
        );
      } else if (data.event === 'agent_created') {
        // Add new agent
        const newAgent = data.agent;
        setAgents((prev) => [
          ...prev,
          {
            id: newAgent.id,
            name: newAgent.name,
            role: newAgent.role,
            status: newAgent.status || 'idle',
            x: Math.random() * (CANVAS_WIDTH - 100) + 50,
            y: Math.random() * (CANVAS_HEIGHT - 100) + 50,
            targetX: Math.random() * (CANVAS_WIDTH - 100) + 50,
            targetY: Math.random() * (CANVAS_HEIGHT - 100) + 50,
          },
        ]);
      } else if (data.event === 'agent_deleted') {
        setAgents((prev) => prev.filter((a) => a.id !== data.agent_id));
      }
    };
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    return () => ws.close();
  }, [desks]);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const animate = () => {
      // Clear canvas
      ctx.fillStyle = '#f3f4f6';
      ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

      // Draw grid background
      ctx.strokeStyle = '#e5e7eb';
      ctx.lineWidth = 1;
      for (let i = 0; i < CANVAS_WIDTH; i += 50) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, CANVAS_HEIGHT);
        ctx.stroke();
      }
      for (let i = 0; i < CANVAS_HEIGHT; i += 50) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(CANVAS_WIDTH, i);
        ctx.stroke();
      }

      // Draw desks
      desks.forEach((desk) => {
        ctx.fillStyle = '#fcd34d';
        ctx.fillRect(desk.x - 30, desk.y - 20, 60, 40);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 2;
        ctx.strokeRect(desk.x - 30, desk.y - 20, 60, 40);
        ctx.fillStyle = '#374151';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`Desk ${desk.id + 1}`, desk.x, desk.y + 25);
      });

      // Draw lounge area
      ctx.fillStyle = '#dbeafe';
      ctx.fillRect(50, 50, 150, 100);
      ctx.strokeStyle = '#0284c7';
      ctx.lineWidth = 2;
      ctx.strokeRect(50, 50, 150, 100);
      ctx.fillStyle = '#374151';
      ctx.font = 'bold 12px Arial';
      ctx.textAlign = 'center';
      ctx.fillText('Lounge', 125, 100);

      // Update and draw agents
      setAgents((prevAgents) =>
        prevAgents.map((agent) => {
          // Move towards target
          const dx = agent.targetX - agent.x;
          const dy = agent.targetY - agent.y;
          const distance = Math.sqrt(dx * dx + dy * dy);

          let newX = agent.x;
          let newY = agent.y;

          if (distance > 2) {
            const speed = 1.5;
            newX += (dx / distance) * speed;
            newY += (dy / distance) * speed;
          } else if (agent.status === 'working') {
            // Complete the task
            newX = agent.targetX;
            newY = agent.targetY;
          } else if (agent.status === 'idle') {
            // Wander around lounge
            if (distance < 10) {
              agent.targetX = Math.random() * 150 + 50;
              agent.targetY = Math.random() * 100 + 50;
            }
          }

          return { ...agent, x: newX, y: newY };
        })
      );

      // Draw agents
      agents.forEach((agent) => {
        const color =
          agent.status === 'working'
            ? '#ef4444'
            : agent.status === 'thinking'
              ? '#f59e0b'
              : agent.status === 'idle'
                ? '#10b981'
                : '#6366f1';

        // Draw agent circle
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(agent.x, agent.y, AGENT_SIZE / 2, 0, Math.PI * 2);
        ctx.fill();

        // Draw border
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw status indicator
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 10px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(agent.status[0].toUpperCase(), agent.x, agent.y + 3);

        // Draw name below
        ctx.fillStyle = '#374151';
        ctx.font = '9px Arial';
        ctx.fillText(agent.name, agent.x, agent.y + 20);
      });

      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [agents, desks]);

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Pixel Office</h2>
        <div className="flex gap-4 mb-4">
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

      <div className="border border-gray-300 rounded-lg overflow-hidden bg-white">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="w-full border-b border-gray-300"
        />
      </div>

      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Agents</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {agents.map((agent) => (
            <div key={agent.id} className="p-4 bg-white border border-gray-200 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    agent.status === 'working'
                      ? 'bg-red-500'
                      : agent.status === 'thinking'
                        ? 'bg-amber-500'
                        : agent.status === 'idle'
                          ? 'bg-green-500'
                          : 'bg-indigo-500'
                  }`}
                ></div>
                <h4 className="font-semibold text-gray-900">{agent.name}</h4>
              </div>
              <p className="text-sm text-gray-600">{agent.role}</p>
              <p className="text-xs text-gray-500 mt-2 capitalize">{agent.status}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}