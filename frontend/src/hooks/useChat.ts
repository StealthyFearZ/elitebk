import { useState } from 'react';

export const useChat = () => {
    const [loading, setLoading] = useState(false);
    const API_URL = import.meta.env.VITE_API_URL;

    const askQuestion = async (question: string) => {
        setLoading(true);
        try {
            const res = await fetch(`${API_URL}/api/ask/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
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
}