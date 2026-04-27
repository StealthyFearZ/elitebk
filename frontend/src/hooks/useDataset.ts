import { useState } from 'react';

export const useDatasetUpdate = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [progress, setProgress] = useState<string[]>([]);
  const [currentMessage, setCurrentMessage] = useState<string>("");
  const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

  const updateDataset = async (options?: { source?: string; season?: string; maxPlayers?: number }) => {
    setLoading(true);
    setError(null);
    setSuccess(false);
    setProgress([]);
    setCurrentMessage("");

    try {
      const query = new URLSearchParams();
      if (options?.source) {
        query.append('source', options.source);
      }
      if (options?.season) {
        query.append('season', options.season);
      }
      if (options?.maxPlayers) {
        query.append('max_players', options.maxPlayers.toString());
      }

      const url = `${API_URL}/api/update-dataset/?${query.toString()}`;

      // Use EventSource for Server-Sent Events
      const eventSource = new EventSource(url);

      return new Promise<void>((resolve, reject) => {
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            console.log("SSE Event received:", data);

            if (data.status === 'processing') {
              console.log("Setting current message to:", data.message);
              setCurrentMessage(data.message);
              if (data.progress) {
                setProgress(data.progress);
              }
            } else if (data.status === 'completed') {
              console.log("Completed - setting success to true");
              setProgress(data.progress || []);
              setSuccess(true);
              setCurrentMessage("");
              eventSource.close();
              resolve();
            } else if (data.status === 'error') {
              console.log("Error received:", data.error);
              setError(data.error);
              setCurrentMessage("");
              eventSource.close();
              reject(new Error(data.error));
            }
          } catch (e) {
            console.error('Failed to parse SSE data:', e);
          }
        };

        eventSource.onerror = (error) => {
          console.error('EventSource error:', error);
          setError('Failed to update the dataset. Please try again.');
          eventSource.close();
          reject(error);
        };
      });

    } catch (error) {
      console.error('Dataset update failure:', error);
      setError('Failed to update the dataset. Please try again.');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { updateDataset, loading, error, success, progress, currentMessage };
};