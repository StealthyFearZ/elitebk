import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import useFileUpload from '../hooks/useFileUpload';
import { useAuth } from '../context/AuthContext';


export default function ChatWindow() {
    const { askQuestion, loading } = useChat();
    const { selectedFile, handleFileChange, handleFileUpload, uploadLoading, uploadError, uploadSuccess } = useFileUpload();
    const { isDeveloper, username, logout } = useAuth();
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
    const [sources, setSources] = useState<{ snippet: string, metadata: any }[]>([]);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const navigate = useNavigate();

    // Auto Scrolls a UI element into view if data changes
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const handleSend = async () => {
        if (!query.trim()) return;

        const currentQuery = query;
        setQuery("");
        setSources([]);
        setMessages(prev => [...prev, { role: 'user', content: currentQuery }]);

        const result = await askQuestion(currentQuery);
        if (result) {
            setMessages(prev => [...prev, { role: 'assistant', content: result.answer }]);
            setSources(result.sources);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex flex-col flex-1 w-full max-w-3xl mx-auto bg-white border-x border-gray-200 overflow-hidden">
            <div className="bg-gray-800 px-5 py-3 text-white flex items-center justify-between border-b border-gray-700">
                <div className="flex items-center gap-2">
                    {/* Add BB lgogo */}
                    <span className="text-xl">🏀</span>
                    <span className="font-semibold text-lg">EliteBK</span>
                </div>
                <div className="flex items-center gap-3 text-sm">
                    <span className="text-gray-400 text-xs">{username}</span>
                    <button
                        onClick={handleLogout}
                        className="bg-gray-700 hover:bg-gray-600 text-gray-200 px-3 py-1 rounded text-xs transition-colors"
                    >
                        Log out
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
                {messages.length === 0 && (
                    <div className="flex flex-col items-center justify-center h-full text-center px-6 py-16 gap-4">
                        <div className="text-5xl">🏀</div>
                        <p className="text-gray-600 font-medium text-lg">Ask EliteBK anything</p>
                        {/* Have a default question for user to try */}
                        {/* We lowk need to update our dataset to have more data */}
                        <p className="text-gray-400 text-sm max-w-xs">
                            Try: "How many points did Lebron score against the Warriors in 2024 ?"
                        </p>
                        {/* Send the query of the question if they click it */}
                        <button
                            onClick={() => setQuery("How many points did Lebron score against the Warriors in 2024 ?")}
                            className="mt-1 bg-white hover:bg-gray-100 text-gray-600 border border-gray-300 text-xs px-4 py-2 rounded-full transition-colors shadow-sm"
                        >
                            Try an example question
                        </button>
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[72%] rounded-2xl px-4 py-3 shadow-sm text-sm leading-relaxed ${msg.role === 'user' ? 'bg-slate-700 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'}`}>
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                        </div>
                    </div>
                ))}
                {/* Display the sources */}
                {sources.length > 0 && !loading && (
                    <div className="flex justify-start w-full max-w-[85%]">
                        <div className="w-full rounded-xl bg-white border border-gray-200 shadow-sm px-4 py-3 space-y-2">
                            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                                Sources ({sources.length})
                            </p>
                            {/* Display each source used here */}
                            {sources.map((source, idx) => (
                                <div key={idx} className="text-xs text-gray-600 border-l-2 border-gray-200 pl-2">
                                    <p className="leading-relaxed">{source.snippet}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                {loading && (
                    <div className="flex justify-start">
                        <div className="max-w-[70%] rounded-2xl p-3 shadow-sm bg-white text-gray-800 rounded-bl-none border border-gray-200 flex space-x-2 items-center">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="p-4 bg-white border-t border-gray-200">
                {isDeveloper && (
                    <div className="flex flex-col gap-2 mb-4">
                        <div className="flex items-center gap-2">
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".json"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors border border-gray-300"
                            >
                                {selectedFile ? selectedFile.name : 'Choose JSON file'}
                            </button>
                            <button
                                onClick={handleFileUpload}
                                disabled={!selectedFile || uploadLoading}
                                className="bg-gray-700 hover:bg-gray-600 text-white px-4 py-2 rounded-lg text-xs font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                                {uploadLoading ? 'Uploading...' : 'Upload Dataset'}
                            </button>
                        </div>
                        {uploadError && <p className="text-red-500 text-sm">{uploadError}</p>}
                        {uploadSuccess && <p className="text-green-500 text-sm">Dataset uploaded and updated successfully!</p>}
                    </div>
                )}

                <div className="flex gap-2">
                    <input
                        className="flex-1 border border-gray-200 bg-gray-50 px-4 py-2.5 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-gray-400 focus:border-transparent transition-all placeholder:text-gray-400"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Ask about a player or stat..."
                        disabled={loading}
                    />
                    <button
                        className="bg-gray-800 hover:bg-gray-700 text-white px-5 py-2.5 rounded-full text-sm font-medium transition-colors shadow-sm disabled:opacity-40 disabled:cursor-not-allowed"
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
