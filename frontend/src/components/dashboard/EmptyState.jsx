import React from 'react';
import { motion } from 'framer-motion';
import { Upload, MessageSquare, Sparkles } from 'lucide-react';

const SUGGESTION_CHIPS = [
    "Summarize the key points of this document",
    "What are the main arguments presented?",
    "Explain the most important concept in simple terms",
];

const EmptyState = ({ hasDocument, onSuggestionClick }) => {
    if (!hasDocument) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-5">
                <motion.div
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.1, duration: 0.4, ease: 'backOut' }}
                    className="w-20 h-20 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center"
                >
                    <Upload className="w-9 h-9 text-indigo-400" />
                </motion.div>
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="space-y-2"
                >
                    <h3 className="text-xl font-bold text-white">Upload a Document to Begin</h3>
                    <p className="text-gray-500 text-sm max-w-xs leading-relaxed">
                        Upload a PDF and I'll analyze it instantly. Then ask me anything about it.
                    </p>
                </motion.div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col items-center justify-center text-center p-8 space-y-6">
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.4, ease: 'backOut' }}
                className="w-20 h-20 rounded-3xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center"
            >
                <MessageSquare className="w-9 h-9 text-indigo-400" />
            </motion.div>
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="space-y-2"
            >
                <h3 className="text-xl font-bold text-white">Ask Anything</h3>
                <p className="text-gray-500 text-sm max-w-xs leading-relaxed">
                    Your document is ready. Start the conversation below, or try one of these:
                </p>
            </motion.div>
            <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex flex-col gap-2 w-full max-w-sm"
            >
                {SUGGESTION_CHIPS.map((chip, i) => (
                    <button
                        key={i}
                        onClick={() => onSuggestionClick(chip)}
                        className="w-full text-left px-4 py-3 rounded-xl bg-white/5 border border-white/8 text-gray-400 text-xs hover:bg-white/10 hover:text-white hover:border-indigo-500/30 transition-all duration-200 flex items-start gap-2"
                    >
                        <Sparkles className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                        {chip}
                    </button>
                ))}
            </motion.div>
        </div>
    );
};

export default EmptyState;
