import React, { useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Plus, LogOut, Sparkles, X, Trash2 } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const Sidebar = ({ documents, selectedDoc, onSelectDoc, onUpload, onDeleteDoc, isUploading }) => {
    const { user, logout } = useAuth();
    const fileInputRef = useRef(null);

    return (
        <aside className="w-72 flex-shrink-0 flex flex-col h-full glass border-r border-white/5 rounded-3xl m-3 mr-0">
            {/* Logo */}
            <div className="p-6 flex items-center gap-3 border-b border-white/5">
                <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/25 flex-shrink-0">
                    <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-white/60">
                    DocMindAI
                </span>
            </div>

            {/* Upload Button */}
            <div className="px-4 py-4">
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="w-full btn-primary py-3 text-sm gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                >
                    {isUploading ? (
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    ) : (
                        <Plus className="w-4 h-4" />
                    )}
                    {isUploading ? 'Uploading...' : 'Upload PDF'}
                </motion.button>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={onUpload}
                    className="hidden"
                    accept=".pdf,.doc,.docx,.txt"
                />
            </div>

            {/* Documents List */}
            <div className="flex-1 overflow-y-auto px-3 space-y-1">
                <p className="px-3 pt-1 pb-2 text-[10px] font-bold text-gray-600 uppercase tracking-[0.18em]">
                    My Documents
                </p>
                {documents.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 space-y-2 opacity-40">
                        <FileText className="w-7 h-7 text-gray-600" />
                        <p className="text-xs text-gray-500 text-center leading-relaxed">No documents yet.<br/>Upload a PDF to start.</p>
                    </div>
                ) : (
                    <AnimatePresence>
                        {documents.map((doc) => (
                            <motion.div
                                key={doc.id}
                                initial={{ opacity: 0, x: -12 }}
                                animate={{ opacity: 1, x: 0 }}
                                exit={{ opacity: 0, x: -12 }}
                                className={`group flex items-center gap-2.5 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ${
                                    selectedDoc?.id === doc.id
                                        ? 'bg-indigo-500/15 border border-indigo-500/25 text-indigo-300'
                                        : 'hover:bg-white/5 text-gray-400 border border-transparent hover:text-gray-200'
                                }`}
                                onClick={() => onSelectDoc(doc)}
                            >
                                <FileText className={`w-4 h-4 flex-shrink-0 ${selectedDoc?.id === doc.id ? 'text-indigo-400' : 'text-gray-600'}`} />
                                <span className="text-xs font-medium truncate flex-1">{doc.name}</span>
                                <button
                                    onClick={(e) => { e.stopPropagation(); onDeleteDoc(doc.id); }}
                                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 hover:text-red-400 rounded-lg transition-all duration-150"
                                    title="Remove"
                                >
                                    <X className="w-3 h-3" />
                                </button>
                            </motion.div>
                        ))}
                    </AnimatePresence>
                )}
            </div>

            {/* User Profile */}
            <div className="p-4 border-t border-white/5">
                <div className="flex items-center gap-3 p-3 rounded-2xl bg-white/3 border border-white/5">
                    <img
                        src={user?.picture || `https://ui-avatars.com/api/?name=${encodeURIComponent(user?.name || 'U')}&background=6366f1&color=fff&size=64`}
                        alt="Avatar"
                        className="w-9 h-9 rounded-xl border border-white/10 flex-shrink-0 object-cover"
                    />
                    <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-gray-200 truncate">{user?.name || 'User'}</p>
                        <p className="text-[10px] text-gray-500 truncate">{user?.email}</p>
                    </div>
                    <button
                        onClick={logout}
                        title="Logout"
                        className="p-2 hover:bg-red-500/10 rounded-xl text-gray-500 hover:text-red-400 transition-all duration-200 flex-shrink-0"
                    >
                        <LogOut className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
