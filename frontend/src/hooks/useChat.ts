import { useState } from 'react';
import { useAuth } from '../context/AuthContext';

export const useChat = () => {
    const [loading, setLoading] = useState(false);
    const { token } = useAuth();
    const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

    const askQuestion = async (question: string) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/ask/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Token ${token}`,
                },
                body: JSON.stringify({ question })
            });

            if (!res.ok) {
                throw new Error("Network response was not ok");
            }

            const data = await res.json();
            return data;
        } catch (error) {
            console.error("Chat failure: ", error);
        } finally {
            setLoading(false);
        }
    };

    return { askQuestion, loading };
};
