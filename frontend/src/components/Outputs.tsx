'use client';

import { useState, useEffect } from 'react';
import { getOutputs, getOutputContent } from '@/lib/api';

interface OutputData {
  [agent: string]: string[];
}

export default function Outputs() {
  const [outputs, setOutputs] = useState<OutputData>({});
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>('');

  useEffect(() => {
    loadOutputs();
  }, []);

  const loadOutputs = async () => {
    const data = await getOutputs();
    setOutputs(data);
  };

  const handleFileClick = async (agent: string, filename: string) => {
    setSelectedAgent(agent);
    setSelectedFile(filename);
    const data = await getOutputContent(agent, filename);
    setFileContent(data.content);
  };

  const handleSendToTelegram = () => {
    // Placeholder for Telegram integration
    alert('Telegram integration not yet implemented');
  };

  const handleShowAsMD = () => {
    // Already showing as MD
    alert('Already displaying as Markdown');
  };

  return (
    <div className="px-4 py-6 sm:px-0">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Outputs</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="md:col-span-1">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Agents</h3>
          <ul className="space-y-2">
            {Object.keys(outputs).map((agent) => (
              <li key={agent}>
                <button
                  onClick={() => setSelectedAgent(agent)}
                  className={`w-full text-left px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    selectedAgent === agent
                      ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {agent} ({outputs[agent].length} files)
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div className="md:col-span-1">
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Files</h3>
          {selectedAgent && (
            <ul className="space-y-2">
              {outputs[selectedAgent].map((file) => (
                <li key={file}>
                  <button
                    onClick={() => handleFileClick(selectedAgent, file)}
                    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                      selectedFile === file
                        ? 'bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-200'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    {file}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="md:col-span-2">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Content</h3>
            {selectedFile && (
              <div className="space-x-2">
                <button
                  onClick={handleShowAsMD}
                  className="bg-blue-600 dark:bg-blue-700 text-white px-3 py-1 rounded text-sm hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors"
                >
                  Show as MD
                </button>
                <button
                  onClick={handleSendToTelegram}
                  className="bg-green-600 dark:bg-green-700 text-white px-3 py-1 rounded text-sm hover:bg-green-700 dark:hover:bg-green-600 transition-colors"
                >
                  Send to Telegram
                </button>
              </div>
            )}
          </div>
          {fileContent ? (
            <div className="bg-white dark:bg-gray-800 p-4 rounded-md shadow dark:shadow-lg dark:border dark:border-gray-700">
              <pre className="whitespace-pre-wrap text-sm text-gray-900 dark:text-gray-100">{fileContent}</pre>
            </div>
          ) : (
            <p className="text-gray-500 dark:text-gray-400">Select a file to view its content</p>
          )}
        </div>
      </div>
    </div>
  );
}