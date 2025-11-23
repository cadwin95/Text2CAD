import React, { useMemo, useState } from 'react';
import axios from 'axios';

export default function ChatInterface({ onModelGenerated }) {
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [xmlContent, setXmlContent] = useState('');
    const [enableValidation, setEnableValidation] = useState(false);
    const [model, setModel] = useState('gpt-4o');
    const [pngUrl, setPngUrl] = useState(null);
    const [validation, setValidation] = useState(null);
    const [runs, setRuns] = useState([]); // list of previous generations

    const lastResult = runs[runs.length - 1] || null;

    const parseFeatures = (xml) => {
        if (!xml) return [];
        try {
            const parser = new DOMParser();
            const doc = parser.parseFromString(xml, "text/xml");
            return Array.from(doc.getElementsByTagName("Panel")).map((p) => {
                const name = p.getAttribute("name") || "Unnamed";
                const type = p.getAttribute("type") || "Panel";
                const materialNode = p.getElementsByTagName("Material")[0];
                const thickness = materialNode ? materialNode.getAttribute("thickness") : null;
                const points = Array.from(p.getElementsByTagName("Point")).map((pt) => ({
                    x: pt.getAttribute("x"),
                    y: pt.getAttribute("y"),
                    z: pt.getAttribute("z"),
                }));
                return { name, type, thickness, points };
            });
        } catch {
            return [];
        }
    };

    const computeDiff = (prevXml, currXml) => {
        if (!prevXml) return "No previous OCX - initial generation.";
        const prevLines = new Set(prevXml.split('\n').map((l) => l.trim()).filter(Boolean));
        const currLines = new Set(currXml.split('\n').map((l) => l.trim()).filter(Boolean));
        const added = [...currLines].filter((l) => !prevLines.has(l));
        const removed = [...prevLines].filter((l) => !currLines.has(l));
        const parts = [];
        if (added.length) parts.push("Added:\n" + added.map((l) => `+ ${l}`).join('\n'));
        if (removed.length) parts.push("Removed:\n" + removed.map((l) => `- ${l}`).join('\n'));
        return parts.join('\n') || "No textual diff detected.";
    };

    const sendMessage = async (e) => {
        if (e && e.preventDefault) e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('http://localhost:8000/api/chat', {
                message: input,
                enable_validation: enableValidation,
                model,
                history: messages, // send prior turns for context
                context: lastResult || {} // send last artifacts
            });

            const data = response.data;

            const assistantMsg = { role: 'assistant', content: data.message };
            setMessages(prev => [...prev, assistantMsg]);

            if (data.xml_content) {
                setXmlContent(data.xml_content);
            }

            if (data.validation) {
                setValidation(data.validation);
            } else {
                setValidation(null);
            }

            if (data.model_url) {
                // Construct full URL if relative
                const url = data.model_url.startsWith('http')
                    ? data.model_url
                    : `http://localhost:8000${data.model_url}`;
                onModelGenerated(url);
            } else {
                onModelGenerated(null);
            }

            if (data.png_url) {
                const fullPng = data.png_url.startsWith('http')
                    ? data.png_url
                    : `http://localhost:8000${data.png_url}`;
                setPngUrl(fullPng);
            } else {
                setPngUrl(null);
            }

            // Persist run history with diff/features
            const prevXml = runs.length ? runs[runs.length - 1].xml_content : null;
            const run = {
                id: Date.now(),
                message: data.message,
                model_url: data.model_url ? (data.model_url.startsWith('http') ? data.model_url : `http://localhost:8000${data.model_url}`) : null,
                xml_url: data.xml_url ? (data.xml_url.startsWith('http') ? data.xml_url : `http://localhost:8000${data.xml_url}`) : null,
                png_url: data.png_url ? (data.png_url.startsWith('http') ? data.png_url : `http://localhost:8000${data.png_url}`) : null,
                validation: data.validation || null,
                xml_content: data.xml_content || null,
                builder_code: data.builder_code || null,
                agent_trace: data.agent_trace || null,
                xml_validation: data.xml_validation || null,
                features: parseFeatures(data.xml_content),
                diff: data.xml_content ? computeDiff(prevXml, data.xml_content) : null,
            };
            setRuns((prev) => [...prev, run]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Error processing request." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full bg-gray-800 text-white p-4 overflow-hidden">
            <div className="flex-1 overflow-y-auto space-y-4 pr-1">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 ml-auto' : 'bg-gray-700 mr-auto'} max-w-[80%]`}>
                        {msg.content}
                    </div>
                ))}
                {loading && <div className="text-gray-400">Thinking...</div>}
                
                {runs.length > 0 && (
                    <div className="space-y-2">
                        <div className="text-gray-200 font-semibold">Runs</div>
                        {runs.slice().reverse().map((run, idx) => (
                            <details key={run.id} className="bg-gray-900 rounded border border-gray-700 text-xs" defaultOpen={idx === 0}>
                                <summary className="cursor-pointer px-3 py-2 flex justify-between items-center text-sm text-gray-200">
                                    <span>Run #{runs.length - idx} — {run.message}</span>
                                    <span className="text-gray-400">{run.model_url ? 'OCX+STL' : 'XML only'}</span>
                                </summary>
                                <div className="px-3 pb-3 space-y-2">
                                    <div className="flex flex-wrap gap-2 text-blue-300 underline">
                                        {run.xml_url && <a href={run.xml_url} target="_blank" rel="noreferrer">OCX XML</a>}
                                        {run.model_url && <a href={run.model_url} target="_blank" rel="noreferrer">STL</a>}
                                        {run.png_url && <a href={run.png_url} target="_blank" rel="noreferrer">PNG</a>}
                                    </div>
                                    {run.diff && (
                                        <div className="bg-gray-800 p-2 rounded border border-gray-700 max-h-32 overflow-auto">
                                            <div className="text-gray-200 font-semibold mb-1">OCX Diff</div>
                                            <pre className="whitespace-pre-wrap break-words">{run.diff}</pre>
                                        </div>
                                    )}
                                    {run.features && run.features.length > 0 && (
                                        <div className="grid grid-cols-1 gap-2 max-h-40 overflow-auto">
                                            {run.features.map((p, i) => (
                                                <div key={`${p.name}-${i}`} className="bg-gray-800 rounded p-2 border border-gray-700">
                                                    <div className="text-sm text-white font-semibold">{p.name}</div>
                                                    <div className="text-gray-300 text-xs">Type: {p.type}</div>
                                                    {p.thickness && <div className="text-gray-300 text-xs">Thickness: {p.thickness} mm</div>}
                                                    <div className="text-gray-400 text-xs mt-1">Points: {p.points.length}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                    {run.png_url && (
                                        <div className="max-h-48 overflow-auto bg-gray-900 p-2 rounded border border-gray-700">
                                            <div className="text-sm text-gray-300 mb-2">Rendered PNG</div>
                                            <img src={run.png_url} alt="Rendered" className="w-full rounded border border-gray-700" />
                                        </div>
                                    )}
                                    {run.validation && (
                                        <div className="bg-gray-800 p-2 rounded border border-gray-700 max-h-32 overflow-auto">
                                            <div className="text-gray-200 font-semibold mb-1">Validation</div>
                                            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(run.validation, null, 2)}</pre>
                                        </div>
                                    )}
                                    {run.xml_validation && (
                                        <div className="bg-gray-800 p-2 rounded border border-gray-700 max-h-32 overflow-auto">
                                            <div className="text-gray-200 font-semibold mb-1">XML Sanity</div>
                                            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(run.xml_validation, null, 2)}</pre>
                                        </div>
                                    )}
                                    {run.xml_content && (
                                        <div className="max-h-32 overflow-auto bg-gray-900 p-2 rounded text-xs font-mono border border-gray-700">
                                            <pre>{run.xml_content}</pre>
                                        </div>
                                    )}
                                    {run.builder_code && (
                                        <div className="max-h-48 overflow-auto bg-gray-900 p-2 rounded text-xs font-mono border border-gray-700">
                                            <div className="text-sm text-gray-300 mb-1">Builder Code</div>
                                            <pre className="whitespace-pre">{run.builder_code}</pre>
                                        </div>
                                    )}
                                    {run.agent_trace && (
                                        <div className="max-h-48 overflow-auto bg-gray-900 p-2 rounded text-xs font-mono border border-gray-700">
                                            <div className="text-sm text-gray-300 mb-1">Agent Trace</div>
                                            <pre className="whitespace-pre-wrap break-words">{JSON.stringify(run.agent_trace, null, 2)}</pre>
                                        </div>
                                    )}
                                </div>
                            </details>
                        ))}
                    </div>
                )}
            </div>

            <div className="flex flex-col gap-2 mt-3 shrink-0">
                <div className="flex items-center gap-2">
                    <select
                        className="bg-gray-700 text-sm text-gray-100 rounded-full px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={model}
                        onChange={(e) => setModel(e.target.value)}
                    >
                        <option value="gpt-4o">gpt-4o</option>
                        <option value="gpt-4o-mini">gpt-4o-mini</option>
                        <option value="groq/llama-3.1-8b-instruct">llama-3.1-8b (Groq)</option>
                    </select>
                    <label className="flex items-center gap-2 text-sm text-gray-300">
                        <input
                            type="checkbox"
                            checked={enableValidation}
                            onChange={(e) => setEnableValidation(e.target.checked)}
                        />
                        VLM 검증
                    </label>
                </div>
                <form onSubmit={sendMessage} className="flex items-center gap-2 bg-gray-700 rounded-full px-3 py-2 shadow-inner">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none px-2"
                        placeholder="Describe the ship structure..."
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-10 h-10 flex items-center justify-center bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-full text-white font-bold"
                        title="Send"
                    >
                        ↑
                    </button>
                </form>
            </div>
        </div>
    );
}
