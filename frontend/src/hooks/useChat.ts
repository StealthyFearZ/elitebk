import { useState } from 'react';

export const useChat = () => {
    const [loading, setLoading] = useState(false);

    const askQuestion = async (question: string) => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/ask/', {
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