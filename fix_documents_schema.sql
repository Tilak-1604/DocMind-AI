-- ──────────────────────────────────────────────
-- DocMind AI: Final Database Schema Alignment
-- Corrects the 'Field id doesn't have a default value' error
-- ──────────────────────────────────────────────

-- 1. Ensure the id column is BIGINT and correctly set to AUTO_INCREMENT
ALTER TABLE documents 
MODIFY COLUMN id BIGINT AUTO_INCREMENT PRIMARY KEY;

-- 2. Ensure doc_id is NOT NULL and UNIQUE (this is our primary business lookup ID)
ALTER TABLE documents 
MODIFY COLUMN doc_id VARCHAR(255) NOT NULL UNIQUE;

-- 3. Add chunk_count if missing (required for extraction metrics)
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS chunk_count INT DEFAULT 0;

-- 4. Add extraction_status and other AI service metadata if missing
ALTER TABLE documents 
ADD COLUMN IF NOT EXISTS extraction_status VARCHAR(50) DEFAULT 'PENDING',
ADD COLUMN IF NOT EXISTS global_summary TEXT,
ADD COLUMN IF NOT EXISTS mind_map_plantuml TEXT;

-- 5. Final check of the structure
DESCRIBE documents;
