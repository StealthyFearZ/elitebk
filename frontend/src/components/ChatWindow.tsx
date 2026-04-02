import { useState } from 'react';
import { useChat } from '../hooks/useChat';

export default function ChatWindow() {
    const { askQuestion, loading } = useChat();
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const currentQuery = query;
        setQuery("");
        setMessages(prev => [...prev, { role: 'user', content: currentQuery }]);

        const result = await askQuestion(currentQuery);
        if (result) {
            setMessages(prev => [...prev, { role: 'assistant', content: result.answer }]);
        }
    };

    return (
        <div className="flex flex-col h-[80vh] w-full max-w-3xl mx-auto bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-blue-600 p-4 text-white text-center font-semibold text-lg">
                EliteChat
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.length === 0 && (
                    <div className="text-center text-gray-400 mt-10">
                        Start a conversation...
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[70%] rounded-2xl p-3 shadow-sm ${msg.role === 'user' ? 'bg-blue-500 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'}`}>
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="flex justify-start">
                        <div className="max-w-[70%] rounded-2xl p-3 shadow-sm bg-white text-gray-800 rounded-bl-none border border-gray-200 flex space-x-2 items-center">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                )}
            </div>
            
            <div className="p-4 bg-white border-t border-gray-200">
                <div className="flex gap-2">
                    <input 
                        className="flex-1 border border-gray-300 p-3 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        value={query} 
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Type your message..."
                        disabled={loading}
                    />
                    <button 
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-full font-medium transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                        onClick={handleSend}
                        disabled={loading || !query.trim()}
                    >
                        Send
                    </button>
                </div>
            </div>
        </div>
    );
}
