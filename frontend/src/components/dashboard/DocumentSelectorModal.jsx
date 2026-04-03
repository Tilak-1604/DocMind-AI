import React, { useState, useEffect } from 'react';
import { X, Search, FileText, Check, Plus } from 'lucide-react';

const DocumentSelectorModal = ({ isOpen, onClose, documents, onConfirm, initialSelectedIds = [] }) => {
    const [selectedIds, setSelectedIds] = useState(initialSelectedIds);
    const [searchQuery, setSearchQuery] = useState('');

    useEffect(() => {
        if (isOpen) {
            setSelectedIds(initialSelectedIds);
        }
    }, [isOpen, initialSelectedIds]);

    if (!isOpen) return null;

    const filteredDocs = documents.filter(doc =>
        doc.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const toggleDocument = (id) => {
        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(i => i !== id)
                : [...prev, id]
        );
    };

    const handleConfirm = () => {
        const selectedDocs = documents.filter(doc => selectedIds.includes(doc.id));
        onConfirm(selectedDocs);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
            <div className="w-full max-w-lg bg-[#1a1a24] border border-white/10 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh] animate-in slide-in-from-bottom-4 duration-300">
                
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
                    <h2 className="text-xl font-semibold text-white">Select Documents</h2>
                    <button onClick={onClose} className="p-2 rounded-full hover:bg-white/5 text-white/40 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Search */}
                <div className="px-6 py-4 border-b border-white/5 bg-white/5">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" size={18} />
                        <input
                            type="text"
                            placeholder="Search documents..."
                            className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-white text-sm placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500/40 transition-all hover:bg-white/10"
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />
                    </div>
                </div>

                {/* List */}
                <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1 scrollbar-thin">
                    {filteredDocs.length > 0 ? (
                        filteredDocs.map((doc) => {
                            const isSelected = selectedIds.includes(doc.id);
                            return (
                                <div
                                    key={doc.id}
                                    onClick={() => toggleDocument(doc.id)}
                                    className={`flex items-center justify-between px-4 py-3 rounded-xl cursor-pointer transition-all border group ${
                                        isSelected 
                                            ? 'bg-blue-500/10 border-blue-500/30' 
                                            : 'bg-transparent border-transparent hover:bg-white/5'
                                    }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg transition-colors ${
                                            isSelected ? 'bg-blue-500/20 text-blue-400' : 'bg-white/5 text-white/30 group-hover:text-white/60'
                                        }`}>
                                            <FileText size={20} />
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-white/90 truncate max-w-[280px]">
                                                {doc.name}
                                            </p>
                                            <p className="text-xs text-white/30">
                                                Uploaded {new Date(doc.uploadDate).toLocaleDateString()}
                                            </p>
                                        </div>
                                    </div>
                                    
                                    <div className={`w-5 h-5 rounded-md border flex items-center justify-center transition-all ${
                                        isSelected 
                                            ? 'bg-blue-500 border-blue-500' 
                                            : 'border-white/20'
                                    }`}>
                                        {isSelected && <Check size={14} className="text-white" />}
                                    </div>
                                </div>
                            );
                        })
                    ) : (
                        <div className="flex flex-col items-center justify-center py-12 text-white/30">
                            <FileText size={48} className="mb-4 opacity-10" />
                            <p className="text-sm font-medium">No documents found</p>
                            <p className="text-xs">Try a different search or upload more documents.</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-white/5 border-t border-white/5 flex items-center justify-between">
                    <p className="text-xs text-white/30">
                        {selectedIds.length} document{selectedIds.length !== 1 && 's'} selected
                    </p>
                    <div className="flex gap-3">
                        <button
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-white/60 hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleConfirm}
                            disabled={selectedIds.length === 0}
                            className={`px-6 py-2 rounded-xl text-sm font-semibold transition-all shadow-lg ${
                                selectedIds.length > 0 
                                    ? 'bg-blue-600 hover:bg-blue-500 text-white shadow-blue-500/20' 
                                    : 'bg-white/5 text-white/20 cursor-not-allowed shadow-none'
                            }`}
                        >
                            Start Chat
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DocumentSelectorModal;
