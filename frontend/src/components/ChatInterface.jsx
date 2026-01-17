import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import MessageBubble from './MessageBubble';
import InputArea from './InputArea';
import { Loader2 } from 'lucide-react';

export default function ChatInterface() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hello! I'm your Agentic RAG assistant. Ask me anything about your documents." }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState('');
    const [typingMessage, setTypingMessage] = useState('');
    const [typingProgress, setTypingProgress] = useState(0);
    const [isTyping, setIsTyping] = useState(false);
    const [pendingSources, setPendingSources] = useState([]);
    const messagesEndRef = useRef(null);
    const typingTimerRef = useRef(null);

    useEffect(() => {
        // Generate simple Session ID
        const sid = 'sess_' + Math.random().toString(36).substr(2, 9);
        setSessionId(sid);
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    // Smooth typing animation effect - letter by letter
    useEffect(() => {
        if (!isTyping || !typingMessage) {
            setTypingProgress(0);
            return;
        }

        if (typingProgress >= typingMessage.length) {
            // Typing complete
            setIsTyping(false);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: typingMessage,
                sources: pendingSources
            }]);
            setTypingMessage('');
            setTypingProgress(0);
            setPendingSources([]);
            return;
        }

        // Smooth character-by-character reveal (like ChatGPT/Gemini)
        const typingSpeed = 3; // milliseconds per character (faster = smoother)
        typingTimerRef.current = setTimeout(() => {
            setTypingProgress(prev => prev + 1);
        }, typingSpeed);

        return () => {
            if (typingTimerRef.current) {
                clearTimeout(typingTimerRef.current);
            }
        };
    }, [isTyping, typingMessage, typingProgress, pendingSources]);

    const handleSend = async (text) => {
        // Add User Message with fade-in animation
        const userMsg = { role: 'user', content: text };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);

        try {
            // Call API (using proxy)
            const response = await fetch('/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: text,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Start typing animation with sources
            setPendingSources(data.source || []);
            setTypingMessage(data.answer);
            setTypingProgress(0);
            setIsTyping(true);

        } catch (error) {
            console.error("Error:", error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "**Error:** Could not connect to the backend. Please ensure the API server is running and accessible."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    // Get the currently typing text to display
    const displayedTypingText = typingMessage.substring(0, typingProgress);

    return (
        <div className="flex flex-col h-screen bg-transparent">
            <Header />

            {/* Messages Area */}
            <main className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.map((msg, idx) => (
                        <MessageBubble key={idx} message={msg} index={idx} />
                    ))}

                    {/* Typing indicator with smooth letter-by-letter animation */}
                    {isTyping && typingMessage && (
                        <div className="flex w-full mb-6 justify-start animate-fade-in">
                            <div className="flex max-w-[80%] flex-row gap-3">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center bg-blue-600">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                        <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                    </svg>
                                </div>
                                <div className="flex flex-col items-start">
                                    <div className="px-5 py-3 rounded-2xl shadow-md backdrop-blur-sm bg-slate-800/80 border border-slate-700 text-slate-100 rounded-tl-none min-h-[3rem]">
                                        <div className="markdown text-sm sm:text-base">
                                            {displayedTypingText}
                                            <span className="inline-block w-0.5 h-4 bg-blue-500 ml-0.5 animate-pulse"></span>
                                        </div>
                                    </div>

                                    {/* Show sources if available during typing */}
                                    {pendingSources && pendingSources.length > 0 && (
                                        <div className="mt-2 ml-1 flex flex-col gap-1 w-full max-w-md animate-slide-up">
                                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Sources</p>
                                            {pendingSources.map((src, idx) => (
                                                <div key={idx} className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800/50 px-3 py-2 rounded-lg border border-slate-700/50">
                                                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-blue-400">
                                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                                        <polyline points="14 2 14 8 20 8"></polyline>
                                                        <line x1="16" y1="13" x2="8" y2="13"></line>
                                                        <line x1="16" y1="17" x2="8" y2="17"></line>
                                                        <polyline points="10 9 9 9 8 9"></polyline>
                                                    </svg>
                                                    <span className="truncate">{src}</span>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Loading indicator */}
                    {isLoading && !isTyping && (
                        <div className="flex items-center gap-3 animate-pulse">
                            <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center">
                                <Loader2 size={16} className="text-blue-500 animate-spin" />
                            </div>
                            <div className="flex gap-1">
                                <div className="w-2 h-2 rounded-full bg-blue-500" style={{ animation: 'typing-dot 1.4s infinite', animationDelay: '0s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-blue-500" style={{ animation: 'typing-dot 1.4s infinite', animationDelay: '0.2s' }}></div>
                                <div className="w-2 h-2 rounded-full bg-blue-500" style={{ animation: 'typing-dot 1.4s infinite', animationDelay: '0.4s' }}></div>
                            </div>
                            <div className="text-slate-500 text-sm">AI is thinking...</div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </main>

            {/* Input Area */}
            <div className="flex-none bg-gradient-to-t from-slate-950 via-slate-950 to-transparent pt-10">
                <InputArea onSend={handleSend} disabled={isLoading || isTyping} />
            </div>
        </div>
    );
}
