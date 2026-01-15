# Future Scope & Roadmap 🚀

TaxMate is built to be extensible. While the current version handles the core ITR-1 workflow, there are immense opportunities for expansion.

## 1. Expanded Functional Capabilities

### 1.1 Support for Complex Returns (ITR-2, ITR-3)
*   **Capital Gains**: detailed parsing of Capital Gains statements (CAMS/Karvy reports) for stock/mutual fund traders.
*   **Business Income**: Module to handle Section 44AD (Presumptive Taxation) for freelancers and small business owners.
*   **Foreign Assets**: Reporting of foreign stocks (RSU/ESOP) for tech employees.

### 1.2 Automated Filing Submission
*   Currently, we generate the JSON for upload.
*   **Future**: Direct integration with the **Income Tax Department API** (E-Filing 2.0) to submit the return directly from the dashboard using OTP authentication.

## 2. Advanced AI Features

### 2.1 Proactive Tax Planning "Playbooks"
*   Instead of just answering "How to save tax?", the AI will proactively monitor the user's portfolio throughout the year.
*   *Example*: "It's February. You have ₹40k left in your 80C limit. Invest in ELSS before March 31st to save ₹12k."

### 2.2 Voice-Enabled Advisory
*   Add a Voice-to-Text layer (OpenAI Whisper) to the mobile app, allowing users to talk to their Tax Advisor naturally.

### 2.3 Local LLM Inference
*   To enhance privacy, move from Cloud LLMs (OpenAI) to **Local LLMs** (e.g., Llama-3-8B quantified) running directly on the user's device or an on-premise server.

## 3. Technical Enhancements

### 3.1 Multi-Tenancy & CA Portal
*   Build a "CA Dashboard" where Chartered Accountants can manage filings for typically 50-100 clients, utilizing the AI to do the heavy lifting of data entry.

### 3.2 Blockchain for Document Integrity
*   Use a private ledger to create a tamper-proof audit trail of all extracted financial documents and filing versions.

### 3.3 Mobile Application
*   Develop a React Native / Flutter app for simpler document uploading (scan via camera) and quick status checks.
