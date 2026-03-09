export interface Agent {
  id: string;
  name: string;
  role: string;
  model: string;
  status: string;
  task_queue: string[];
  memory: string;
}

export interface Output {
  agent: string;
  files: string[];
}