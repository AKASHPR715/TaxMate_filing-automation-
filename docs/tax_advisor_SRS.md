# Software Requirements Specification (SRS) for `tax_advisor.py`

**Version:** 1.0  
**Date:** 2025-12-22  
**Status:** Draft  

---

## 1. Introduction

### 1.1 Purpose
The purpose of this document is to specify the detailed software requirements for the `tax_advisor.py` module within the TaxMate filing automation system. This module serves as an intelligent AI agent capable of providing personalized tax advice, analyzing investment opportunities, and optimizing tax liability based on the Indian Income Tax Act.

### 1.2 Scope
The `tax_advisor.py` module is a backend service component that:
- Integrates with Large Language Models (LLMs) via OpenRouter.
- Utilizes the LangChain framework for agentic behavior (Reasoning + Acting).
- Provides specific tools for Retrieving Augmented Generation (RAG) from local tax documents and performing real-time web searches.
- Interfaces with the `TaxOrchestrator` to deliver context-aware recommendations based on user financial data.

### 1.3 Definitions, Acronyms, and Abbreviations
- **SRS**: Software Requirements Specification
- **LLM**: Large Language Model
- **RAG**: Retrieval-Augmented Generation
- **AIS**: Annual Information Statement
- **FY**: Financial Year
- **AY**: Assessment Year
- **LangChain**: A framework for developing applications powered by language models.

---

## 2. Overall Description

### 2.1 Product Perspective
`tax_advisor.py` is a core service in the `src/services/` layer of the TaxMate application. It acts as a specialized worker agent invoked by the central `TaxOrchestrator`. It relies on:
- **Environment**: Python 3.x, Linux OS.
- **External APIs**: OpenRouter (for LLM inference), Tavily (for web search).
- **Internal Modules**: `models.hybridsearch` (for RAG), `models.graphdb` (optional graph queries).

### 2.2 Product Functions
The module provides the following primary functions:
1.  **Context-Aware Advisory**: Generates answers to tax-related queries using specific user context (Generic advice vs. Personalized advice).
2.  **Regulatory Compliance**: Fetches accurate legal context from the Indian Income Tax Act via vector search.
3.  **Real-Time Updates**: Performs web searches for the latest budget notifications or tax rule changes.
4.  **Logging**: Maintains a detailed audit log of advisory sessions.

### 2.3 User Classes and Characteristics
- **Primary User (System)**: The `TaxOrchestrator` calls this module programmatically to generate the "Strategic Advisory" section of the final report.
- **Secondary User (End User)**: Users interacting via the Chat Interface (indirectly, if routed through `main.py`'s chat endpoints that utilize this service).

### 2.4 Assumptions and Dependencies
- **API Keys**: Valid `OPENROUTER_API_KEY` and `TAVILY_API_KEY` must be present in the environment variables.
- **Network**: Active internet connection is required to reach OpenRouter and Tavily APIs.
- **Local Models**: The `retriever` from `models.hybridsearch` must be initialized and capable of querying the local vector store.

---

## 3. System Features & Functional Requirements

### 3.1 AI Agent Initialization
**Description**: The system must initialize a LangChain ReAct (Reason+Act) agent with access to specific tools.
- **FR-01**: The module shall load environment variables using `dotenv`.
- **FR-02**: The module shall configure the `ChatOpenAI` model using `tngtech/deepseek-r1t-chimera:free` (or configured model) via `openrouter.ai`.
- **FR-03**: The module shall pull the `hwchase17/react` prompt template from LangChain Hub.
- **FR-04**: The agent executor must be configured with `max_iterations=20` to prevent infinite loops.

### 3.2 Tool Integration
**Description**: The agent must have access to specific tools to ground its answers in reality.

#### 3.2.1 Tool: `retrieve_context`
- **Input**: `query` (string) - A specific question about tax sections (e.g., "Section 80C limit").
- **Functionality**: Invokes `retriever.invoke(query)` to fetch relevant documents from the local vector store.
- **Output**: Returns page content of matched documents or a concatenated string of multiple results.
- **Error Handling**: Catches exceptions and returns a failure message string.

#### 3.2.2 Tool: `web_search`
- **Input**: `query` (string) - Search query for live data.
- **Functionality**: Uses `TavilyClient` to search the web with `search_depth="advanced"`.
- **Constraint**: Should only be used if `retrieve_context` yields insufficient information.
- **Output**: Returns a summary answer and top 3 source URLs.

#### 3.2.3 Tool: `query_tax_graph`
- **Input**: `query` (string).
- **Functionality**: Queries a Neo4j knowledge graph for structural tax relationships.
- **Fallback**: If `models.graphdb` import fails, a fallback tool returns "Graph database query is currently unavailable."

### 3.3 Advisory Generation (`get_tax_advice`)
**Description**: The main entry point for generating advice.
- **Signature**: `get_tax_advice(question: str, deductions: List[str] = None, income_details: Dict[str, Any] = None) -> str`
- **FR-05**: The function shall accept a natural language question.
- **FR-06**: The function shall optionally accept a list of current deductions and a dictionary of income details.
- **FR-07**: The function shall construct a `full_prompt` by appending formatted context strings to the user question.
    - Format: `Context: \nIncome Context: ... \nCurrent Deductions: ...`
- **FR-08**: The function shall invoke the `agent_executor` with the constructed prompt.
- **FR-09**: The function shall return the final string output from the agent.
- **FR-10**: If the agent is not initialized (e.g., missing keys), it shall return an error message to the caller.

### 3.4 Logging
**Description**: Comprehensive logging for debugging and audit.
- **FR-11**: Logs shall be written to `logs/tax_advisor.log`.
- **FR-12**: Log rotation shall be configured (Max 5MB, keep 2 backups).
- **FR-13**: System shall log:
    - Initialization warnings (missing keys).
    - Incoming queries (`INFO` level).
    - Tool invocation details (via Agent verbose mode).
    - Errors and Exceptions (`ERROR` level).

---

## 4. External Interface Requirements

### 4.1 Programmatic Interface
The module exports the following symbol for external use:

```python
def get_tax_advice(
    question: str, 
    deductions: List[str] = None, 
    income_details: Dict[str, Any] = None
) -> str
```

**Input Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `question` | `str` | Yes | The user's tax-related query. |
| `deductions` | `List[str]` | No | List of strings modifying current deductions (e.g., "Section 80C: ₹150,000"). |
| `income_details` | `Dict[str, Any]` | No | KPI-value pairs of income status (e.g., {"Gross Salary": 1500000}). |

**Return Value:**
- `str`: A comprehensive, natural language response containing the advice, citations, and actionable steps.

### 4.2 Application Programming Interfaces (APIs)
- **OpenRouter API**: Used for LLM inference. Endpoint `https://openrouter.ai/api/v1`.
- **Tavily API**: Used for web search.

---

## 5. Non-Functional Requirements

### 5.1 Reliability
- The system must feature graceful degradation. If the Graph DB is unavailable, the agent continues with Vector Search and Web Search.
- If Web Search is unavailable (missing key), the agent relies solely on internal knowledge and vector store.

### 5.2 Performance
- The `get_tax_advice` call runs synchronously but is designed to be executed in a separate thread/executor (as seen in `tax_orchestrator.py`) to avoid blocking the main application loop.
- Default timeout for internal processing is implicitly governed by the `max_iterations=20` limit of the agent to preventing indefinite hanging.

### 5.3 Security
- **API Keys**: Keys are loaded strictly from environment variables and never hardcoded.
- **Data Privacy**: User financial data passed in `income_details` is sent to the LLM provider (OpenRouter). Usage implies consent for this data transmission.

### 5.4 Maintainability
- The code uses modular tool definitions (`@tool` decorator). Adding a new tool (e.g., a Calculator) requires defining a function and adding it to the `tools` list.
- Logging is centralized via `setup_advisor_logger`.

---

## 6. Implementation Constraints
- **Model dependency**: The quality of advice is directly dependent on the performance of the `deepseek-r1t-chimera` model. Hallucinations are possible; the system mitigates this via RAG (`retrieve_context`).
- **Path Resolution**: The module assumes a specific directory structure (`../../logs`, `../models`) for relative imports and logging.

