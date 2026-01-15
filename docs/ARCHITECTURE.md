# TaxMate System Architecture

## 1. High-Level Design (HLD)

The TaxMate system follows a modern, decoupled architecture separating the User Interface (Next.js) from the business logic and AI orchestration (FastAPI + LangGraph). This allows for independent scaling and maintenance of the frontend and backend components.

### 1.1 System Diagram

```mermaid
graph TD
    Client["User Client"]
    
    subgraph Frontend["Frontend Layer (Next.js)"]
        UI["UI Components (Radix/Tailwind)"]
        Pages["Page Logic & State"]
        API_Client["API Integration Layer"]
    end
    
    subgraph Backend["Backend Layer (FastAPI)"]
        API_GW["API Gateway (Router)"]
        Orchestrator["Tax Orchestrator (LangGraph)"]
        
        subgraph Services["Core Services"]
            FormExt["Form Extraction (LlamaCloud)"]
            TaxComp["Tax Computation Engine"]
            Advisor["AI Advisor (RAG Agent)"]
            GenSvc["Form Generation Service"]
        end
    end
    
    subgraph Data["Data Layer"]
        MongoDB[("MongoDB (User & Tax Data)")]
        VectorDB[("ChromaDB/Qdrant (Embeddings)")]
        ObjectStore[("File System (PDFs/JSONs)")]
    end

    Client <--> Frontend
    Frontend -- REST/WebSockets --> API_GW
    
    API_GW <--> Orchestrator
    Orchestrator --> FormExt
    Orchestrator --> TaxComp
    Orchestrator --> Advisor
    Orchestrator --> GenSvc
    
    FormExt --> ObjectStore
    FormExt --> MongoDB
    
    TaxComp --> MongoDB
    
    Advisor <--> VectorDB
    Advisor --> MongoDB
```

## 2. Core Components

### 2.1 Frontend (User Interface)
*   **Tech Stack**: Next.js 13+, React, Typescript, Tailwind CSS.
*   **Responsibility**: provides the interactive dashboard for file uploads, chat interface, and result visualization.
*   **Communication**: detailed in [Frontend Architecture](FRONTEND_ARCHITECTURE.md).

### 2.2 Backend (Orchestration & Logic)
*   **Tech Stack**: Python 3.10+, FastAPI, LangGraph, LangChain.
*   **Responsibility**: Acts as the brain of the system. It exposes REST endpoints and manages the long-running workflows for tax filing.
*   **Orchestrator**: A state-machine based workflow engine that coordinates data flow between extraction, computation, and advisory. Detailed in [Orchestrator Architecture](ORCHESTRATOR_ARCHITECTURE.md).

### 2.3 Data Services
*   **MongoDB**: Primary transactional database. Stores User profiles, extracted form data (Form 16/AIS), and ITR filing status.
*   **Vector DB**: Stores semantic embeddings of the Income Tax Act and user documents to support the RAG (Retrieval Augmented Generation) based Tax Advisor.

### 2.4 End-to-End Sequence Diagram

The following diagram illustrates the interaction between components during a typical tax analysis request.

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant API as API Gateway
    participant ORCH as Orchestrator
    participant EXT as Extraction Svc
    participant CALC as Computation Svc
    participant ADV as Advisor Agent
    participant DB as MongoDB

    U->>FE: Uploads Form 16 PDF
    FE->>API: POST /api/upload
    API->>EXT: Process File (LlamaExtract)
    EXT-->>DB: Save Extracted JSON
    EXT-->>API: Success (File ID)
    API-->>FE: File Uploaded

    U->>FE: Clicks "Analyze Tax"
    FE->>API: GET /api/analyze
    API->>ORCH: Start Mission
    
    rect rgb(240, 240, 255)
        note right of ORCH: LangGraph Workflow
        ORCH->>DB: Fetch User Context
        ORCH->>CALC: Compare Regimes(Old vs New)
        CALC-->>ORCH: Computation Result
        
        ORCH->>ADV: Generate Tax Advice
        ADV->>DB: Fetch Tax Laws (Vector)
        ADV-->>ORCH: Strategic Advice
        
        ORCH-->>DB: Save State
    end
    
    ORCH-->>API: Final Mission Result
    API-->>FE: JSON (Tax Liability, Savings, Advice)
    FE-->>U: Displays Dashboard
```

## 3. Key Workflows

### 3.1 The Filing Workflow (The "Mission")
1.  **Ingestion**: User uploads PDF documents.
2.  **Extraction**: System converts PDFs to structured JSON (Form 16/AIS schemas).
3.  **Computation**: Engine calculates tax under Old vs. New regime.
4.  **Advisory**: AI analyzes the financial situation to suggest tax saving opportunities.
5.  **Generation**: System produces the final ITR JSON for filing.

### 3.2 The Advisory Workflow
1.  User asks a question (e.g., "How can I save more tax?").
2.  **Retrieval**: System fetches relevant user financial data (Context) and Tax Law sections (Knowledge).
3.  **Reasoning**: LLM Agent plans a response, potentially searching the web for latest updates.
4.  **Response**: AI delivers a personalized, cited answer.

## 4. Design Principles
*   **Modularity**: Each service (Extraction, Computation) is independent and testable.
*   **Statelessness**: The API layer is stateless; state is managed by the Database and the Orchestrator's checkpointing mechanism.
*   **Security**: PII (Personally Identifiable Information) is handled with strict access controls. See [Security Documentation](SECURITY.md).
