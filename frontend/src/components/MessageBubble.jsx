import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, FileText, Copy, Check } from 'lucide-react';

export default function MessageBubble({ message, index }) {
    const isUser = message.role === 'user';
    const [copiedCode, setCopiedCode] = useState(null);

    const copyToClipboard = (text, idx) => {
        navigator.clipboard.writeText(text);
        setCopiedCode(idx);
        setTimeout(() => setCopiedCode(null), 2000);
    };

    // Custom components for ReactMarkdown
    const components = {
        code({ node, inline, className, children, ...props }) {
            const codeString = String(children).replace(/\n$/, '');
            const codeIdx = `${index}-${codeString.substring(0, 20)}`;

            if (inline) {
                return <code className={className} {...props}>{children}</code>;
            }

            return (
                <div className="relative group my-2">
                    <pre className="overflow-x-auto">
                        <code className={className} {...props}>{children}</code>
                    </pre>
                    <button
                        onClick={() => copyToClipboard(codeString, codeIdx)}
                        className="absolute top-2 right-2 p-2 rounded bg-slate-700 hover:bg-slate-600 transition-colors opacity-0 group-hover:opacity-100"
                        title="Copy code"
                    >
                        {copiedCode === codeIdx ? (
                            <Check size={14} className="text-green-400" />
                        ) : (
                            <Copy size={14} className="text-slate-300" />
                        )}
                    </button>
                </div>
            );
        }
    };

    return (
        <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
            <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-3`}>
                {/* Avatar with subtle animation */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center transition-transform hover:scale-110
          ${isUser ? 'bg-indigo-600' : 'bg-blue-600'}`}>
                    {isUser ? <User size={16} color="white" /> : <Bot size={16} color="white" />}
                </div>

                {/* Content */}
                <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
                    <div className={`px-5 py-3 rounded-2xl shadow-md backdrop-blur-sm transition-all hover:shadow-lg
            ${isUser
                            ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white rounded-tr-none'
                            : 'bg-slate-800/80 border border-slate-700 text-slate-100 rounded-tl-none'
                        }`}>
                        {isUser ? (
                            <p className="whitespace-pre-wrap">{message.content}</p>
                        ) : (
                            <div className="markdown text-sm sm:text-base">
                                <ReactMarkdown components={components}>{message.content}</ReactMarkdown>
                            </div>
                        )}
                    </div>

                    {/* Sources Section (AI only) */}
                    {!isUser && message.sources && message.sources.length > 0 && (
                        <div className="mt-2 ml-1 flex flex-col gap-1 w-full max-w-md animate-slide-up">
                            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Sources</p>
                            {message.sources.map((src, idx) => (
                                <div key={idx} className="flex items-center gap-2 text-xs text-slate-300 bg-slate-800/50 px-3 py-2 rounded-lg border border-slate-700/50 hover:bg-slate-700/50 hover:border-blue-500/50 transition-all cursor-pointer">
                                    <FileText size={12} className="text-blue-400" />
                                    <span className="truncate">{src}</span>
                                </div>
                            ))}
                        </div>
                    )}

                    <span className="text-[10px] text-slate-500 mt-1 px-1">
                        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>
            </div>
        </div>
    );
}
