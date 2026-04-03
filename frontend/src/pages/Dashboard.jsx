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

            toast.success(`"${file.name}" uploaded successfully!`, { id: toastId });
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
        setIsModalOpen(true);
    };

    const handleConfirmSelection = async (docs) => {
        await createNewSession(docs);
    };

    const handleAddMoreDocs = () => {
        setIsModalOpen(true);
    };

    const handleRemoveDoc = (docId) => {
        const updated = selectedDocuments.filter(d => d.id !== docId);
        setSelectedDocuments(updated);
        // Bonus: In a real app we might want to update the ChatSession entity in DB too
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
                onClose={() => setIsModalOpen(false)}
                documents={allDocuments}
                onConfirm={handleConfirmSelection}
                initialSelectedIds={selectedDocuments.map(d => d.id)}
            />
        </div>
    );
};

export default Dashboard;
