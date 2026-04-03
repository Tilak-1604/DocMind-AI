-- DocMind AI - Database Index Creation Script
-- Run this to add performance indexes to existing tables
-- Expected impact: 70-95% faster queries on indexed columns

USE docmind_ai;

-- ============================================
-- MESSAGE TABLE INDEXES
-- ============================================

-- Index for fetching messages by conversation (most common query)
CREATE INDEX idx_message_conversation 
ON messages(conversation_id);

-- Index for time-based message queries
CREATE INDEX idx_message_created 
ON messages(created_at);

-- Composite index for fetching conversation messages ordered by time
-- This is the most common query pattern: SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at
CREATE INDEX idx_conversation_created 
ON messages(conversation_id, created_at);

-- ============================================
-- CONVERSATION TABLE INDEXES
-- ============================================

-- Index for user lookup (fetch all conversations for a user)
CREATE INDEX idx_conversation_user 
ON conversations(user_id);

-- Index for time-based conversation queries
CREATE INDEX idx_conversation_created 
ON conversations(created_at);

-- Composite index for fetching user conversations ordered by time
-- Common query: SELECT * FROM conversations WHERE user_id = ? ORDER BY created_at DESC
CREATE INDEX idx_user_created 
ON conversations(user_id, created_at);

-- ============================================
-- DOCUMENT TABLE INDEXES
-- ============================================
-- Note: Document table already has indexes on 'id' and 'user_id'

-- Index for extraction status queries (batch processing)
CREATE INDEX idx_document_extraction_status 
ON documents(extraction_status);

-- Composite index for user document queries
CREATE INDEX idx_document_user_status 
ON documents(user_id, extraction_status);

-- ============================================
-- CONVERSATION SUMMARY TABLE INDEXES
-- ============================================
-- Note: conversation_id already has unique index

-- ============================================
-- EXTRACTED DATA TABLE INDEXES
-- ============================================

-- Index for document lookup (if table exists)
-- CREATE INDEX idx_extracted_chunks_doc ON extracted_chunks(doc_id);

-- Index for user lookup (if table exists)
-- CREATE INDEX idx_extracted_chunks_user ON extracted_chunks(user_id);

-- Composite index for user + document queries (if table exists)
-- CREATE INDEX idx_extracted_chunks_user_doc ON extracted_chunks(user_id, doc_id);
