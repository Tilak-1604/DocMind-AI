import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';

const MessageBubble = ({ message, userPicture, userName }) => {
    const { role, content } = message;

    if (role === 'system') {
        return (
            <div className="flex justify-center">
                <span className="text-xs text-gray-500 italic bg-white/5 px-4 py-1.5 rounded-full border border-white/5">
                    {content}
                </span>
            </div>
        );
    }

    const isUser = role === 'user';

    return (
        <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, ease: 'easeOut' }}
            className={`flex items-end gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
        >
            {/* Avatar */}
            <div className="flex-shrink-0 w-8 h-8 rounded-xl overflow-hidden border border-white/10">
                {isUser ? (
                    <img
                        src={userPicture || `https://ui-avatars.com/api/?name=${encodeURIComponent(userName || 'U')}&background=6366f1&color=fff&size=64`}
                        alt="You"
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="w-full h-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                    </div>
                )}
            </div>

            {/* Bubble */}
            <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                    isUser
                        ? 'bg-indigo-600 text-white rounded-br-sm shadow-lg shadow-indigo-500/20'
                        : 'bg-white/5 text-gray-200 rounded-bl-sm border border-white/8'
                }`}
            >
                {content}
            </div>
        </motion.div>
    );
};

export default MessageBubble;
