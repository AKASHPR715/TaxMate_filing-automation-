# Backend Integration Guide for TaxMate

This guide explains how to connect your Python/FastAPI backend to the TaxMate Next.js frontend.

## Overview

The frontend uses a combination of:
- **Supabase** for database storage and real-time updates
- **REST API calls** to your FastAPI backend for AI processing
- **Supabase Storage** for document storage

## Architecture

```
Frontend (Next.js) → Supabase Database (metadata)
                  → Supabase Storage (documents)
                  → FastAPI Backend (AI processing)
```

## Database Schema

Three main tables have been created in Supabase:

### 1. `documents` table
Stores uploaded documents and their processing status.

### 2. `tax_computations` table
Stores tax calculation results for each user.

### 3. `chat_history` table
Stores AI chat conversation history.

## Backend API Endpoints Required

Your FastAPI backend should implement these endpoints:

### 1. Document Processing
**POST** `/api/process-document`

Receives document information and performs AI extraction.

**Request Body:**
```json
{
  "document_id": "uuid",
  "file_url": "https://supabase-storage-url/file.pdf"
}
```

**Response:**
```json
{
  "extracted_data": {
    "document_type": "Form16",
    "income": 1200000,
    "employer": "Company Name",
    "pan": "ABCDE1234F",
    "fields": {...}
  }
}
```

**What to implement:**
- Download file from `file_url`
- Use Llama2/OCR to extract information
- Parse and structure the data
- Return extracted fields

### 2. Tax Computation
**POST** `/api/compute-tax`

Calculates tax based on user documents.

**Request Body:**
```json
{
  "user_id": "user123",
  "assessment_year": "2024-25"
}
```

**Response:**
```json
{
  "total_income": 1250000,
  "total_deductions": 390000,
  "taxable_income": 860000,
  "tax_liability": 45000,
  "computation_data": {
    "income_breakdown": {...},
    "deduction_breakdown": {...},
    "tax_slabs": {...}
  }
}
```

**What to implement:**
- Fetch all documents for user from Supabase
- Aggregate income from all sources
- Calculate eligible deductions
- Apply Indian tax slabs
- Return detailed breakdown

### 3. AI Chat Assistant
**POST** `/api/chat`

Handles chat queries using RAG and LLM.

**Request Body:**
```json
{
  "user_id": "user123",
  "session_id": "session456",
  "message": "Can I claim HRA deduction?"
}
```

**Response:**
```json
{
  "response": "Yes, you can claim HRA deduction if you are paying rent...",
  "context": {
    "relevant_documents": ["doc1", "doc2"],
    "suggestions": ["Upload rent receipts"]
  }
}
```

**What to implement:**
- Use FAISS to find relevant context
- Query Llama2/Cohere with user's question + context
- Return natural language response
- Track conversation history

### 4. Deduction Finder
**POST** `/api/find-deductions`

Analyzes documents to find all eligible deductions.

**Request Body:**
```json
{
  "user_id": "user123"
}
```

**Response:**
```json
{
  "deductions": [
    {
      "section": "80C",
      "type": "PPF",
      "amount": 150000,
      "source_document": "doc_id"
    },
    {
      "section": "80D",
      "type": "Health Insurance",
      "amount": 25000,
      "source_document": "doc_id"
    }
  ],
  "potential_savings": 52500,
  "suggestions": [
    "You can claim additional 50000 under 80C"
  ]
}
```

### 5. Return Validation
**POST** `/api/validate-return`

Validates the tax return before filing.

**Request Body:**
```json
{
  "user_id": "user123",
  "assessment_year": "2024-25"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [
    "Consider claiming 80C deductions"
  ],
  "missing_documents": []
}
```

## Environment Variables

Add to your `.env` file:

```bash
# Supabase (already configured)
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# Your FastAPI Backend URL
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
# or for production:
# NEXT_PUBLIC_BACKEND_URL=https://your-backend.com
```

## Using the API in Frontend

The `TaxMateAPI` class (`lib/api.ts`) provides methods to interact with your backend:

```typescript
import { taxMateAPI } from '@/lib/api';

// Upload and process document
const result = await taxMateAPI.uploadDocument({
  userId: 'user123',
  file: selectedFile
});

// Get tax computation
const computation = await taxMateAPI.computeTax('user123', '2024-25');

// Chat with AI
const response = await taxMateAPI.chatWithAI(
  'user123',
  'session456',
  'How much tax do I owe?'
);

// Find deductions
const deductions = await taxMateAPI.findDeductions('user123');

// Validate return
const validation = await taxMateAPI.validateReturn('user123', '2024-25');
```

## FastAPI Backend Example Structure

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

class ProcessDocumentRequest(BaseModel):
    document_id: str
    file_url: str

class ComputeTaxRequest(BaseModel):
    user_id: str
    assessment_year: str

@app.post("/api/process-document")
async def process_document(request: ProcessDocumentRequest):
    # 1. Download file from file_url
    # 2. Use your AI agents (Llama2, OCR) to extract data
    # 3. Parse and structure the information
    # 4. Return extracted_data

    extracted_data = {
        "document_type": "Form16",
        "income": 1200000,
        # ... more fields
    }

    return {"extracted_data": extracted_data}

@app.post("/api/compute-tax")
async def compute_tax(request: ComputeTaxRequest):
    # 1. Fetch user documents from Supabase
    # 2. Aggregate all income sources
    # 3. Calculate deductions
    # 4. Apply tax slabs
    # 5. Return computation

    return {
        "total_income": 1250000,
        "total_deductions": 390000,
        "taxable_income": 860000,
        "tax_liability": 45000,
        "computation_data": {}
    }

@app.post("/api/chat")
async def chat(request: dict):
    # 1. Get user context from Supabase
    # 2. Use FAISS to find relevant documents
    # 3. Query LLM with context
    # 4. Return response

    return {
        "response": "AI generated response",
        "context": {}
    }

# Add other endpoints...
```

## Supabase Storage Setup

Create a storage bucket for documents:

1. Go to Supabase Dashboard → Storage
2. Create new bucket: `tax-documents`
3. Set bucket to **public** or configure RLS policies
4. The frontend will upload files directly to this bucket

## CORS Configuration

Your FastAPI backend needs CORS enabled:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing the Integration

1. **Start your FastAPI backend:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **Set environment variable:**
   ```bash
   echo "NEXT_PUBLIC_BACKEND_URL=http://localhost:8000" >> .env.local
   ```

3. **Start Next.js frontend:**
   ```bash
   npm run dev
   ```

4. **Test document upload:**
   - Go to `/dashboard`
   - Upload a test PDF
   - Check your FastAPI logs for the processing request
   - Verify the extracted data in Supabase

## Multi-Agent System Integration

For your multi-agent architecture:

```python
# In your FastAPI backend

class AgentOrchestrator:
    def __init__(self):
        self.document_agent = DocumentProcessingAgent()
        self.computation_agent = TaxComputationAgent()
        self.deduction_agent = DeductionFinderAgent()
        self.validation_agent = ValidationAgent()
        self.chat_agent = ChatAgent()

    async def process_document(self, file_url: str):
        # Use document agent to extract information
        result = await self.document_agent.extract(file_url)
        return result

    async def compute_tax(self, user_id: str, year: str):
        # Orchestrate multiple agents
        documents = await self.get_user_documents(user_id)
        income = await self.computation_agent.calculate_income(documents)
        deductions = await self.deduction_agent.find_deductions(documents)
        tax = await self.computation_agent.calculate_tax(income, deductions)
        return tax

orchestrator = AgentOrchestrator()

@app.post("/api/process-document")
async def process_document(request: ProcessDocumentRequest):
    result = await orchestrator.process_document(request.file_url)
    return result
```

## Real-time Updates (Optional)

For real-time status updates, use Supabase Realtime:

```typescript
// In your frontend
import { supabase } from '@/lib/supabase';

// Subscribe to document changes
const subscription = supabase
  .channel('document-updates')
  .on('postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'documents',
      filter: `user_id=eq.${userId}`
    },
    (payload) => {
      console.log('Document updated:', payload.new);
      // Update UI with new status
    }
  )
  .subscribe();
```

## Next Steps

1. ✅ Database schema created
2. ✅ API service layer ready
3. ⏳ Implement FastAPI endpoints
4. ⏳ Connect AI agents to endpoints
5. ⏳ Test end-to-end flow
6. ⏳ Deploy backend and frontend

## Need Help?

Check the example implementations in `lib/api.ts` for the expected request/response formats.
