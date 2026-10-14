import React, { useRef, useEffect } from 'react';
import { Send, Sparkles, Trash2, Plus, MessageSquare } from 'lucide-react';
import MessageBubble from './MessageBubble';
import DocumentChip from './DocumentChip';

const ChatArea = ({ 
    messages, 
    isProcessing, 
    selectedDocuments = [], 
    onSendMessage, 
    onRunTool, 
    onClearChat,
    onAddMoreDocs,
    onRemoveDoc,
    inputValue, 
    setInputValue 
}) => {
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const hasDocs = selectedDocuments.length > 0;

    return (
        <div className="flex flex-col h-full relative">
            {/* Header / Document Chips */}
            <div className="px-6 py-4 flex flex-col gap-2 border-b border-white/5 bg-[#16161e]/50 backdrop-blur-md z-10">
                <div className="flex items-center justify-between">
                    <span className="text-xs text-white/40 font-medium">
                        {hasDocs ? `Using ${selectedDocuments.length} document${selectedDocuments.length !== 1 ? 's' : ''}` : 'No context selected'}
                    </span>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={onClearChat}
                            className="p-1.5 rounded-xl hover:bg-white/5 text-white/30 hover:text-red-400 transition-all group"
                            title="Clear Chat"
                        >
                            <Trash2 size={16} />
                        </button>
                    </div>
                </div>
                <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
                    {selectedDocuments.length > 0 ? (
                        <>
                            {selectedDocuments.map((doc) => (
                                <DocumentChip 
                                    key={doc.id} 
                                    name={doc.name} 
                                    onRemove={() => onRemoveDoc(doc.id)} 
                                />
                            ))}
                            <button 
                                onClick={onAddMoreDocs}
                                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-dashed border-white/20 text-white/40 hover:text-white/80 hover:border-white/40 hover:bg-white/5 transition-all text-sm font-medium whitespace-nowrap"
                            >
                                <Plus size={14} />
                                Add
                            </button>
                        </>
                    ) : (
                        <div className="flex items-center gap-2 text-white/20 italic text-sm">
                            <MessageSquare size={14} />
                            <span>No documents selected</span>
                        </div>
                    )}
                </div>
            </div>


            {/* Messages Area */}
            <div 
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth scrollbar-thin"
            >
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto animate-in fade-in zoom-in duration-700">
                        <div className="w-20 h-20 bg-blue-500/10 rounded-3xl flex items-center justify-center mb-6 border border-blue-500/20">
                            <Sparkles className="text-blue-400 w-10 h-10" />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-3">
                            {hasDocs ? 'How can I help you today?' : 'Select documents first'}
                        </h2>
                        <p className="text-white/40 leading-relaxed">
                            {hasDocs 
                                ? `I've analyzed your ${selectedDocuments.length} document${selectedDocuments.length !== 1 ? 's' : ''}. Ask me for a summary, explain concepts, or find specific details.` 
                                : 'You need to select at least one document from your library before we can start chatting.'}
                        </p>
                        {!hasDocs && (
                            <button
                                onClick={onAddMoreDocs}
                                className="mt-6 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
                            >
                                <Plus size={18} />
                                Select Documents
                            </button>
                        )}
                    </div>
                ) : (
                    messages.map((msg, idx) => (
                        <MessageBubble key={idx} message={msg} />
                    ))
                )}
                {isProcessing && (
                    <div className="flex gap-4 animate-pulse">
                        <div className="w-8 h-8 rounded-xl bg-white/5 border border-white/10 shrink-0" />
                        <div className="space-y-2 flex-1 pt-2">
                            <div className="h-2 bg-white/10 rounded w-1/4" />
                            <div className="h-2 bg-white/5 rounded w-3/4" />
                        </div>
                    </div>
                )}
            </div>

            {/* AI Tools Strip */}
            {hasDocs && (
                <div className="px-6 py-3 border-t border-white/5 bg-white/[0.02] flex items-center justify-between">
                    <div className="flex items-center gap-3 overflow-x-auto no-scrollbar">
                        <button
                            onClick={() => onRunTool('summarize', 'Summary')}
                            disabled={isProcessing}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 disabled:opacity-50 transition-all text-sm font-medium whitespace-nowrap"
                        >
                            <Sparkles size={14} className="text-yellow-400" />
                            Summarize
                        </button>
                        <button
                            onClick={() => onRunTool('flashcards', 'Flashcards')}
                            disabled={isProcessing}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 disabled:opacity-50 transition-all text-sm font-medium whitespace-nowrap"
                        >
                            <Sparkles size={14} className="text-purple-400" />
                            Flashcards
                        </button>
                        <button
                            onClick={() => onRunTool('mind-map', 'Mind Map')}
                            disabled={isProcessing}
                            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-white/60 hover:text-white hover:bg-white/10 disabled:opacity-50 transition-all text-sm font-medium whitespace-nowrap"
                        >
                            <Sparkles size={14} className="text-cyan-400" />
                            Mind Map
                        </button>
                    </div>
                    {selectedDocuments.length > 1 && (
                        <span className="text-[10px] text-white/30 hidden sm:block italic">
                            *Tools currently work on the first document
                        </span>
                    )}
                </div>
            )}

            {/* Input Area */}
            <div className="p-6 pt-2">
                <form 
                    onSubmit={onSendMessage}
                    className={`relative flex items-center transition-all ${!hasDocs ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                    <input
                        type="text"
                        placeholder={hasDocs ? "Ask something about your documents..." : "Select documents to start chatting"}
                        className="w-full bg-white/5 border border-white/10 rounded-2xl pl-6 pr-16 py-4 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-all hover:bg-white/[0.08]"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        disabled={!hasDocs || isProcessing}
                    />
                    <button
                        type="submit"
                        disabled={!inputValue.trim() || isProcessing || !hasDocs}
                        className="absolute right-3 p-2 bg-blue-600 hover:bg-blue-500 disabled:bg-white/10 text-white disabled:text-white/20 rounded-xl transition-all shadow-lg shadow-blue-500/20"
                    >
                        <Send size={20} />
                    </button>
                </form>
                <p className="text-center text-[10px] text-white/20 mt-4 uppercase tracking-widest font-medium">
                    DocMind AI • Secure RAG Intelligence
                </p>
            </div>
        </div>
    );
};

export default ChatArea;
