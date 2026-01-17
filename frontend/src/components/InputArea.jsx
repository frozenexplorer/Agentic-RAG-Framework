import React, { useState, useRef } from 'react';
import { Send, Sparkles } from 'lucide-react';

export default function InputArea({ onSend, disabled }) {
    const [input, setInput] = useState('');
    const [shake, setShake] = useState(false);
    const inputRef = useRef(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !disabled) {
            onSend(input);
            setInput('');
            inputRef.current?.focus();
        } else if (!input.trim()) {
            // Shake animation on empty submit
            setShake(true);
            setTimeout(() => setShake(false), 500);
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto px-4 pb-6 pt-2">
            <form onSubmit={handleSubmit} className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl blur opacity-20 group-hover:opacity-30 transition-opacity"></div>
                <div className={`relative flex items-center bg-slate-900/90 border border-slate-700/50 rounded-xl shadow-2xl backdrop-blur-xl overflow-hidden group-focus-within:border-blue-500/50 transition-all ${shake ? 'animate-shake' : ''}`}>

                    <div className="pl-4 pr-2 text-slate-400">
                        <Sparkles size={18} className="transition-transform group-focus-within:scale-110 group-focus-within:text-blue-400" />
                    </div>

                    <input
                        ref={inputRef}
                        type="text"
                        className="w-full bg-transparent border-none text-slate-100 placeholder-slate-400 px-2 py-4 focus:outline-none focus:ring-0 text-base"
                        placeholder="Ask anything about your documents..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        disabled={disabled}
                    />

                    <button
                        type="submit"
                        disabled={!input.trim() || disabled}
                        className={`mr-2 p-2 rounded-lg transition-all duration-200
              ${input.trim() && !disabled
                                ? 'bg-blue-600 text-white hover:bg-blue-500 shadow-lg shadow-blue-500/20 animate-pulse-glow'
                                : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                            }`}
                    >
                        <Send size={18} className={input.trim() && !disabled ? 'transition-transform hover:translate-x-0.5' : ''} />
                    </button>
                </div>
            </form>
            <div className="text-center mt-3">
                <p className="text-xs text-slate-500 font-medium">Powered by Agentic RAG Framework</p>
            </div>
        </div>
    );
}
