This setup will transform your Claude Sonnet 4.5 instance into a persistent development agent. By maintaining a structured JSON "State File," you minimize token overhead by only loading the relevant context for the current task.

### 1. The Initial Setup Prompt
Copy and paste this to initialize the workspace. 

***

**Prompt:**
I am building a personal expense tracker. Attached is the PRD. Act as a Lead Backend Engineer and perform the following initialization:

1. **Task Breakdown:** Analyze the PRD and create a `project_state.json` file. This file must contain all features and subtasks, with fields for `status` (pending/in-progress/completed) and `priority`.
2. **Developer README:** Create a `README_DEV.md` for me. Include architecture design, setup steps, environment assumptions, and known limitations based on the PRD.
3. **Standards & Conventions:** Establish a "Project Rulebook." Define naming conventions, directory structure, error handling patterns, and coding standards. Adopt a modular design so you (the AI) can easily navigate the codebase in future sessions.
4. **Memory Management Strategy:** Propose a method for maintaining "long-term memory" (e.g., summary files for completed modules) to ensure we stay within context windows and reduce token consumption.
5. **Testing Protocol:** Implement a "Test-First" workflow. Before marking any task as `completed` in `project_state.json`, you must write and execute unit tests (including edge cases) and confirm they pass.

Please output the `project_state.json` first.

***

### 2. The "Golden" Work Prompt
Use this prompt every time you start a new coding session. It ensures the model pulls only what it needs, keeps the `project_state.json` updated, and maintains consistency.

***

**Prompt:**
We are continuing work on the Expense Tracker. 

**Context & State:**
* **`project_state.json`:** (Attach current file content here)
* **`README_DEV.md`:** (Attach current file content here)
* **Active Task:** [Insert the specific feature/subtask you are working on today]

**Constraints & Workflow:**
1. **Load Context:** Review the project state to understand what is completed. Do not re-implement existing logic.
2. **Adhere to Standards:** Follow the rules and coding structure defined in our `README_DEV.md`. 
3. **Implementation:** Write the implementation for the active task. Include unit tests that cover standard and edge cases.
4. **Validation:** Execute the tests before presenting the solution.
5. **Update State:** Once the task is verified, update the `project_state.json` (mark the task as "completed") and summarize the technical changes in a brief note. 

Let's begin with: [Insert Task Name]

***

### Pro-Tips for your Workflow:

* **Memory Injection:** When you copy-paste the `project_state.json` in the "Golden Prompt," you are essentially "bootstrapping" the model's brain. If the project gets huge (e.g., 50+ files), ask the model to create a `summary.md` of the core logic and include that instead of the entire file list to save tokens.
* **The "Rulebook" Rule:** If you decide to change a coding standard (e.g., switching from `if err != nil` patterns in Go to a different error handler), ensure you update `README_DEV.md` immediately so the model stays aligned.
* **Edge Case Focus:** Since this handles financial data, explicitly tell the model in your "Golden Prompt": *"Prioritize precision for currency calculations (use fixed-point arithmetic, not floats) and ensure data integrity for uploads."*