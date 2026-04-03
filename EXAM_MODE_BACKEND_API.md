# Exam Mode Backend API Documentation

## Overview
Backend-only implementation of Exam Mode feature that generates customizable exam papers with questions and model answers based on document content.

**Status:** ✅ Backend Complete | ❌ Frontend Not Included

---

## Implementation Details

### Files Created/Modified

#### Python AI-Service
1. **`Ai-Service/app/services/exam_mode_service.py`** (NEW)
   - Core exam generation logic
   - Flexible parameter support
   - Uses Gemini 2.5 Flash AI

2. **`Ai-Service/app/services/document_tools_service.py`** (MODIFIED)
   - Added `exam_mode()` wrapper function

3. **`Ai-Service/app/main.py`** (MODIFIED)
   - Added `POST /documents/{doc_id}/exam` endpoint

#### Java Spring Boot Backend
1. **`Backend/.../DocumentService.java`** (MODIFIED)
   - Added `generateExam()` method

2. **`Backend/.../DocumentController.java`** (MODIFIED)
   - Added `POST /api/documents/{docId}/exam` endpoint

---

## API Endpoints

### 1. Direct AI-Service Endpoint

**URL:** `POST http://localhost:8000/documents/{doc_id}/exam`

**Parameters (Form Data):**
- `user_id` (required): User identifier
- `marks_1` (optional, default: 2): Number of 1-mark questions
- `marks_2` (optional, default: 5): Number of 2-mark questions
- `marks_5` (optional, default: 3): Number of 5-mark questions
- `marks_10` (optional, default: 0): Number of 10-mark questions

**Response:**
```json
{
  "exam_paper": "📝 EXAMINATION PAPER\n━━━━━━━━━━━━━━━━━━\nTotal Marks: 27\nTotal Questions: 10\n..."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/documents/123456/exam \
  -F "user_id=user123" \
  -F "marks_1=3" \
  -F "marks_2=7" \
  -F "marks_5=5" \
  -F "marks_10=1"
```

---

### 2. Spring Boot API Endpoint (with JWT Auth)

**URL:** `POST http://localhost:8080/api/documents/{docId}/exam`

**Parameters (Query String):**
- `marks_1` (optional, default: 2)
- `marks_2` (optional, default: 5)
- `marks_5` (optional, default: 3)
- `marks_10` (optional, default: 0)

**Headers:**
- `Authorization: Bearer {jwt_token}`

**Response:**
```json
{
  "exam_paper": "📝 EXAMINATION PAPER\n..."
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8080/api/documents/doc123/exam?marks_1=5&marks_2=7&marks_5=3" \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## Exam Question Types

### 1-Mark Questions
- **Purpose:** Quick recall, definitions, terminology
- **Answer Length:** 1-2 sentences
- **Examples:** "Define X", "What is Y?", "State Z"

### 2-Mark Questions
- **Purpose:** Brief explanations, comparisons
- **Answer Length:** 2-4 sentences
- **Examples:** "Explain briefly...", "Differentiate between..."

### 5-Mark Questions
- **Purpose:** Detailed analysis, explanations
- **Answer Length:** 5-8 sentences or structured points
- **Examples:** "Explain in detail...", "Discuss the significance..."

### 10-Mark Questions
- **Purpose:** Extensive evaluation, critical thinking
- **Answer Length:** Comprehensive multi-aspect answers
- **Examples:** "Critically evaluate...", "Compare and contrast extensively..."

---

## Default Configuration

```
Total Questions: 10
Total Marks: 27

Distribution:
- 2 questions × 1 mark = 2 marks
- 5 questions × 2 marks = 10 marks
- 3 questions × 5 marks = 15 marks
- 0 questions × 10 marks = 0 marks
```

---

## Usage Examples

### Example 1: Quick Quiz (10 questions, 10 marks)
```bash
curl -X POST http://localhost:8000/documents/doc123/exam \
  -F "user_id=user1" \
  -F "marks_1=10" \
  -F "marks_2=0" \
  -F "marks_5=0" \
  -F "marks_10=0"
```

### Example 2: Mid-term Exam (15 questions, 35 marks)
```bash
curl -X POST http://localhost:8000/documents/doc123/exam \
  -F "user_id=user1" \
  -F "marks_1=5" \
  -F "marks_2=7" \
  -F "marks_5=3" \
  -F "marks_10=0"
```

### Example 3: Final Exam (22 questions, 70 marks)
```bash
curl -X POST http://localhost:8000/documents/doc123/exam \
  -F "user_id=user1" \
  -F "marks_1=5" \
  -F "marks_2=10" \
  -F "marks_5=5" \
  -F "marks_10=2"
```

### Example 4: Using Spring Boot API
```bash
curl -X POST "http://localhost:8080/api/documents/doc123/exam?marks_1=3&marks_2=5&marks_5=2" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## Output Format

The exam paper includes:

1. **Header Section**
   - Total marks
   - Total questions
   - Question distribution breakdown

2. **Question Sections** (Organized by mark value)
   - Section A: 1-Mark Questions
   - Section B: 2-Mark Questions
   - Section C: 5-Mark Questions
   - Section D: 10-Mark Questions

3. **Model Answers Section**
   - Comprehensive answers for all questions
   - All key points needed for full marks
   - Examples and explanations where relevant

---

## Integration with Frontend

Since frontend is not included, you can integrate the API using:

### Option 1: Direct API Calls from React
```javascript
const generateExam = async (docId, config) => {
  const params = new URLSearchParams({
    marks_1: config.marks1,
    marks_2: config.marks2,
    marks_5: config.marks5,
    marks_10: config.marks10
  });
  
  const response = await fetch(
    `/api/documents/${docId}/exam?${params}`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const data = await response.json();
  return data.exam_paper;
};
```

### Option 2: Using Axios
```javascript
import axios from 'axios';

const generateExam = async (docId, marks1, marks2, marks5, marks10) => {
  const response = await axios.post(
    `/api/documents/${docId}/exam`,
    {},
    {
      params: { marks_1: marks1, marks_2: marks2, marks_5: marks5, marks_10: marks10 },
      headers: { Authorization: `Bearer ${token}` }
    }
  );
  return response.data.exam_paper;
};
```

---

## Testing

### Using Postman

1. **Set Request Type:** POST
2. **Set URL:** `http://localhost:8080/api/documents/{docId}/exam`
3. **Set Headers:**
   - `Authorization: Bearer {your_jwt_token}`
4. **Set Query Params:**
   - `marks_1`: 3
   - `marks_2`: 5
   - `marks_5`: 2
   - `marks_10`: 1
5. **Send Request**

### Using Browser Console

```javascript
fetch('/api/documents/doc123/exam?marks_1=5&marks_2=5&marks_5=3', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(r => r.json())
.then(data => console.log(data.exam_paper));
```

---

## Error Handling

### Common Errors

1. **No document content found**
   ```json
   { "exam_paper": "No document content found." }
   ```

2. **No questions specified**
   ```json
   { "exam_paper": "Error: Please specify at least one question." }
   ```

3. **Gemini API error**
   ```json
   { "exam_paper": "Error generating exam paper: {error_message}" }
   ```

4. **Authentication error (401)**
   - User not authenticated
   - Invalid or expired JWT token

5. **Internal server error (500)**
   - AI Service connection issues
   - Database errors

---

## Notes

- ✅ Backend fully implemented and functional
- ❌ Frontend components not included
- ✅ Supports flexible customization
- ✅ JWT authentication enforced
- ✅ Default values provided for all parameters
- ⚠️ Requires active Gemini API key
- ⚠️ Subject to Gemini API rate limits

---

## Next Steps (Frontend Implementation)

If you want to add frontend later:

1. Create UI button/menu item for "Exam Mode"
2. Create modal for parameter selection
3. Call the API endpoint with selected parameters
4. Display the exam paper in the chat or dedicated view
5. Optional: Add print/export functionality

Example UI flow:
```
User clicks "Exam Mode" 
  → Modal opens with sliders/inputs for marks_1, marks_2, marks_5, marks_10
  → User configures exam
  → Clicks "Generate"
  → API call with parameters
  → Display formatted exam paper
```

---

**Created:** April 3, 2026  
**Version:** 1.0  
**Status:** Backend Complete - Ready for Frontend Integration
