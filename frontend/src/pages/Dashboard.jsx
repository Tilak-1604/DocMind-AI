import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Sidebar from '../components/dashboard/Sidebar';
import ChatArea from '../components/dashboard/ChatArea';
import DocumentSelectorModal from '../components/dashboard/DocumentSelectorModal';

const Dashboard = () => {
    const { user, status } = useAuth();
    const navigate = useNavigate();

    // Core state
    const [chatSessions, setChatSessions] = useState([]);
    const [activeSession, setActiveSession] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    // Document Specific State
    const [allDocuments, setAllDocuments] = useState([]);
    const [selectedDocuments, setSelectedDocuments] = useState([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [documentModalMode, setDocumentModalMode] = useState('new'); // 'new' | 'update'

    // Redirect if unauthenticated
    useEffect(() => {
        if (status === 'unauthenticated') {
            navigate('/login');
        }
    }, [status, navigate]);

    // Load data on mount
    useEffect(() => {
        if (status === 'authenticated') {
            loadChatSessions();
            loadAllDocuments();
        }
    }, [status]);

    const loadChatSessions = async () => {
        try {
            const res = await api.get('/api/chats');
            setChatSessions(res.data || []);
        } catch (err) {
            console.error('Failed to load chat sessions:', err);
        }
    };

    const loadAllDocuments = async () => {
        try {
            const res = await api.get('/api/documents');
            setAllDocuments(res.data || []);
        } catch (err) {
            console.error('Failed to load documents:', err);
        }
    };

    // Load messages and selected docs when a session is selected
    const handleSelectSession = useCallback(async (session) => {
        setActiveSession(session);
        setSelectedDocuments(session.documents || []);
        try {
            const res = await api.get(`/api/chats/${session.id}`);
            const loadedMessages = (res.data.messages || []).map(m => ({
                role: m.role,
                content: m.content
            }));
            setMessages(loadedMessages);
        } catch (err) {
            console.error('Failed to load messages:', err);
            toast.error('Failed to load chat history');
            setMessages([]);
        }
    }, []);

    // Save a message to the backend
    const saveMessageToBackend = async (sessionId, role, content) => {
        try {
            await api.post(`/api/chats/${sessionId}/messages`, { role, content });
        } catch (err) {
            console.error('Failed to save message:', err);
        }
    };

    // Create a new session with multiple documents
    const createNewSession = async (docs) => {
        try {
            const docIds = docs.map(d => d.id);
            
            // 1. Start a new AI conversation first
            const params = new URLSearchParams({ user_id: user.id || user.email });
            const aiRes = await api.post('/api/documents/start-conversation', params);
            const conversationId = aiRes.data?.conversation_id || aiRes.data;

            // 2. Create the persistent chat session in Spring Boot
            const res = await api.post('/api/chats', {
                title: 'New Chat',
                documentIds: docIds,
                conversationId: conversationId
            });
            
            const newSession = res.data;
            setChatSessions(prev => [newSession, ...prev]);
            setActiveSession(newSession);
            setSelectedDocuments(newSession.documents || []);
            setMessages([]);
            
            return newSession;
        } catch (err) {
            console.error('Failed to create session:', err);
            toast.error('Failed to create chat session');
            return null;
        }
    };

    // Document upload
    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        e.target.value = '';

        setIsUploading(true);
        const toastId = toast.loading(`Uploading ${file.name}...`);

        const docId = `${Date.now()}`;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', user.id || user.email);
        formData.append('doc_id', docId);

        try {
            await api.post('/api/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });

            toast((t) => (
                <div className="flex flex-col gap-2">
                    <span className="font-semibold text-white">"{file.name}" uploaded successfully!</span>
                    <button 
                        onClick={() => {
                            toast.dismiss(t.id);
                            setDocumentModalMode('new');
                            setIsModalOpen(true);
                        }}
                        className="px-3 py-1.5 bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 rounded-lg text-sm font-medium transition-colors border border-blue-500/20 w-full"
                    >
                        Start Chat with this document
                    </button>
                </div>
            ), { id: toastId, duration: 5000 });
            loadAllDocuments(); // Refresh the list
        } catch (err) {
            console.error('Upload error:', err);
            toast.error(err.response?.data || 'Upload failed.', { id: toastId });
        } finally {
            setIsUploading(false);
        }
    };

    // Delete a chat session
    const handleDeleteSession = async (sessionId) => {
        try {
            await api.delete(`/api/chats/${sessionId}`);
            setChatSessions(prev => prev.filter(s => s.id !== sessionId));
            if (activeSession?.id === sessionId) {
                setActiveSession(null);
                setMessages([]);
                setSelectedDocuments([]);
            }
            toast.success('Chat deleted');
        } catch (err) {
            console.error('Failed to delete session:', err);
            toast.error('Failed to delete chat');
        }
    };

    // Send chat message
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || !activeSession || selectedDocuments.length === 0) return;

        const userMessage = { role: 'user', content: inputValue.trim() };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsProcessing(true);

        saveMessageToBackend(activeSession.id, userMessage.role, userMessage.content);

        try {
            const formData = new FormData();
            formData.append('user_id', user.id || user.email);
            formData.append('conversation_id', activeSession.conversationId || '');
            formData.append('question', userMessage.content);
            
            // Pass all selected document external IDs to the AI service
            const externalDocIds = selectedDocuments.map(d => d.docId).join(',');
            formData.append('document_ids', externalDocIds);

            const res = await api.post('/api/documents/chat', formData);
            const answer = res.data?.answer || res.data || 'No response received.';
            const assistantMsg = { role: 'assistant', content: answer };
            setMessages(prev => [...prev, assistantMsg]);

            saveMessageToBackend(activeSession.id, assistantMsg.role, assistantMsg.content);
        } catch (err) {
            console.error('Chat error:', err);
            toast.error('AI response failed.');
            const errMsg = { role: 'system', content: 'Error: Could not reach the AI service.' };
            setMessages(prev => [...prev, errMsg]);
            saveMessageToBackend(activeSession.id, errMsg.role, errMsg.content);
        } finally {
            setIsProcessing(false);
        }
    };

    // Tools handling (modified to use first doc or handle multi)
    const handleRunTool = async (toolEndpoint, toolLabel) => {
        const firstDoc = selectedDocuments[0];
        if (!firstDoc) {
            toast.error('Please select at least one document.');
            return;
        }
        if (isProcessing) return;

        setIsProcessing(true);
        const toastId = toast.loading(`Generating ${toolLabel}...`);

        try {
            const params = new URLSearchParams({ user_id: user.id || user.email });
            const res = await api.post(`/api/documents/${firstDoc.docId}/${toolEndpoint}`, params);

            let content = '';
            const data = res.data;
            if (typeof data === 'string') content = data;
            else if (data?.summary) content = `📄 Summary (for ${firstDoc.name}):\n\n${data.summary}`;
            else if (data?.flashcards) content = `🃏 Flashcards (for ${firstDoc.name}):\n\n${data.flashcards.map(f => `Q: ${f.question}\nA: ${f.answer}`).join('\n\n')}`;
            else if (data?.mind_map) content = `🧠 Mind Map (for ${firstDoc.name}):\n\n${data.mind_map}`;
            else content = JSON.stringify(data, null, 2);

            toast.success(`${toolLabel} complete!`, { id: toastId });
            const assistantMsg = { role: 'assistant', content };
            setMessages(prev => [...prev, assistantMsg]);
            saveMessageToBackend(activeSession.id, assistantMsg.role, assistantMsg.content);
        } catch (err) {
            console.error(`${toolLabel} error:`, err);
            toast.error(`${toolLabel} failed.`, { id: toastId });
        } finally {
            setIsProcessing(false);
        }
    };

    const handleClearChat = () => {
        setMessages([]);
        toast.success('Chat cleared.');
    };

    const handleNewChat = () => {
        setDocumentModalMode('new');
        setIsModalOpen(true);
    };

    const updateChatDocuments = async (newDocs) => {
        if (!activeSession) return;
        if (newDocs.length === 0) {
            toast.error('Cannot update with empty document list.');
            return;
        }

        // The modal returns the exact deduplicated final list of documents based on ID selection.
        const mergedIds = Array.from(new Set(newDocs.map(d => d.id)));
        const finalDocs = allDocuments.filter(d => mergedIds.includes(d.id));

        try {
            const res = await api.put(`/api/chats/${activeSession.id}/documents`, {
                documentIds: mergedIds
            });
            
            setSelectedDocuments(finalDocs);
            const systemMsg = { role: 'system', content: 'Context updated. New responses will use updated documents.' };
            setMessages(prev => [...prev, systemMsg]);
            
            toast.success('Context updated', {
                icon: '🔄',
                style: { borderRadius: '10px', background: '#333', color: '#fff' }
            });
        } catch (err) {
            console.error('Failed to update chat context', err);
            toast.error(err.response?.data?.error || 'Failed to update document context.');
        }
    };

    const handleConfirmSelection = async (docs) => {
        if (documentModalMode === 'new') {
            await createNewSession(docs);
        } else {
            await updateChatDocuments(docs);
        }
    };

    const handleAddMoreDocs = () => {
        setDocumentModalMode('update');
        setIsModalOpen(true);
    };

    const handleRemoveDoc = async (docId) => {
        if (!activeSession) return;
        
        const remainingDocs = selectedDocuments.filter(d => d.id !== docId);
        
        if (remainingDocs.length === 0) {
            if (!window.confirm("Removing this will disable chat. Continue?")) {
                return;
            }
        }

        if (remainingDocs.length === 0) {
            // Cannot clear via PUT (rejected by backend), we just visually clear and chat is disabled
            setSelectedDocuments([]);
            toast('Context cleared. Chat disabled.', { icon: '⚠️' });
            return;
        }

        try {
            const mergedIds = remainingDocs.map(d => d.id);
            await api.put(`/api/chats/${activeSession.id}/documents`, {
                documentIds: mergedIds
            });
            
            setSelectedDocuments(remainingDocs);
            const systemMsg = { role: 'system', content: 'Context updated. New responses will use updated documents.' };
            setMessages(prev => [...prev, systemMsg]);
            
            toast.success(`Context updated: ${remainingDocs.length} documents remaining`, {
                icon: '🗑️',
                style: { borderRadius: '10px', background: '#333', color: '#fff' }
            });
        } catch (err) {
            toast.error('Failed to remove document.');
        }
    };

    return (
        <div className="flex h-screen w-full overflow-hidden" style={{ background: '#0d0d12' }}>
            <Sidebar
                chatSessions={chatSessions}
                activeSession={activeSession}
                onSelectSession={handleSelectSession}
                onUpload={handleUpload}
                onDeleteSession={handleDeleteSession}
                onNewChat={handleNewChat}
                isUploading={isUploading}
            />
            <div className="flex-1 flex flex-col m-3 ml-3 glass rounded-3xl overflow-hidden">
                <ChatArea
                    messages={messages}
                    isProcessing={isProcessing}
                    selectedDocuments={selectedDocuments}
                    onSendMessage={handleSendMessage}
                    onRunTool={handleRunTool}
                    onClearChat={handleClearChat}
                    onAddMoreDocs={handleAddMoreDocs}
                    onRemoveDoc={handleRemoveDoc}
                    inputValue={inputValue}
                    setInputValue={setInputValue}
                />
            </div>

            <DocumentSelectorModal
                isOpen={isModalOpen}
                mode={documentModalMode}
                onClose={() => setIsModalOpen(false)}
                documents={allDocuments}
                onConfirm={handleConfirmSelection}
                initialSelectedIds={documentModalMode === 'new' ? [] : selectedDocuments.map(d => d.id)}
            />
        </div>
    );
};

export default Dashboard;
