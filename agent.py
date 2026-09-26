import json
import re
import ollama


HISTORY_FILE = "change_history.json"
MODEL = "qwen3:1.7b"


def load_history():
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8-sig") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


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


def is_all_changes_question(question):
    question_lower = question.lower()

    phrases = [
        "all changes",
        "all product changes",
        "everything that changed",
        "what changed across",
        "show me everything",
        "show all"
    ]

    return any(phrase in question_lower for phrase in phrases)


def retrieve_changes(question, history):
    product = detect_product(question)

    # If the user clearly asks for a specific product,
    # search ONLY that product.
    if product:
        matches = [
            record
            for record in history
            if record.get("product", "").lower() == product.lower()
        ]

        return matches

    # If the user asks for all changes, return everything.
    if is_all_changes_question(question):
        return history

    # Otherwise search using important words from the question.
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


def format_records(records):
    formatted = []

    for i, record in enumerate(records, start=1):
        product = record.get("product", "Unknown")
        title = record.get("title", "Unknown")
        date = record.get("date", "Unknown")
        description = record.get("description", "")

        text = f"Record {i}:\n"
        text += f"Product: {product}\n"
        text += f"Title: {title}\n"
        text += f"Date: {date}\n"

        if description:
            text += f"Description: {description}\n"

        formatted.append(text)

    return "\n".join(formatted)


def fallback_answer(records):
    """Create a safe answer directly from stored data."""

    if not records:
        return "No recorded product change was found for that question."

    if len(records) == 1:
        record = records[0]

        product = record.get("product", "Unknown")
        title = record.get("title", "Unknown")
        date = record.get("date", "Unknown")
        description = record.get("description", "")

        answer = f"{product}: {title} ({date})."

        if description:
            answer += f" {description}"

        return answer

    lines = []

    for i, record in enumerate(records, start=1):
        product = record.get("product", "Unknown")
        title = record.get("title", "Unknown")
        date = record.get("date", "Unknown")

        lines.append(
            f"Record {i}: {product} — {title} ({date})."
        )

    return "\n".join(lines)


def ask_ai(question, records):
    context = format_records(records)

    prompt = f"""
You are a product change monitoring assistant.

Answer the user's question using ONLY the stored records below.

Do not use outside knowledge.
Do not invent facts.
Do not add details that are not present in the records.

If the records do not contain enough information to answer,
say that the information is not recorded.

Keep the answer concise and useful.

Stored records:
{context}

User question:
{question}
"""

    try:
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

        answer = response["message"]["content"].strip()

        # Remove any accidental reasoning block.
        answer = re.sub(
            r"<think>.*?</think>",
            "",
            answer,
            flags=re.DOTALL
        ).strip()

        if answer:
            return answer

    except Exception:
        pass

    return fallback_answer(records)


def main():

    print("=" * 60)
    print("🤖 PRODUCT CHANGE MONITORING AI AGENT")
    print("=" * 60)

    print()
    print("Ask questions about your monitored products.")
    print("The AI answers using your stored product-change history.")
    print()
    print("Type 'exit' to stop.")
    print()

    while True:

        question = input("You: ").strip()

        if question.lower() == "exit":
            print()
            print("👋 Agent stopped.")
            break

        if not question:
            continue

        history = load_history()

        records = retrieve_changes(question, history)

        print()
        print(f"🔎 Retrieved {len(records)} relevant change(s).")
        print()

        if not records:

            product = detect_product(question)

            if product:
                print(
                    f"🧠 AI:\n"
                    f"No recorded changes for {product}."
                )
            else:
                print(
                    "🧠 AI:\n"
                    "I couldn't find a recorded product change "
                    "that matches your question."
                )

            print()
            print("-" * 60)
            print()
            continue

        print("🤖 Agent is thinking...")
        print()

        answer = ask_ai(question, records)

        print("🧠 AI:")
        print(answer)

        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()