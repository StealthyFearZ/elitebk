import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useChat } from '../hooks/useChat';
import useFileUpload from '../hooks/useFileUpload';
import { useAuth } from '../context/AuthContext';
import ReportPanel from './ReportPanel';
import type { ReportState } from '../types/report';


export default function ChatWindow() {
    const { askQuestion, loading } = useChat();
    const { selectedFile, handleFileChange, handleFileUpload, uploadLoading, uploadError, uploadSuccess } = useFileUpload();
    const { isDeveloper, username, logout, token } = useAuth();
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState<{ role: 'user' | 'assistant', content: string }[]>([]);
    const [sources, setSources] = useState<{ snippet: string, metadata: any }[]>([]);
    const [detectedTeam, setDetectedTeam] = useState<string | null>(null);
    const [detectedOpponent, setDetectedOpponent] = useState<string | null>(null);
    const [reportStates, setReportStates] = useState<Record<number, ReportState>>({});
    const [predictionStates, setPredictionStates] = useState<Record<number, {
        loading: boolean;
        error: string | null;
        rows: Array<Record<string, any>> | null;
        xlsxBase64: string | null;
        notes: string | null;
    }>>({});
    const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
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
        setDetectedTeam(null);
        setDetectedOpponent(null);
        setMessages(prev => [...prev, { role: 'user', content: currentQuery }]);

        const result = await askQuestion(currentQuery);
        if (result) {
            setMessages(prev => [...prev, { role: 'assistant', content: result.answer }]);
            setSources(result.sources);
            setDetectedTeam(result.detected_team ?? null);
            setDetectedOpponent(result.detected_opponent ?? null);
        }
    };

    const handleGenerateReport = async (msgIndex: number) => {
      // pull the question / answer
        const question = messages[msgIndex - 1]?.content;
        const answer = messages[msgIndex]?.content;
        if (!question || !answer) return;

        // call setReportStates before fetching
        setReportStates(prev => ({ ...prev, [msgIndex]: { loading: true, error: null, preview: null, pdfBlob: null } }));

        try {
            // use the generate-report view func
            const res = await fetch(`${API_URL}/api/generate-report/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', Authorization: `Token ${token}` },
                body: JSON.stringify({ question, answer, sources }),
            });
            // error catching
            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error((err as any).error ?? `Server Error ${res.status}`);
            }
            const data = await res.json();
            const binaryStr = atob(data.pdf_base64); //pdf in the making,,,
            const bytes = new Uint8Array(binaryStr.length);
            for (let i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);
            const pdfBlob = new Blob([bytes], { type: 'application/pdf' });
            setReportStates(prev => ({ ...prev, [msgIndex]: { loading: false, error: null, preview: data.preview, pdfBlob } }));
        } catch (err) {
            setReportStates(prev => ({ ...prev, [msgIndex]: { loading: false, error: err instanceof Error ? err.message : 'Report generation failed', preview: null, pdfBlob: null } }));
        }
    };

    // add func to download the report
    const handleDownloadReport = (msgIndex: number) => {
        const blob = reportStates[msgIndex]?.pdfBlob;
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `elitebk-report-${msgIndex}.pdf`;
        a.click();
        URL.revokeObjectURL(url); // use URL 
    };

    const handleGeneratePredictions = async (msgIndex: number) => {
        const question = messages[msgIndex - 1]?.content ?? '';
        if (!detectedTeam) return;

        setPredictionStates(prev => ({
            ...prev,
            [msgIndex]: { loading: true, error: null, rows: null, xlsxBase64: null, notes: null },
        }));

        try {
            const res = await fetch(`${API_URL}/api/predict-lineup/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', Authorization: `Token ${token}` },
                body: JSON.stringify({ team: detectedTeam, opponent: detectedOpponent, question }),
            });

            if (!res.ok) {
                const err = await res.json().catch(() => ({}));
                throw new Error((err as any).error ?? `Server Error ${res.status}`);
            }

            const data = await res.json();
            setPredictionStates(prev => ({
                ...prev,
                [msgIndex]: {
                    loading: false,
                    error: null,
                    rows: data.table ?? [],
                    xlsxBase64: data.xlsx_base64 ?? null,
                    notes: data.notes ?? null,
                },
            }));
        } catch (err) {
            setPredictionStates(prev => ({
                ...prev,
                [msgIndex]: {
                    loading: false,
                    error: err instanceof Error ? err.message : 'Prediction generation failed',
                    rows: null,
                    xlsxBase64: null,
                    notes: null,
                },
            }));
        }
    };

    const downloadBase64Xlsx = (base64: string, filename: string) => {
        const binaryStr = atob(base64);
        const bytes = new Uint8Array(binaryStr.length);
        for (let i = 0; i < binaryStr.length; i++) bytes[i] = binaryStr.charCodeAt(i);

        const blob = new Blob([bytes], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`;
        a.click();
        URL.revokeObjectURL(url);
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
                {/* Add Generate Report Option Here */ }
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[72%] rounded-2xl px-4 py-3 shadow-sm text-sm leading-relaxed ${msg.role === 'user' ? 'bg-slate-700 text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none border border-gray-200'}`}>
                            <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                        </div>
                        {/* Button to generate the Report */ }
                        {msg.role === 'assistant' && !reportStates[idx]?.preview && !reportStates[idx]?.loading && (
                            <button onClick={() => handleGenerateReport(idx)} className="mt-1 ml-1 text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2 transition-colors">
                                Generate Report
                            </button>
                        )}
                        {/* Button to generate lineup predictions (Excel) */}
                        {msg.role === 'assistant' && detectedTeam && !predictionStates[idx]?.rows && !predictionStates[idx]?.loading && (
                            <button
                                onClick={() => handleGeneratePredictions(idx)}
                                className="mt-1 ml-1 text-xs text-gray-400 hover:text-gray-600 underline underline-offset-2 transition-colors"
                            >
                                Generate Predicted Stat Lines (Excel) — {detectedTeam}{detectedOpponent ? ` vs ${detectedOpponent}` : ''}
                            </button>
                        )}
                        {predictionStates[idx] && (predictionStates[idx].loading || predictionStates[idx].error || predictionStates[idx].rows) && (
                            <div className="w-full max-w-[85%] mt-2 rounded-xl bg-white border border-gray-200 shadow-sm px-4 py-3 space-y-3">
                                {predictionStates[idx].loading && (
                                    <p className="text-xs text-gray-500">Generating predictions...</p>
                                )}
                                {predictionStates[idx].error && (
                                    <p className="text-xs text-red-500">{predictionStates[idx].error}</p>
                                )}
                                {predictionStates[idx].notes && (
                                    <p className="text-xs text-gray-500">{predictionStates[idx].notes}</p>
                                )}
                                {predictionStates[idx].rows && predictionStates[idx].rows.length > 0 && (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-xs">
                                            <thead>
                                                <tr className="text-gray-500 border-b">
                                                    {Object.keys(predictionStates[idx].rows[0]).map((k) => (
                                                        <th key={k} className="text-left py-2 pr-3 font-semibold whitespace-nowrap">
                                                            {k}
                                                        </th>
                                                    ))}
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {predictionStates[idx].rows.map((row, rIdx) => (
                                                    <tr key={rIdx} className="border-b last:border-b-0">
                                                        {Object.keys(predictionStates[idx].rows![0]).map((k) => (
                                                            <td key={k} className="py-2 pr-3 whitespace-nowrap text-gray-700">
                                                                {String((row as any)[k] ?? '')}
                                                            </td>
                                                        ))}
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <button
                                        disabled={!predictionStates[idx].xlsxBase64}
                                        onClick={() => {
                                            const fn = `${detectedTeam}${detectedOpponent ? `_vs_${detectedOpponent}` : ''}_predictions.xlsx`;
                                            downloadBase64Xlsx(predictionStates[idx].xlsxBase64!, fn);
                                        }}
                                        className="bg-gray-800 hover:bg-gray-700 text-white px-3 py-2 rounded text-xs disabled:opacity-40 disabled:cursor-not-allowed"
                                    >
                                        Download Excel
                                    </button>
                                </div>
                            </div>
                        )}
                        {reportStates[idx] && (reportStates[idx].loading || reportStates[idx].error || reportStates[idx].preview) && (
                            <div className="w-full max-w-[85%] mt-2">
                                <ReportPanel reportState={reportStates[idx]} onDownload={() => handleDownloadReport(idx)} /> {/* handle Download report view */}
                            </div>
                        )}
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