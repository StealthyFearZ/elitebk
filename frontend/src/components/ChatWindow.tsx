// frontend/src/components/ChatWindow.tsx
import { useState } from 'react';
import { useChat } from '../hooks/useChat';

export default function ChatWindow() {
    const { askQuestion, loading } = useChat();
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState("");

    const handleSend = async () => {
        if (!query.trim()) return;

        const result = await askQuestion(query); // also gets the sources (user story 4)
        if (result) {
            setAnswer(result.answer);
        }
    };

    // following CSS def needs adjustment to display chat history so this is just temp for me
    return (
        <div className="flex flex-col gap-4 p-6 max-w-2xl mx-auto">
            {/* Input area */}
            <div className="flex gap-2">
                <input 
                    className="border p-2 flex-grow rounded"
                    value={query} 
                    onChange={(e) => setQuery(e.target.value)} 
                    placeholder="Ask a question"
                />
                <button 
                    className="bg-blue-500 text-white px-4 py-2 rounded"
                    onClick={handleSend}
                    disabled={loading}
                >
                    {loading ? 'Sending...' : 'Send'}
                </button>
            </div>
            
            {/* Answer box */}
            {answer && (
                <div className="bg-gray-100 p-4 rounded mt-4">
                    <h3 className="font-bold">Answer:</h3>
                    <p className="whitespace-pre-wrap">{answer}</p>
                </div>
            )}
        </div>
    );
}