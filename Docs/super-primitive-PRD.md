# Product Requirement Document: Personal Expense Tracker

## 1. Overview
A private, AI-augmented expense management system designed for granular control over personal finance data. The system prioritizes local data ownership while offering optional AI-driven insights for categorization and trend analysis.

## 2. Architecture & Components

### A. Data Processing Engine
* **Ingestion:** Supports structured statement uploads (e.g., CSV/Excel).
* **Categorization:** * **Manual:** User-defined rules and identifier mapping.
    * **AI-Augmented:** Cloud-based processing for intelligent transaction classification (requires explicit user consent for data sharing).
* **Action Logic:** Detects anomalies (e.g., unrecognized vendors or uncategorized spending).

### B. Visualization & Intelligence
* **Dashboarding:** Interactive tables and charts with multi-dimensional filtering (date, source, amount, category, description keywords).
* **Agentic Analysis:** An LLM-powered chat interface capable of querying historical data to provide personalized savings recommendations and spending insights.

---

## 3. User Flow

1.  **Authentication:** Secure login/access control.
2.  **Onboarding:** Define spending sources (Savings, Credit Cards, Benefits/Pluxee) and establish initial category identifiers.
3.  **Statement Ingestion:** User uploads a financial statement.
4.  **Classification:**
    * System performs auto-mapping via existing rules.
    * Unmapped items are flagged for user review or AI-assisted labeling.
5.  **Insight Generation:** Data is processed into the dashboard. User interacts with the agent for deep-dive analysis.

---

## 4. Screen Specifications

| Screen | Key Elements |
| :--- | :--- |
| **Login** | Secure entry point. |
| **Homescreen** | **Filters:** Date range, Source, Sort (Amt), Category, Search (Description). **Display:** Chart/Table view. **Actions:** Upload trigger, AI Chat interface, Action Item/Alert feed. |
| **Profile/Config** | **Source Management:** Add/Edit/Delete accounts. **Category Management:** CRUD operations for categories and associated regex/text identifiers. |

---

## 5. Technical Constraints & Data Privacy
* **Privacy First:** All data processing is local by default. AI features for categorization and querying are **opt-in** and explicitly labeled: *"Warning: Data will be shared."*
* **System Extensibility:** The category management system must allow users to map specific transaction descriptions (e.g., "AMZN MKT") to custom categories (e.g., "Shopping") via a CRUD interface.

---

## 6. AI Development Roadmap (Prompt Instructions)
*When working on this project, treat the following as the primary context:*
* **Component 1 (Data):** Prioritize regex-based mapping for local performance.
* **Component 2 (Analysis):** The agent must reference the `Category Management` rules first before suggesting new classifications.
* **Formatting:** When generating code, always prioritize maintainability and modularity as defined in the "Components" section.
