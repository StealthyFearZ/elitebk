import { useState } from 'react';

export const useDatasetUpdate = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const API_URL = import.meta.env.VITE_API_URL;

  const updateDataset = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const res = await fetch(`${API_URL}/api/update-dataset/`, {
        method: 'GET',
      });

      if (!res.ok) {
        throw new Error('Network response was not ok');
      }

      setSuccess(true);
    } catch (error) {
      console.error('Dataset update failure:', error);
      setError('Failed to update the dataset. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return { updateDataset, loading, error, success };
};