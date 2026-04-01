import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import Sidebar from '../components/dashboard/Sidebar';
import ChatArea from '../components/dashboard/ChatArea';

const Dashboard = () => {
    const { user, status } = useAuth();
    const navigate = useNavigate();

    // Core state
    const [documents, setDocuments] = useState([]);
    const [selectedDoc, setSelectedDoc] = useState(null);
    const [conversationId, setConversationId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);

    // Redirect if unauthenticated
    useEffect(() => {
        if (status === 'unauthenticated') {
            navigate('/login');
        }
    }, [status, navigate]);

    // Start a fresh conversation on mount
    useEffect(() => {
        const startConversation = async () => {
            if (user && !conversationId && status === 'authenticated') {
                try {
                    const params = new URLSearchParams({ user_id: user.id || user.email });
                    const res = await api.post('/api/documents/start-conversation', params);
                    // backend returns conversation_id in various locations — handle both
                    const cid = res.data?.conversation_id || res.data;
                    setConversationId(cid);
                } catch (err) {
                    console.error('Failed to start conversation:', err);
                }
            }
        };
        startConversation();
    }, [user, conversationId, status]);

    // When a new document is selected, clear chat
    const handleSelectDoc = useCallback((doc) => {
        setSelectedDoc(doc);
        setMessages([{
            role: 'system',
            content: `Switched to "${doc.name}". Ask me anything about it.`
        }]);
    }, []);

    // Document upload
    const handleUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        // Reset input so the same file can be re-uploaded
        e.target.value = '';

        setIsUploading(true);
        const toastId = toast.loading(`Uploading ${file.name}...`);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('user_id', user.id || user.email);
        const docId = `${Date.now()}`;
        formData.append('doc_id', docId);

        try {
            await api.post('/api/documents/upload', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            const newDoc = { id: docId, name: file.name };
            setDocuments(prev => [...prev, newDoc]);
            handleSelectDoc(newDoc);
            toast.success(`"${file.name}" ready to chat!`, { id: toastId });
        } catch (err) {
            console.error('Upload error:', err);
            toast.error(
                err.response?.data || 'Upload failed. Check your connection.',
                { id: toastId }
            );
        } finally {
            setIsUploading(false);
        }
    };

    // Remove document from list
    const handleDeleteDoc = (docId) => {
        setDocuments(prev => prev.filter(d => d.id !== docId));
        if (selectedDoc?.id === docId) {
            setSelectedDoc(null);
            setMessages([]);
        }
    };

    // Send chat message
    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!inputValue.trim() || !conversationId || !selectedDoc) return;

        const userMessage = { role: 'user', content: inputValue.trim() };
        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsProcessing(true);

        try {
            const params = new URLSearchParams({
                user_id: user.id || user.email,
                conversation_id: conversationId,
                question: userMessage.content
            });
            const res = await api.post('/api/documents/chat', params);
            const answer = res.data?.answer || res.data || 'No response received.';
            setMessages(prev => [...prev, { role: 'assistant', content: answer }]);
        } catch (err) {
            console.error('Chat error:', err);
            toast.error('AI response failed. The service may be unavailable.');
            setMessages(prev => [...prev, {
                role: 'system',
                content: 'Error: Could not reach the AI service. Please try again.'
            }]);
        } finally {
            setIsProcessing(false);
        }
    };

    // AI tool runner
    const handleRunTool = async (toolEndpoint, toolLabel) => {
        if (!selectedDoc) {
            toast.error('Please select a document first.');
            return;
        }
        if (isProcessing) return;

        setIsProcessing(true);
        const toastId = toast.loading(`Generating ${toolLabel}...`);

        try {
            const params = new URLSearchParams({ user_id: user.id || user.email });
            const res = await api.post(`/api/documents/${selectedDoc.id}/${toolEndpoint}`, params);

            let content = '';
            const data = res.data;
            if (typeof data === 'string') {
                content = data;
            } else if (data?.summary) {
                content = `📄 Summary:\n\n${data.summary}`;
            } else if (data?.flashcards) {
                content = `🃏 Flashcards:\n\n${data.flashcards.map(f => `Q: ${f.question}\nA: ${f.answer}`).join('\n\n')}`;
            } else if (data?.mind_map) {
                content = `🧠 Mind Map:\n\n${data.mind_map}`;
            } else {
                content = JSON.stringify(data, null, 2);
            }

            toast.success(`${toolLabel} complete!`, { id: toastId });
            setMessages(prev => [...prev, { role: 'assistant', content }]);
        } catch (err) {
            console.error(`${toolLabel} error:`, err);
            toast.error(`${toolLabel} failed.`, { id: toastId });
        } finally {
            setIsProcessing(false);
        }
    };

    // Clear chat
    const handleClearChat = () => {
        setMessages([]);
        toast.success('Chat cleared.');
    };

    return (
        <div className="flex h-screen w-full overflow-hidden" style={{ background: '#0d0d12' }}>
            <Sidebar
                documents={documents}
                selectedDoc={selectedDoc}
                onSelectDoc={handleSelectDoc}
                onUpload={handleUpload}
                onDeleteDoc={handleDeleteDoc}
                isUploading={isUploading}
            />
            <div className="flex-1 flex flex-col m-3 ml-3 glass rounded-3xl overflow-hidden">
                <ChatArea
                    messages={messages}
                    isProcessing={isProcessing}
                    selectedDoc={selectedDoc}
                    onSendMessage={handleSendMessage}
                    onRunTool={handleRunTool}
                    onClearChat={handleClearChat}
                    inputValue={inputValue}
                    setInputValue={setInputValue}
                />
            </div>
        </div>
    );
};

export default Dashboard;
