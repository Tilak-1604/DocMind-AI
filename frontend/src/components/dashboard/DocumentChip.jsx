import React from 'react';
import { X, FileText } from 'lucide-react';

const DocumentChip = ({ name, onRemove }) => {
    return (
        <div className="flex items-center gap-2 px-3 py-1.5 bg-white/10 hover:bg-white/15 border border-white/5 rounded-full backdrop-blur-md transition-all duration-200 group animate-in fade-in zoom-in duration-300">
            <FileText size={14} className="text-blue-400" />
            <span className="text-sm font-medium text-white/90 max-w-[120px] truncate">{name}</span>
            <button
                onClick={onRemove}
                className="p-0.5 rounded-full hover:bg-red-500/20 text-white/40 hover:text-red-400 transition-colors"
                title="Remove Document"
            >
                <X size={14} />
            </button>
        </div>
    );
};

export default DocumentChip;
