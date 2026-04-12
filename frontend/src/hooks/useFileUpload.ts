import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

const useFileUpload = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const { token } = useAuth();
  const API_URL = import.meta.env.VITE_API_URL;

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(event.target.files?.[0] ?? null);
    setUploadError(null);
    setUploadSuccess(false);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) return;

    setUploadLoading(true);
    setUploadError(null);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await fetch(`${API_URL}/api/upload-context/`, {
        method: 'POST',
        headers: { Authorization: `Token ${token}` },
        body: formData,
      });

      const data = await res.json();

      if (!res.ok) {
        setUploadError(data.error || 'Upload failed');
        return;
      }

      setUploadSuccess(true);
      setSelectedFile(null);
    } catch {
      setUploadError('Unable to reach the server. Please try again.');
    } finally {
      setUploadLoading(false);
    }
  };

  return { selectedFile, handleFileChange, handleFileUpload, uploadLoading, uploadError, uploadSuccess };
};

export default useFileUpload;
