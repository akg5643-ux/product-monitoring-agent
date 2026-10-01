import json
import re
import ollama

HISTORY_FILE = "change_history.json"
COMPANY_FILE = "fictional_company_context.json"
MODEL = "qwen3:1.7b"


# ============================================================
# LOAD DATA
# ============================================================

def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def load_company_context():
    try:
        with open(COMPANY_FILE, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


# ============================================================
# QUESTION DETECTION
# ============================================================

def detect_product(question):
    question_lower = question.lower()

    products = {
        "notion": "Notion",
        "figma": "Figma",
        "canva": "Canva"
    }

    for keyword, product_name in products.items():
        if keyword in question_lower:
            return product_name

    return None


def is_latest_question(question):
    question_lower = question.lower()

    phrases = [
        "latest change",
        "latest update",
        "latest release",
        "last change",
        "last update",
        "last release",
        "most recent change",
        "most recent update",
        "most recent release"
    ]

    return any(phrase in question_lower for phrase in phrases)


def is_all_changes_question(question):
    question_lower = question.lower()

    phrases = [
        "all changes",
        "all product changes",
        "everything that changed",
        "what changed across",
        "show me everything",
        "show all",
        "remain competitive",
        "stay competitive",
        "competitive response"
    ]

    return any(phrase in question_lower for phrase in phrases)


def is_impact_question(question):
    question_lower = question.lower()

    phrases = [
        "affect the fictional company",
        "affect fictional company",
        "impact the fictional company",
        "impact fictional company",
        "affect the company",
        "impact the company",
        "company impact",
        "business impact",
        "how does this affect",
        "how could this affect",
        "how will this affect"
    ]

    return any(phrase in question_lower for phrase in phrases)


def is_response_question(question):
    question_lower = question.lower()

    phrases = [
        "what should the fictional company do",
        "what should the company do",
        "what can the fictional company do",
        "what can the company do",
        "how should the fictional company respond",
        "how should the company respond",
        "how can the fictional company respond",
        "how can the company respond",
        "remain competitive",
        "stay competitive",
        "response to this change"
    ]

    return any(phrase in question_lower for phrase in phrases)


# ============================================================
# RETRIEVE PRODUCT CHANGES
# ============================================================

def retrieve_changes(question, history):

    product = detect_product(question)

    if product:

        product_records = [
            record
            for record in history
            if record.get("product", "").lower() == product.lower()
        ]

        if is_latest_question(question):
            return product_records[-1:]

        return product_records

    if is_all_changes_question(question):
        return history

    question_words = set(
        re.findall(r"[a-zA-Z0-9]+", question.lower())
    )

    matches = []

    for record in history:

        searchable_text = " ".join([
            str(record.get("product", "")),
            str(record.get("title", "")),
            str(record.get("description", ""))
        ]).lower()

        record_words = set(
            re.findall(r"[a-zA-Z0-9]+", searchable_text)
        )

        if question_words.intersection(record_words):
            matches.append(record)

    return matches


# ============================================================
# FORMAT CHANGE RECORDS
# ============================================================

def format_records(records):

    if not records:
        return "No stored product-change records were found."

    output = []

    for record in records:

        output.append(
            f"""
Product: {record.get("product", "")}
Title: {record.get("title", "")}
Date: {record.get("date", "")}
Description: {record.get("description", "")}
Source: {record.get("source", "")}
"""
        )

    return "\n".join(output)


# ============================================================
# EXTRACT COMPANY FACTS
# ============================================================

def get_company_features(company):

    features = company.get("product_features", [])

    results = []

    for feature in features:

        if not isinstance(feature, dict):
            continue

        name = feature.get("Feature", "")
        description = feature.get("Description", "")
        target_user = feature.get("Target User", "")
        similarity = feature.get("Similarity Status", "")

        if name:

            results.append({
                "name": name,
                "description": description,
                "target_user": target_user,
                "similarity": similarity
            })

    return results


def get_company_pricing(company):

    pricing = company.get("pricing", [])

    results = []

    for plan in pricing:

        if not isinstance(plan, dict):
            continue

        results.append({
            "plan": plan.get("Plan Name", ""),
            "price": plan.get("Price (INR/month)", ""),
            "billing": plan.get("Billing Basis", ""),
            "description": plan.get("Description", "")
        })

    return results


def get_customer_feedback(company):

    feedback = company.get("customer_feedback", [])

    results = []

    for item in feedback:

        if not isinstance(item, dict):
            continue

        results.append({
            "customer": item.get("Customer ID", ""),
            "segment": item.get("Segment", ""),
            "plan": item.get("Plan", ""),
            "rating": item.get("Rating (1-5)", ""),
            "sentiment": item.get("Sentiment", ""),
            "feedback": item.get("Feedback", ""),
            "pain_point": item.get("Pain Point", ""),
            "feature": item.get("Feature Mentioned", "")
        })

    return results


# ============================================================
# FIND EXPLICITLY RELEVANT COMPANY FACTS
# ============================================================

def find_relevant_company_facts(records, company):

    features = get_company_features(company)
    pricing = get_company_pricing(company)
    feedback = get_customer_feedback(company)

    change_text = " ".join([
        str(record.get("title", ""))
        + " "
        + str(record.get("description", ""))
        for record in records
    ]).lower()

    change_words = set(
        re.findall(r"[a-zA-Z0-9]+", change_text)
    )

    relevant_features = []
    relevant_feedback = []
    relevant_pricing = []

    # --------------------------------------------------------
    # Match company features using actual words appearing in
    # feature name/description/target user.
    # --------------------------------------------------------

    for feature in features:

        feature_text = " ".join([
            feature["name"],
            feature["description"],
            feature["target_user"]
        ]).lower()

        feature_words = set(
            re.findall(r"[a-zA-Z0-9]+", feature_text)
        )

        overlap = change_words.intersection(feature_words)

        # Require at least one meaningful overlap.
        meaningful_overlap = {
            word for word in overlap
            if len(word) >= 5
        }

        if meaningful_overlap:
            relevant_features.append(feature)

    # --------------------------------------------------------
    # Match customer feedback using actual words appearing in
    # feedback, pain point, and feature mentioned.
    # --------------------------------------------------------

    for item in feedback:

        feedback_text = " ".join([
            item["feedback"],
            item["pain_point"],
            item["feature"],
            item["segment"]
        ]).lower()

        feedback_words = set(
            re.findall(r"[a-zA-Z0-9]+", feedback_text)
        )

        overlap = change_words.intersection(feedback_words)

        meaningful_overlap = {
            word for word in overlap
            if len(word) >= 5
        }

        if meaningful_overlap:
            relevant_feedback.append(item)

    # --------------------------------------------------------
    # Pricing is only included when the monitored change
    # actually contains pricing-related words.
    # --------------------------------------------------------

    pricing_words = {
        "price",
        "pricing",
        "plan",
        "subscription",
        "cost",
        "paid",
        "free",
        "billing",
        "tier",
        "payment"
    }

    if change_words.intersection(pricing_words):
        relevant_pricing = pricing

    return {
        "features": relevant_features,
        "feedback": relevant_feedback,
        "pricing": relevant_pricing
    }


# ============================================================
# FORMAT RELEVANT COMPANY FACTS
# ============================================================

def format_relevant_company_facts(facts):

    sections = []

    features = facts.get("features", [])

    if features:

        lines = []

        for feature in features:

            lines.append(
                f"- Feature: {feature['name']}\n"
                f"  Description: {feature['description']}\n"
                f"  Target User: {feature['target_user']}\n"
                f"  Similarity Status: {feature['similarity']}"
            )

        sections.append(
            "EXPLICITLY MATCHED COMPANY FEATURES:\n"
            + "\n".join(lines)
        )

    feedback = facts.get("feedback", [])

    if feedback:

        lines = []

        for item in feedback:

            lines.append(
                f"- Customer: {item['customer']}\n"
                f"  Segment: {item['segment']}\n"
                f"  Feature Mentioned: {item['feature']}\n"
                f"  Feedback: {item['feedback']}\n"
                f"  Pain Point: {item['pain_point']}\n"
                f"  Sentiment: {item['sentiment']}"
            )

        sections.append(
            "EXPLICITLY MATCHED CUSTOMER FEEDBACK:\n"
            + "\n".join(lines)
        )

    pricing = facts.get("pricing", [])

    if pricing:

        lines = []

        for plan in pricing:

            lines.append(
                f"- {plan['plan']}: "
                f"{plan['price']} INR/month | "
                f"{plan['billing']} | "
                f"{plan['description']}"
            )

        sections.append(
            "RELEVANT COMPANY PRICING:\n"
            + "\n".join(lines)
        )

    if not sections:

        return (
            "NO DIRECT COMPANY FACTS WERE MATCHED TO THE "
            "MONITORED CHANGE.\n"
            "Do not invent a connection."
        )

    return "\n\n".join(sections)


# ============================================================
# FORMAT BASIC COMPANY SUMMARY
# ============================================================

def format_company_summary(company):

    summary = company.get("company_summary", {})

    if not summary:
        return "No company summary available."

    return f"""
Company: {summary.get("Company", "")}
Category: {summary.get("Category", "")}
Target Customers: {summary.get("Target Customers", "")}
Core Product: {summary.get("Core Product", "")}
Key Differentiators: {summary.get("Key Differentiators", "")}
"""


# ============================================================
# NORMAL PRODUCT QUESTION
# ============================================================

def ask_normal_ai(question, records):

    context = format_records(records)

    prompt = f"""
You are a Product Change Monitoring AI Agent.

Answer the user's question using ONLY the stored product-change
records below.

Rules:

- Do not use outside knowledge.
- Do not invent facts.
- Do not invent product features.
- Do not confuse one product with another.
- If the records do not contain enough information, say so.
- Keep the answer concise.

STORED PRODUCT-CHANGE RECORDS:

{context}

USER QUESTION:

{question}
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        },
        think=False
    )

    return response["message"]["content"]


# ============================================================
# STRICT COMPANY IMPACT ANALYSIS
# ============================================================

def ask_company_impact_ai(question, records, company):

    change_context = format_records(records)

    company_summary = format_company_summary(company)

    relevant_facts = find_relevant_company_facts(
        records,
        company
    )

    relevant_company_context = format_relevant_company_facts(
        relevant_facts
    )

    prompt = f"""
You are a Product Change Impact Analysis Assistant.

Your task is to analyze how a monitored product change MAY affect
a fictional company.

This is a strict grounded-analysis task.

============================================================
ENTITY SEPARATION
============================================================

There are TWO separate entities:

ENTITY 1:
The monitored product, such as Figma, Notion, or Canva.

ENTITY 2:
The fictional company.

A feature belonging to Entity 1 MUST NEVER be described as a feature
belonging to Entity 2.

For example:

Figma introduced "Community riffs."

Correct:
"Figma introduced Community riffs."

Incorrect:
"The fictional company introduced Community riffs."

Also incorrect:
"Community riffs is part of the fictional company's
Creator Micro-Licensing Marketplace."

unless the company dataset explicitly says that.

============================================================
COMPANY DATA RULE
============================================================

The fictional company is synthetic.

You may use ONLY the company information supplied below.

Do NOT invent:

- features
- capabilities
- customers
- customer needs
- pricing
- competitors
- partnerships
- integrations
- revenue
- market share
- business results
- strategic capabilities

If the company data does not establish something, say:

"The available company data does not establish a direct connection."

============================================================
VERY IMPORTANT: MATCHED FACTS
============================================================

The section called:

"EXPLICITLY MATCHED COMPANY FEATURES"

contains company features that were matched using actual words
from the monitored change.

The section called:

"EXPLICITLY MATCHED CUSTOMER FEEDBACK"

contains customer feedback that was matched using actual words
from the monitored change.

Use these facts as the primary grounding for company impact.

If there are NO matched company facts, do NOT force a connection.

Instead say that the available company data does not establish
a direct connection.

============================================================
INFERENCE RULE
============================================================

You MAY make a cautious business inference from an explicitly
matched company fact.

Example:

Figma introduces a feature for sharing creative work.

Company data says the fictional company has a
Creator Micro-Licensing Marketplace for creators.

Acceptable inference:

"Because the company already has a creator-focused
micro-licensing marketplace, the Figma change may be relevant
to how the company thinks about creator visibility and asset
discovery."

Unacceptable inference:

"The Figma feature will increase the company's marketplace
transactions."

The second statement predicts a business result that is not
supported by the company data.

Use:

- may
- could
- potentially
- might
- could be relevant
- may create pressure
- may create an opportunity

Do NOT state uncertain effects as facts.

============================================================
RESPONSE SUGGESTIONS
============================================================

Recommendations must be grounded in existing company information.

Prefer:

- improving an existing company feature
- clarifying an existing customer pain point
- strengthening an existing differentiator
- monitoring a relevant customer-feedback area
- improving an existing workflow
- improving existing documentation

Do NOT automatically recommend creating a new capability.

If the company dataset does not support a specific recommendation,
say so.

============================================================
REQUIRED ANSWER
============================================================

Use this structure:

1. WHAT CHANGED

Describe only the monitored product change.

2. EXISTING FICTIONAL-COMPANY AREA THAT MAY BE RELEVANT

Name an existing company feature, customer feedback item,
pricing element, target user, pain point, or differentiator.

If there is no direct match, explicitly say that.

3. WHY IT MAY MATTER

Explain the connection cautiously.

Do not claim that the two products have the same feature unless
the company data explicitly establishes that.

4. POTENTIAL IMPACT

Describe possible implications.

Do not invent measurable results, revenue changes, customer growth,
market share, or other outcomes.

5. WHAT THE FICTIONAL COMPANY COULD CONSIDER

Give grounded actions based on existing company information.

If there is not enough evidence for a specific action, say so.

============================================================
MONITORED PRODUCT CHANGE
============================================================

{change_context}

============================================================
FICTIONAL COMPANY SUMMARY
============================================================

{company_summary}

============================================================
EXPLICITLY MATCHED COMPANY INFORMATION
============================================================

{relevant_company_context}

============================================================
USER QUESTION
============================================================

{question}

Final reminder:

The monitored product's feature and the fictional company's
feature are separate things.

Never merge them.

Do not invent a relationship that the supplied company data
does not support.
"""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        options={
            "temperature": 0
        },
        think=False
    )

    return response["message"]["content"]


# ============================================================
# FALLBACK
# ============================================================

def fallback_answer(records):

    if not records:
        return "I could not find a matching product-change record."

    latest = records[-1]

    return (
        f"{latest.get('product', '')} changed: "
        f"{latest.get('title', '')} "
        f"({latest.get('date', '')}).\n\n"
        f"{latest.get('description', '')}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("🤖 PRODUCT CHANGE MONITORING AI AGENT")
    print("=" * 60)

    print()
    print("Ask questions about your monitored products.")
    print(
        "The AI can also assess potential impact on "
        "the fictional company."
    )

    print()
    print("Type 'exit' to stop.")
    print()

    company = load_company_context()

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":

            print()
            print("Goodbye!")
            break

        if not question:
            continue

        history = load_history()

        records = retrieve_changes(
            question,
            history
        )

        print()
        print(
            f"🔎 Retrieved {len(records)} relevant change(s)."
        )

        print()
        print("🤖 Agent is thinking...")
        print()

        try:

            if not records:

                answer = fallback_answer(records)

            elif (
                is_impact_question(question)
                or is_response_question(question)
            ):

                answer = ask_company_impact_ai(
                    question,
                    records,
                    company
                )

            else:

                answer = ask_normal_ai(
                    question,
                    records
                )

            print("🧠 AI:")
            print(answer)

        except Exception as error:

            print("⚠️ AI error:")
            print(error)

        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()