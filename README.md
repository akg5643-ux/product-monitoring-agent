# Product Change Monitoring Agent

A Python-based product monitoring agent that tracks release updates from **Notion, Figma, and Canva**, detects new product changes, stores them in a local history, and allows users to ask natural-language questions about recorded changes using a local AI model.

---

## Project Overview

The Product Change Monitoring Agent automatically checks product release pages and compares the latest release date with the previously stored release date.

If a new release is detected, the agent:

1. Detects the change
2. Displays the new release information
3. Saves the change to `change_history.json`
4. Updates the product's stored release date

The project also includes a local AI agent that can answer questions about previously recorded product changes.

---

## Products Monitored

The agent currently monitors:

- Notion
- Figma
- Canva

### Source Pages

- Notion Releases: https://www.notion.com/releases
- Figma Release Notes: https://www.figma.com/release-notes/
- Canva Newsroom: https://www.canva.com/newsroom/news/

---

## How the System Works

```text
                 Product Release Pages
                    /      |      \
                   /       |       \
              Notion     Figma     Canva
                 \         |         /
                  \        |        /
                   v       v       v
                 Python Monitoring
                       System
                          |
                          v
                 Compare Release Date
                          |
                 +--------+--------+
                 |                 |
             No Change          New Change
                 |                 |
                 v                 v
              Continue       Save Change
                                  |
                                  v
                         change_history.json
                                  |
                                  v
                              agent.py
                                  |
                                  v
                         Ollama Local AI
                                  |
                                  v
                         Natural Language
                              Answer
```

---

## Project Architecture

The project consists of two main workflows.

### Monitoring Workflow

```text
Product Release Pages
        ↓
main.py
        ↓
Extract release information
        ↓
Compare with stored memory
        ↓
Detect new change
        ↓
Save to change_history.json
        ↓
Update product memory
```

### AI Question-Answering Workflow

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

---

## Project Structure

```text
product-monitoring-agent/
│
├── .venv/
├── .vscode/
│
├── main.py
├── agent.py
│
├── change_history.json
│
├── notion_last_seen.txt
├── figma_last_seen.txt
├── canva_last_seen.txt
│
├── run_monitor.bat
└── README.md
```

### File Responsibilities

| File | Purpose |
|---|---|
| `main.py` | Main product monitoring system |
| `agent.py` | Natural-language RAG agent |
| `change_history.json` | Stores detected product changes |
| `notion_last_seen.txt` | Stores the last detected Notion release date |
| `figma_last_seen.txt` | Stores the last detected Figma release date |
| `canva_last_seen.txt` | Stores the last detected Canva release date |
| `run_monitor.bat` | Starts the monitoring system for scheduled execution |
| `README.md` | Project documentation |
| `.venv/` | Python virtual environment |
| `.vscode/` | VS Code configuration |

---

## Main Components

### `main.py`

`main.py` is the main monitoring program.

It is responsible for:

- Checking product release pages
- Extracting release information
- Comparing current and previous release dates
- Detecting new product changes
- Saving detected changes
- Updating product memory
- Preventing duplicate history records
- Handling monitoring errors

Run it manually with:

```powershell
python main.py
```

---

### `agent.py`

`agent.py` is the natural-language question-answering agent.

It uses the recorded product history to answer questions about previously detected changes.

Run it with:

```powershell
python agent.py
```

Example:

```text
You: What changed in Figma?
```

The agent retrieves the relevant Figma record and provides the information to the local AI model.

To exit the agent:

```text
exit
```

---

## Product Memory

The monitoring system uses three memory files:

```text
notion_last_seen.txt
figma_last_seen.txt
canva_last_seen.txt
```

Each file stores the latest release date that has already been processed.

For example:

```text
figma_last_seen.txt
```

may contain:

```text
Sep 25, 2026
```

When `main.py` runs, it compares the current release date with the stored date.

### No Change

```text
Current release date: Sep 25, 2026
Previous release date: Sep 25, 2026

✅ No new change.
```

### New Change

If the current release date is newer:

```text
Current release date: Sep 26, 2026
Previous release date: Sep 25, 2026

🚨 NEW PRODUCT CHANGE DETECTED!
```

The system then saves the new change and updates the memory file.

---

## Change History

All detected product changes are stored in:

```text
change_history.json
```

This file acts as the project's historical memory.

Each record can contain:

- Product
- Release title
- Release date
- Source URL
- Description
- Detection time

Example:

```json
[
  {
    "product": "Figma",
    "title": "Vertical wrap available in auto layout",
    "date": "Sep 25, 2026",
    "source": "https://www.figma.com/release-notes/",
    "description": "Vertical wrap is now available when auto layout is set to vertical flow.",
    "detected_at": "2026-09-26 15:30:00"
  }
]
```

---

## Duplicate Prevention

The monitoring system checks whether a detected release is already present in:

```text
change_history.json
```

If the same product release has already been recorded, it is not added again.

This prevents duplicate history records when the monitoring system runs repeatedly.

---

## Error Handling

The monitoring system includes error handling for situations such as:

- Website request failures
- Network problems
- Unexpected webpage structures
- Missing release information
- Parsing errors

If a monitoring request fails, the system avoids intentionally replacing valid stored memory with invalid information.

---

# Local AI

The project uses **Ollama** to run the AI model locally.

The model used by the project is:

```text
qwen3:1.7b
```

The AI runs locally rather than using a paid external AI API.

The agent uses recorded product changes as its knowledge source.

---

## Retrieval-Augmented Generation (RAG)

The AI agent uses a simple Retrieval-Augmented Generation approach.

Instead of allowing the AI to freely answer questions about product history, the agent first retrieves relevant records from:

```text
change_history.json
```

The process is:

```text
User Question
      ↓
Identify relevant product/change
      ↓
Search stored history
      ↓
Retrieve relevant records
      ↓
Provide records to local AI
      ↓
Generate answer
```

This helps keep the AI answers grounded in the product changes actually recorded by the monitoring system.

---

## Example AI Questions

The user can ask questions such as:

```text
What changed in Figma?
```

```text
What changed in Notion?
```

```text
Did Canva change anything?
```

```text
Explain the Figma change in simple words.
```

```text
Explain the Notion change in simple words.
```

```text
What are Notion skills?
```

```text
Show me all product changes.
```

---

## Automatic Daily Monitoring

The monitoring system is configured to run automatically **every day at 9:00 AM** using **Windows Task Scheduler**.

### Schedule

```text
Task: Product Monitoring Agent
Frequency: Daily
Time: 9:00 AM
```

The automatic workflow is:

```text
Windows Task Scheduler
        ↓
Every day at 9:00 AM
        ↓
run_monitor.bat
        ↓
Activate Python virtual environment
        ↓
python main.py
        ↓
Check Notion
        ↓
Check Figma
        ↓
Check Canva
        ↓
Compare release dates
        ↓
Detect new changes
        ↓
Save changes to change_history.json
        ↓
Update product memory
```

This means the user does not need to manually start the monitoring program every morning.

---

## `run_monitor.bat`

The project includes:

```text
run_monitor.bat
```

This batch file is used by Windows Task Scheduler.

Its purpose is to:

1. Move into the project directory
2. Activate the Python virtual environment
3. Run `main.py`

The scheduled task starts this batch file every day at **9:00 AM**.

The same batch file can also be run manually if required.

---

## Manual Monitoring

The monitoring system can also be run manually.

First activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Then run:

```powershell
python main.py
```

---

## Example Monitoring Output

A normal monitoring check looks like:

```text
============================================================
🤖 PRODUCT MONITORING AGENT
============================================================

============================================================
🔍 Checking Notion...
Current release date: September 15, 2026
Previous release date: September 15, 2026
✅ No new change.

============================================================
🔍 Checking Figma...
Current release date: Sep 25, 2026
Previous release date: Sep 25, 2026
✅ No new change.

============================================================
🔍 Checking Canva...
Current release date: September 16, 2026
Previous release date: September 16, 2026
✅ No new change.

============================================================
✅ Monitoring check complete.
============================================================
```

---

## Example Detected Change

When a newer release is detected, the system displays information similar to:

```text
🚨 NEW PRODUCT CHANGE DETECTED!

Product: Figma
Release: Vertical wrap available in auto layout
Date: Sep 25, 2026

Description:
Vertical wrap is now available when auto layout is set to vertical flow.
```

The detected change is then stored in:

```text
change_history.json
```

---

## Complete End-to-End Workflow

The complete project workflow is:

```text
                  DAILY AT 9:00 AM
                         ↓
               Windows Task Scheduler
                         ↓
                  run_monitor.bat
                         ↓
                      main.py
                         ↓
        +----------------+----------------+
        |                |                |
        ↓                ↓                ↓
      Notion           Figma            Canva
        |                |                |
        +----------------+----------------+
                         ↓
                 Extract release data
                         ↓
                Compare stored memory
                         ↓
                  +------+------+
                  |             |
                  ↓             ↓
              No change     New change
                  |             |
                  |             ↓
                  |     Save to history
                  |             |
                  |             ↓
                  |    Update memory
                  |
                  ↓
                 Done


                    USER
                     ↓
                  agent.py
                     ↓
              Natural-language
                  question
                     ↓
          Retrieve relevant history
                     ↓
              Ollama / Qwen
                     ↓
                 AI answer
```

---

## Technologies Used

- **Python** — Main programming language
- **Requests** — HTTP requests
- **BeautifulSoup** — HTML parsing and web scraping
- **JSON** — Persistent change history
- **Ollama** — Local AI runtime
- **Qwen3 1.7B** — Local language model
- **PowerShell** — Development and execution
- **VS Code** — Development environment
- **Windows Task Scheduler** — Daily automation
- **Batch Script** — Automated project startup

---

## Setup

### Python

The project uses a Python virtual environment:

```text
.venv/
```

Activate it using PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

---

### Python Packages

The project uses packages including:

```text
requests
beautifulsoup4
ollama
```

---

### Ollama

The local AI portion requires Ollama.

The model used is:

```text
qwen3:1.7b
```

---

## Running the Project

### Start the monitoring system

```powershell
python main.py
```

### Start the AI agent

```powershell
python agent.py
```

### Automatic execution

Windows Task Scheduler runs:

```text
run_monitor.bat
```

every day at:

```text
9:00 AM
```

---

## Testing

The project was tested through the following workflow:

1. Run the monitoring system normally
2. Check Notion
3. Check Figma
4. Check Canva
5. Verify stored release dates
6. Simulate a product release-date change
7. Detect the simulated change
8. Store the detected change
9. Query the change using the AI agent
10. Verify that the AI retrieves the correct product record
11. Restore the normal product memory
12. Run the monitoring system again
13. Verify that all products report no new change when the stored dates match

The final monitoring check confirms that the stored baseline matches the currently detected release dates.

---

## Current Recorded Product Changes

The project's recorded product changes are stored in:

```text
change_history.json
```

Examples include:

### Notion

```text
Notion 3.7: Agent skills for your whole team
Date: September 15, 2026
```

### Figma

```text
Vertical wrap available in auto layout
Date: Sep 25, 2026
```

The history file contains the detailed descriptions and detection information.

---

## Limitations

### Website Structure

Product websites can change their HTML structure.

If a website changes its structure significantly, the corresponding scraper may need to be updated.

### Internet Access

The monitoring system requires access to the product release pages.

If a website is unavailable or blocks the request, the monitoring check may fail.

### Historical Coverage

The project only contains product changes that have been recorded by this monitoring system.

It does not attempt to reconstruct the complete historical release history of each product.

### AI Knowledge

The AI agent is grounded in:

```text
change_history.json
```

If a product change has not been recorded by the monitoring system, the AI may not have information about it.

### Product Coverage

The current system monitors:

- Notion
- Figma
- Canva

---

## Project Goal

The goal of this project is to demonstrate how multiple software-agent concepts can be combined into one practical system:

```text
Web Scraping
      +
Change Detection
      +
Persistent Memory
      +
Historical Storage
      +
Information Retrieval
      +
Local AI
      +
Scheduled Automation
```

The result is a system that can automatically monitor product updates and allow users to explore recorded changes using natural language.

---

## Current Project Status

The project currently includes:

- ✅ Notion monitoring
- ✅ Figma monitoring
- ✅ Canva monitoring
- ✅ Release-date comparison
- ✅ Persistent product memory
- ✅ Change history
- ✅ Duplicate prevention
- ✅ Error handling
- ✅ RAG-based retrieval
- ✅ Local Ollama AI
- ✅ Qwen3 1.7B
- ✅ Natural-language questions
- ✅ Windows Task Scheduler
- ✅ Daily automatic execution at 9:00 AM
- ✅ Manual monitoring
- ✅ Project documentation

---

## Conclusion

The Product Change Monitoring Agent combines web scraping, change detection, persistent memory, historical storage, information retrieval, local AI, and scheduled automation into one practical monitoring system.

The system automatically checks **Notion, Figma, and Canva** for product changes.

When a new change is detected, it is stored in the project's historical memory.

The AI agent can then retrieve those recorded changes and answer natural-language questions using the local Qwen3 model through Ollama.

The monitoring system runs automatically every day at **9:00 AM** through Windows Task Scheduler, while the monitoring system and AI agent can also be run manually.

This completes the Product Change Monitoring Agent project.