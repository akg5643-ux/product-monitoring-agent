# Product Change Monitoring Agent

A Python-based product monitoring agent that tracks release updates from **Notion, Figma, and Canva**, detects new product changes, stores them in a local historical record, and allows users to ask natural-language questions about recorded changes using a local AI model.

The project combines **web scraping, change detection, persistent memory, historical storage, Retrieval-Augmented Generation (RAG), local AI, fictional company context, contextual company-impact analysis, and scheduled automation** into one practical product intelligence system.

---

## Project Overview

The Product Change Monitoring Agent automatically checks official product release and update pages for Notion, Figma, and Canva.

The system compares the latest detected release date with the previously stored release date for each product.

If a new release is detected, the agent:

1. Detects the change
2. Displays the new release information
3. Saves the change to `change_history.json`
4. Updates the product's stored release date
5. Prevents the same release from being recorded repeatedly

The project also includes a local AI agent that can answer natural-language questions about previously recorded product changes.

The system can also use a separate fictional company context file to provide contextual analysis of how recorded product changes may relate to the fictional company's existing product features, pricing, target customers, customer feedback, pain points, and differentiators.

---

## Products Monitored

The agent currently monitors:

* Notion
* Figma
* Canva

### Source Pages

* Notion Releases: [https://www.notion.com/releases](https://www.notion.com/releases)
* Figma Release Notes: [https://www.figma.com/release-notes/](https://www.figma.com/release-notes/)
* Canva Newsroom: [https://www.canva.com/newsroom/news/](https://www.canva.com/newsroom/news/)

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

                Extract Release Data

                        |

                        v

                Compare Release Date
                With Stored Memory

                        |

                 +------+------+
                 |             |
                 |             |
             No Change      New Change
                 |             |
                 v             v
             Continue      Save Change
                               |
                               v
                     change_history.json
                               |
                               v
                         agent.py
                               |
                               v
                       Retrieve Records
                               |
                               v
                       Ollama Local AI
                               |
                               v
                    Natural Language Answer
```

The monitoring workflow continuously compares the latest release information with the previously stored release date for each product.

If the release date has not changed, the system reports that there is no new change.

If a newer release is detected, the system records it in the historical database.

---

## Project Architecture

The project consists of two primary workflows:

1. Product Monitoring Workflow
2. AI and RAG Question-Answering Workflow

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

Detect new product change

        ↓

Save change to change_history.json

        ↓

Update product memory

        ↓

Prevent duplicate records
```

### AI and RAG Workflow

```text
User Question

        ↓

agent.py

        ↓

Identify relevant product/change

        ↓

Retrieve relevant records

        ↓

change_history.json

        ↓

Provide retrieved information
to local AI

        ↓

Ollama / Qwen3 1.7B

        ↓

Generate natural-language answer
```

The RAG workflow uses the recorded product history as the primary knowledge source rather than allowing the AI to freely generate product-history information without retrieved records.

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
├── fictional_company_context.json
│
├── notion_last_seen.txt
├── figma_last_seen.txt
├── canva_last_seen.txt
│
├── run_monitor.bat
└── README.md
```

### File Responsibilities

| File                             | Purpose                                                                      |
| -------------------------------- | ---------------------------------------------------------------------------- |
| `main.py`                        | Main product monitoring system                                               |
| `agent.py`                       | Natural-language RAG agent                                                   |
| `change_history.json`            | Stores detected product changes                                              |
| `fictional_company_context.json` | Stores structured fictional company information used for contextual analysis |
| `notion_last_seen.txt`           | Stores the last detected Notion release date                                 |
| `figma_last_seen.txt`            | Stores the last detected Figma release date                                  |
| `canva_last_seen.txt`            | Stores the last detected Canva release date                                  |
| `run_monitor.bat`                | Starts the monitoring system for scheduled execution                         |
| `README.md`                      | Project documentation                                                        |
| `.venv/`                         | Python virtual environment                                                   |
| `.vscode/`                       | VS Code configuration                                                        |

---

## Main Components

### `main.py`

`main.py` is the main monitoring program.

It is responsible for:

* Checking official product release pages
* Extracting release information
* Comparing current and previous release dates
* Detecting new product changes
* Saving detected changes
* Updating product memory
* Preventing duplicate history records
* Handling monitoring errors

Run it manually with:

```powershell
python main.py
```

The monitoring program checks:

```text
Notion
   ↓
Figma
   ↓
Canva
```

and compares the latest detected information with the stored product memory.

---

### `agent.py`

`agent.py` is the natural-language question-answering agent.

It uses recorded product history to answer questions about previously detected changes.

The agent retrieves relevant information from:

```text
change_history.json
```

and provides that information to the local Qwen3 model through Ollama.

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
Sep 30, 2026
```

When `main.py` runs, it compares the current release date with the stored date.

### No Change

```text
Current release date: Sep 30, 2026

Previous release date: Sep 30, 2026

✅ No new change.
```

When both dates match, the system does not create another history record.

### New Change

If the current release date is newer:

```text
Current release date: Oct 1, 2026

Previous release date: Sep 30, 2026

🚨 NEW PRODUCT CHANGE DETECTED!
```

The system then:

1. Displays the detected change
2. Saves the change to `change_history.json`
3. Updates the corresponding product memory file

This persistent-memory approach allows the system to remember which release date it has already processed.

---

## Change History

All detected product changes are stored in:

```text
change_history.json
```

This file acts as the project's historical memory.

Each record can contain:

* Product
* Release title
* Release date
* Source URL
* Description
* Detection time

Example:

```json
[
  {
    "product": "Figma",
    "title": "Post riffs to Figma Community",
    "date": "Sep 30, 2026",
    "source": "https://www.figma.com/release-notes/",
    "description": "Community riffs are a new way to share your latest ideas, animations, prototypes, and experiments. Post riffs to the Figma Community and to your Community profile to showcase your best work and build out a creative portfolio you’re proud of in Figma.",
    "detected_at": "2026-10-01 14:36:00"
  }
]
```

The history file allows the AI agent to retrieve information about previously detected changes.

---

## Duplicate Prevention

The monitoring system checks whether a detected release is already present in:

```text
change_history.json
```

If the same product release has already been recorded, it is not added again.

This prevents duplicate history records when the monitoring system runs repeatedly.

For example:

```text
Figma
Post riffs to Figma Community
Sep 30, 2026
```

If the monitoring system detects the same release again during a later run, it does not create another identical record.

This keeps the historical record cleaner and allows the RAG agent to retrieve meaningful records without unnecessary duplication.

---

## Error Handling

The monitoring system includes error handling for situations such as:

* Website request failures
* Network problems
* Unexpected webpage structures
* Missing release information
* Parsing errors
* Invalid or incomplete retrieved information

If a monitoring request fails, the system avoids intentionally replacing valid stored memory with invalid information.

This helps protect the previously stored release date when the website cannot be successfully checked.

---

# Local AI

The project uses **Ollama** to run the AI model locally.

The model used by the project is:

```text
qwen3:1.7b
```

The AI runs locally rather than relying on a paid external AI API for the final AI workflow.

The local AI layer uses the recorded product changes as its knowledge source.

The general flow is:

```text
Recorded Product Changes

        ↓

change_history.json

        ↓

agent.py

        ↓

Retrieve Relevant Information

        ↓

Ollama

        ↓

Qwen3 1.7B

        ↓

Natural-Language Answer
```

Using a local model allows the project to run the question-answering component locally on the user's computer.

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

Ollama / Qwen3 1.7B

      ↓

Generate answer
```

For example, if the user asks:

```text
What changed in Figma?
```

the agent identifies Figma as the relevant product and retrieves the stored Figma records.

The retrieved information is then provided to Qwen3 1.7B through Ollama.

This helps keep the AI answers grounded in product changes that have actually been recorded by the monitoring system.

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

The agent can also use the fictional company context for contextual questions related to the monitored changes.

---

## Fictional Company Context

The project includes a separate fictional company context file:

```text
fictional_company_context.json
```

This file contains structured information about a fictional company.

The fictional company context includes information such as:

* Company overview
* Target customers
* Product features
* Pricing plans
* Customer feedback
* Pain points
* Product differentiators

The fictional company context is separate from the monitored product history.

The separation is important because the monitored products and the fictional company represent different entities.

The project therefore maintains two different information sources:

```text
External Product Monitoring

        ↓

Notion / Figma / Canva

        ↓

change_history.json
```

and:

```text
Fictional Company Information

        ↓

fictional_company_context.json
```

These sources can then be used together when contextual analysis is required.

---

## Company-Impact Analysis

The project can use recorded product changes together with the fictional company context for contextual company-impact analysis.

The analysis distinguishes between:

1. The monitored external product or product change
2. The fictional company's existing product information

The system should not treat a feature released by Notion, Figma, or Canva as if it were already a feature of the fictional company.

For example:

```text
Monitored Product:

Figma

Post riffs to Figma Community
```

and:

```text
Fictional Company:

Existing product features
Existing pricing plans
Existing customer feedback
Existing pain points
Existing differentiators
```

are treated as separate information.

The fictional company context is used to understand which existing company information is relevant when considering a monitored product change.

The analysis can use the available company information such as:

* Product features
* Pricing plans
* Target customers
* Customer feedback
* Pain points
* Product differentiators

The purpose is to provide contextual information while keeping the analysis grounded in the fictional company data available to the system.

The company-impact workflow can be represented as:

```text
Recorded Product Change

        ↓

Identify Monitored Product

        ↓

Retrieve Product Change Details

        ↓

Load Fictional Company Context

        ↓

Review Relevant Company Information

        ↓

Compare the Change With Existing
Company Information

        ↓

Provide Contextual Analysis
```

The monitored product remains separate from the fictional company throughout this process.

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

The current batch file is:

```bat
@echo off
cd /d "C:\Users\Asus\OneDrive\Desktop\product-monitoring-agent"
call .venv\Scripts\activate.bat
python main.py
```

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

To start the AI agent:

```powershell
python agent.py
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

Current release date: Sep 30, 2026

Previous release date: Sep 30, 2026

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

When the current and stored release dates are the same, the system reports that no new change has been detected.

---

## Example Detected Change

When a newer release is detected, the system displays information similar to:

```text
🚨 NEW PRODUCT CHANGE DETECTED!

Product: Figma

Release: Post riffs to Figma Community

Date: Sep 30, 2026

Description:

Community riffs are a new way to share your latest ideas,
animations, prototypes, and experiments. Post riffs to the
Figma Community and to your Community profile to showcase
your best work and build out a creative portfolio you’re
proud of in Figma.
```

The detected change is then stored in:

```text
change_history.json
```

The corresponding product memory is also updated so that the same release is not repeatedly treated as a new change.

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
              +-----------------+-----------------+
              |                 |                 |
              ↓                 ↓                 ↓
           Notion             Figma             Canva
              |                 |                 |
              +-----------------+-----------------+
                                ↓
                       Extract release data
                                ↓
                       Compare stored memory
                                ↓
                       +--------+--------+
                       |                 |
                       ↓                 ↓
                   No Change        New Change
                       |                 |
                       |                 ↓
                       |          Save to history
                       |                 |
                       |                 ↓
                       |          Update memory
                       |
                       ↓
                      Done


                         HISTORICAL DATA
                                ↓
                      change_history.json
                                ↓
                           agent.py
                                ↓
                       Natural-language
                            question
                                ↓
                    Retrieve relevant history
                                ↓
                       Ollama / Qwen3 1.7B
                                ↓
                           AI answer


                    FICTIONAL COMPANY CONTEXT
                                ↓
                 fictional_company_context.json
                                ↓
                  Company features / pricing /
                  customers / feedback / pain points /
                  differentiators
                                ↓
                    Contextual company analysis
```

The system therefore combines automated monitoring with historical memory and local AI-powered retrieval.

---

## Technologies Used

* **Python** — Main programming language
* **Requests** — HTTP requests
* **BeautifulSoup** — HTML parsing and web scraping
* **JSON** — Persistent change history and fictional company context
* **Ollama** — Local AI runtime
* **Qwen3 1.7B** — Local language model
* **PowerShell** — Development and execution
* **VS Code** — Development environment
* **Windows Task Scheduler** — Daily automation
* **Batch Script** — Automated project startup
* **Git** — Version control
* **GitHub** — Source code repository

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

These packages support:

* Website requests
* HTML parsing
* Local Ollama interaction

---

### Ollama

The local AI portion requires Ollama.

The model used is:

```text
qwen3:1.7b
```

The model runs locally through Ollama.

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

The scheduled batch file activates the virtual environment and executes:

```text
python main.py
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

The project was also tested with the local AI workflow to verify that recorded product changes can be retrieved and explained using natural-language questions.

---

## Current Recorded Product Changes

The project's recorded product changes are stored in:

```text
change_history.json
```

### Notion

```text
Product: Notion

Title: Notion 3.7: Agent skills for your whole team

Date: September 15, 2026
```

### Figma

```text
Product: Figma

Title: Post riffs to Figma Community

Date: Sep 30, 2026
```

Description:

```text
Community riffs are a new way to share your latest ideas,
animations, prototypes, and experiments. Post riffs to the
Figma Community and to your Community profile to showcase
your best work and build out a creative portfolio you’re
proud of in Figma.
```

### Canva

The current Canva baseline is:

```text
Product: Canva

Date: September 16, 2026
```

The monitoring system currently treats this date as the stored baseline when checking for new Canva changes.

The detailed historical information is stored in:

```text
change_history.json
```

---

## Git and GitHub

The project is maintained using Git and hosted on GitHub.

### GitHub Repository

[https://github.com/akg5643-ux/product-monitoring-agent](https://github.com/akg5643-ux/product-monitoring-agent)

The repository contains the project source code and documentation.

### Git Workflow

After making project changes:

```powershell
git add .
```

Then create a commit:

```powershell
git commit -m "Update project"
```

Then push the changes:

```powershell
git push
```

A typical workflow is:

```text
Make changes

      ↓

git add .

      ↓

git commit -m "Update project"

      ↓

git push

      ↓

GitHub
```

Git does not automatically upload future changes. The project must be committed and pushed whenever updated files need to be uploaded to GitHub.

---

## Limitations

### Website Structure

Product websites can change their HTML structure.

If a website changes its structure significantly, the corresponding scraper may need to be updated.

### Internet Access

The monitoring system requires access to the product release pages.

If a website is unavailable, blocks the request, or changes its response structure, the monitoring check may fail.

### Historical Coverage

The project only contains product changes that have been recorded by this monitoring system.

It does not attempt to reconstruct the complete historical release history of each product.

### AI Knowledge

The AI agent is grounded primarily in:

```text
change_history.json
```

If a product change has not been recorded by the monitoring system, the AI may not have information about it.

The fictional company analysis is grounded in:

```text
fictional_company_context.json
```

The AI should not treat information that is not present in these project sources as confirmed company information.

### Product Coverage

The current system monitors:

* Notion
* Figma
* Canva

Additional products would require additional monitoring logic and product-specific release-page handling.

### Local Model Limitations

The project uses:

```text
Qwen3 1.7B
```

through Ollama.

Because the model is a relatively small local model, the quality of generated natural-language answers can vary depending on the complexity of the question and the amount of retrieved information.

The RAG workflow therefore focuses on retrieving the relevant stored information before generating an answer.

### Company-Impact Analysis Limitations

The fictional company analysis is based only on the information available in:

```text
fictional_company_context.json
```

The analysis should not be interpreted as verified real-world market intelligence.

The monitored product information and fictional company information remain separate.

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

RAG

      +

Fictional Company Context

      +

Contextual Analysis

      +

Scheduled Automation

      +

Git / GitHub
```

The result is a system that can automatically monitor product updates and allow users to explore recorded changes using natural language.

The project also demonstrates how monitored external product information can be combined with structured fictional company information for contextual product-impact analysis without treating the external product data as if it were company-owned data.

---

## Current Project Status

The project currently includes:

* ✅ Notion monitoring
* ✅ Figma monitoring
* ✅ Canva monitoring
* ✅ Official release-page monitoring
* ✅ Release-date comparison
* ✅ Persistent product memory
* ✅ `notion_last_seen.txt`
* ✅ `figma_last_seen.txt`
* ✅ `canva_last_seen.txt`
* ✅ Change history
* ✅ `change_history.json`
* ✅ Duplicate prevention
* ✅ Error handling
* ✅ RAG-based retrieval
* ✅ Local Ollama AI
* ✅ Qwen3 1.7B
* ✅ Natural-language questions
* ✅ Windows Task Scheduler
* ✅ Daily automatic execution at 9:00 AM
* ✅ `run_monitor.bat`
* ✅ Manual monitoring
* ✅ Fictional company context
* ✅ `fictional_company_context.json`
* ✅ Product feature context
* ✅ Pricing context
* ✅ Customer feedback context
* ✅ Pain-point context
* ✅ Product differentiator context
* ✅ Contextual company-impact analysis
* ✅ Git version control
* ✅ GitHub repository
* ✅ Project documentation

---

## Conclusion

The Product Change Monitoring Agent combines web scraping, change detection, persistent memory, historical storage, information retrieval, Retrieval-Augmented Generation, local AI, fictional company context, contextual analysis, and scheduled automation into one practical monitoring system.

The system automatically checks **Notion, Figma, and Canva** for product changes.

When a new change is detected, it is stored in the project's historical memory:

```text
change_history.json
```

The product-specific memory files:

```text
notion_last_seen.txt
figma_last_seen.txt
canva_last_seen.txt
```

allow the system to compare newly detected release dates with previously processed releases and avoid repeatedly treating the same release as a new change.

The AI agent uses:

```text
agent.py
      ↓
change_history.json
      ↓
Retrieval
      ↓
Ollama
      ↓
Qwen3 1.7B
      ↓
Natural-language answer
```

This allows users to ask questions such as:

```text
What changed in Figma?
```

or:

```text
Explain the Notion change in simple words.
```

The project also contains:

```text
fictional_company_context.json
```

which provides structured fictional company information covering areas such as company overview, target customers, product features, pricing plans, customer feedback, pain points, and product differentiators.

This information can be used together with recorded product changes for contextual company-impact analysis while keeping the monitored external products separate from the fictional company's existing information.

The monitoring system runs automatically every day at **9:00 AM** through Windows Task Scheduler using:

```text
run_monitor.bat
```

The monitoring system and AI agent can also be run manually through Python.

The complete project demonstrates how web monitoring, persistent memory, RAG, local AI, contextual analysis, and automation can be combined into a single practical Product Change Monitoring Agent.
