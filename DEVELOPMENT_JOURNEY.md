# Developer Journey

This project was developed step by step, starting from a basic Python setup and gradually evolving into a complete product monitoring and AI-assisted analysis system.

---

## 1. Initial Setup

The development started by setting up:

* Python
* VS Code
* Python virtual environment
* Required Python packages

The project was developed in VS Code with coding assistance from GPT.

---

## 2. Building the Monitoring System

The first major objective was to build a system that could monitor product updates from:

* Notion
* Figma
* Canva

Python was used with **Requests** and **BeautifulSoup** to access and extract information from the official product release pages.

The first working version focused on detecting the latest release and displaying the result.

---

## 3. Adding Persistent Product Memory

The next challenge was preventing the system from treating the same release as a new change every time it ran.

Three memory files were introduced:

```text
notion_last_seen.txt
figma_last_seen.txt
canva_last_seen.txt
```

The system could now compare the current release date with the previously stored date.

This introduced **persistent memory and change detection** into the project.

---

## 4. Building Historical Change Storage

After detecting changes, the next step was to preserve them for future use.

A historical database using:

```text
change_history.json
```

was introduced.

Each detected change could now be stored with information such as:

* Product
* Release title
* Date
* Source
* Description
* Detection time

Duplicate prevention was also added so that the same release would not repeatedly enter the history.

---

## 5. Adding Error Handling

Error handling was added to make the monitoring process more reliable.

The system was designed to handle situations such as:

* Website request failures
* Network problems
* Missing information
* Unexpected webpage structures
* Parsing errors

The existing product memory is protected from being unnecessarily overwritten when valid information cannot be retrieved.

---

## 6. Adding Automatic Daily Monitoring

Once the monitoring system was working manually, automation was added using **Windows Task Scheduler**.

A batch file was created:

```text
run_monitor.bat
```

The scheduled workflow became:

```text
Windows Task Scheduler
        ↓
9:00 AM every day
        ↓
run_monitor.bat
        ↓
python main.py
        ↓
Monitor Notion, Figma and Canva
```

This changed the project from a manually operated script into an automatically running monitoring system.

---

## 7. Adding Local AI

The next stage was adding an AI layer.

Instead of depending on a paid external AI API, **Ollama** was integrated to run AI locally.

The final model used was:

```text
Qwen3 1.7B
```

This allowed the project to answer natural-language questions about the recorded product changes.

---

## 8. Adding RAG

The AI system was then extended into a simple **Retrieval-Augmented Generation (RAG)** workflow.

The agent:

```text
User Question
      ↓
agent.py
      ↓
Retrieve relevant records
      ↓
change_history.json
      ↓
Ollama / Qwen3 1.7B
      ↓
Natural-language answer
```

This allowed questions such as:

```text
What changed in Figma?
```

```text
What changed in Notion?
```

```text
Show me all product changes.
```

The AI therefore uses the project's stored monitoring history as its information source.

---

## 9. Adding Fictional Company Context

The project was then extended beyond simple product monitoring.

A structured fictional company dataset was added through:

```text
fictional_company_context.json
```

The context includes:

* Company overview
* Target customers
* Product features
* Pricing plans
* Customer feedback
* Pain points
* Product differentiators

This created a second information source separate from the monitored product history.

---

## 10. Adding Company-Impact Analysis

The next stage was connecting monitored product changes with the fictional company context.

The purpose was to understand a monitored product change in relation to the fictional company's existing:

* Product features
* Pricing
* Customers
* Feedback
* Pain points
* Differentiators

An important design principle was established:

```text
External Product Information
          ≠
Fictional Company Information
```

The monitored product's feature should not be incorrectly treated as an existing feature of the fictional company.

---

## 11. Testing and Validation

The project was tested progressively by:

1. Running the monitoring system
2. Checking all three products
3. Verifying stored release dates
4. Simulating a new release
5. Detecting the change
6. Saving the change to history
7. Querying the change through the AI agent
8. Verifying retrieval
9. Restoring the normal memory state
10. Running the monitoring system again
11. Confirming that matching release dates produce no duplicate changes

This helped validate both the monitoring and AI workflows.

---

## 12. Git and GitHub

After the core system was developed and tested, Git was introduced for version control.

The project was pushed to GitHub:

```text
https://github.com/akg5643-ux/product-monitoring-agent
```

The repository now provides a central place for the project's source code and documentation.

---

## 13. Final Development Outcome

The project evolved from a basic Python monitoring script into a complete system combining:

```text
Python
   +
Web Scraping
   +
Change Detection
   +
Persistent Memory
   +
Historical Storage
   +
RAG
   +
Local AI
   +
Fictional Company Context
   +
Company-Impact Analysis
   +
Scheduled Automation
   +
Git / GitHub
```

The development journey focused on building each capability step by step, testing it, and then extending the system with the next required layer.
