# TaxMate - Intelligent Tax Filing Automation 🤖📄

TaxMate is an AI-powered tax filing automation platform designed to simplify the Indian Income Tax Return (ITR) process. It leverages advanced document extraction, tax regime comparison logic, and an AI-driven advisory system to help users file their taxes accurately and efficiently.

## 🚀 Key Features

*   **Intelligent Document Extraction**: Automatically parses Form 16 (Part A & B), AIS (Annual Information Statement), and Form 26AS using LlamaExtract to extract financial data.
*   **Smart Regime Comparison**: Instantly compares tax liabilities under the Old and New Tax Regimes (FY 2025-26) to recommend the most beneficial option.
*   **AI Tax Advisor**: A context-aware chatbot ("Tax Advisor") that answers tax-related queries based on your uploaded documents and Indian Tax Laws.
*   **Automated Form Generation**: Generates ITR JSON files ready for submission based on computed data.
*   **Modern Dashboard**: A responsive Next.js frontend for managing documents, viewing analytics, and interacting with the system.

## 📚 Documentation

Detailed documentation for the project is available in the `docs/` directory:

*   **[Architecture Overview](docs/ARCHITECTURE.md)**: High-level system design and component interaction.
*   **[Frontend Architecture](docs/FRONTEND_ARCHITECTURE.md)**: Next.js structure, UI components, and state management.
*   **[Orchestrator Architecture](docs/ORCHESTRATOR_ARCHITECTURE.md)**: The "Brain" of the system managing the workflow state machine.
*   **[Form Extraction Pipeline](docs/FORM_EXTRACTION_ARCHITECTURE.md)**: How documents are processed and mapped to data models.
*   **[AI Advisor Architecture](docs/ADVISOR_ARCHITECTURE.md)**: Design of the RAG-based tax advisory agent.
*   **[Security & Privacy](docs/SECURITY.md)**: Data handling, authentication, and security measures.
*   **[Future Scope](docs/FUTURE_SCOPE.md)**: Planned features and roadmap.

## 🛠️ Tech Stack

*   **Frontend**: Next.js 13+, React, Tailwind CSS, Radix UI, Lucide Icons.
*   **Backend**: Python, FastAPI, LangGraph (Workflow Orchestration), LangChain.
*   **Database**: MongoDB (User Data, Form Data), ChromaDB/Qdrant (Vector Store).
*   **AI/ML**: LlamaCloud (Extraction), OpenAI/DeepSeek (LLMs), Tavily (Web Search).

## ⚡ Getting Started

### Prerequisites

*   Python 3.10+
*   Node.js 18+
*   MongoDB Instance
*   API Keys: LlamaCloud, OpenRouter/OpenAI, Tavily (optional).

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-org/taxmate.git
    cd taxmate
    ```

2.  **Backend Setup**:
    ```bash
    # Create virtual environment
    python -m venv venv
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    
    # Run server
    ./server.sh
    ```

3.  **Frontend Setup**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

4.  **Access**:
    *   Frontend: `http://localhost:3000`
    *   Backend API Docs: `http://localhost:8000/docs`

## 🤝 Contribution

Contributions are welcome! Please check the issues tab for open tasks.

## 📄 License

[MIT License](LICENSE)
