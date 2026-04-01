import React, { useRef, useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Trash2, FileText, List, BookOpen, Brain, FlaskConical } from 'lucide-react';
import MessageBubble from './MessageBubble';
import EmptyState from './EmptyState';
import { useAuth } from '../../context/AuthContext';

const TypingIndicator = () => (
    <div className="flex items-end gap-3">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 border border-white/10">
            <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="currentColor">
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
            </svg>
        </div>
        <div className="bg-white/5 border border-white/8 rounded-2xl rounded-bl-sm px-4 py-3">
            <div className="flex gap-1.5 items-center h-4">
                {[0, 1, 2].map(i => (
                    <motion.div
                        key={i}
                        className="w-1.5 h-1.5 bg-indigo-400 rounded-full"
                        animate={{ y: [0, -5, 0] }}
                        transition={{ duration: 0.6, delay: i * 0.15, repeat: Infinity }}
                    />
                ))}
            </div>
        </div>
    </div>
);

const AI_TOOLS = [
    { label: 'Summarize', icon: List, tool: 'summarize' },
    { label: 'Flashcards', icon: BookOpen, tool: 'flashcards' },
    { label: 'Study Mode', icon: FlaskConical, tool: 'study' },
    { label: 'Mind Map', icon: Brain, tool: 'mind-map' },
];

const ChatArea = ({ messages, isProcessing, selectedDoc, onSendMessage, onRunTool, onClearChat, inputValue, setInputValue }) => {
    const chatEndRef = useRef(null);
    const { user } = useAuth();

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isProcessing]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            onSendMessage(e);
        }
    };

    return (
        <main className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <header className="flex-shrink-0 flex items-center justify-between px-6 py-4 border-b border-white/5 bg-black/10 backdrop-blur-sm">
                <div className="flex items-center gap-2.5">
                    {selectedDoc ? (
                        <>
                            <div className="w-8 h-8 rounded-xl bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center">
                                <FileText className="w-4 h-4 text-indigo-400" />
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-white leading-tight truncate max-w-[250px]">{selectedDoc.name}</p>
                                <p className="text-[10px] text-indigo-400">Ready to chat</p>
                            </div>
                        </>
                    ) : (
                        <div>
                            <p className="text-sm font-semibold text-gray-400">No document selected</p>
                            <p className="text-[10px] text-gray-600">Upload a PDF to begin</p>
                        </div>
                    )}
                </div>

                {/* AI Tool Buttons */}
                <div className="flex items-center gap-1">
                    {AI_TOOLS.map(({ label, icon: Icon, tool }) => (
                        <button
                            key={tool}
                            onClick={() => onRunTool(tool, label)}
                            disabled={!selectedDoc || isProcessing}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-400 hover:bg-white/10 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-150 border border-transparent hover:border-white/10"
                            title={label}
                        >
                            <Icon className="w-3.5 h-3.5" />
                            <span className="hidden lg:inline">{label}</span>
                        </button>
                    ))}
                    {messages.length > 0 && (
                        <button
                            onClick={onClearChat}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-gray-500 hover:bg-red-500/10 hover:text-red-400 transition-all duration-150 border border-transparent ml-1"
                            title="Clear chat"
                        >
                            <Trash2 className="w-3.5 h-3.5" />
                        </button>
                    )}
                </div>
            </header>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
                {messages.length === 0 ? (
                    <EmptyState
                        hasDocument={!!selectedDoc}
                        onSuggestionClick={(text) => {
                            setInputValue(text);
                        }}
                    />
                ) : (
                    <>
                        {messages.map((msg, i) => (
                            <MessageBubble
                                key={i}
                                message={msg}
                                userPicture={user?.picture}
                                userName={user?.name}
                            />
                        ))}
                        {isProcessing && <TypingIndicator />}
                    </>
                )}
                <div ref={chatEndRef} />
            </div>

            {/* Input Bar */}
            <div className="flex-shrink-0 px-6 py-4 border-t border-white/5 bg-black/10">
                <form onSubmit={onSendMessage} className="flex items-end gap-3 max-w-4xl mx-auto">
                    <div className="flex-1 relative">
                        <textarea
                            rows={1}
                            placeholder={selectedDoc ? 'Ask anything about your document...' : 'Upload a document to start asking questions'}
                            disabled={!selectedDoc || isProcessing}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyDown={handleKeyDown}
                            className="w-full input-field pr-4 resize-none overflow-hidden leading-relaxed disabled:opacity-40 disabled:cursor-not-allowed"
                            style={{ minHeight: '44px', maxHeight: '120px' }}
                            onInput={(e) => {
                                e.target.style.height = 'auto';
                                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                            }}
                        />
                    </div>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        disabled={!selectedDoc || !inputValue.trim() || isProcessing}
                        className="w-11 h-11 flex-shrink-0 bg-indigo-600 hover:bg-indigo-500 rounded-xl flex items-center justify-center text-white shadow-lg shadow-indigo-500/25 disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-200"
                    >
                        <Send className="w-4 h-4" />
                    </motion.button>
                </form>
                <p className="text-center text-[10px] text-gray-700 mt-2">
                    DocMindAI can make mistakes. Verify important information independently.
                </p>
            </div>
        </main>
    );
};

export default ChatArea;
