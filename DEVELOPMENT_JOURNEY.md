# Development Journey — Product Change Monitoring Agent

This document records the development journey of the Product Change Monitoring Agent, from the initial Python experiments to the final working monitoring and AI system.

The purpose of this document is to show the major problems encountered, the solutions developed, and how the different components were combined into the final project.

---

# 1. Project Idea

The original goal was to build an agent that could monitor product updates from:

- Notion
- Figma
- Canva

The system should detect when a new product release appears and remember the change.

The final goal was:

```text
Product Release Pages
        ↓
Monitoring System
        ↓
Detect New Changes
        ↓
Store History
        ↓
AI Agent
        ↓
Answer Questions About Changes

---

# 2. Development Environment



