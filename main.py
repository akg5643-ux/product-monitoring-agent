import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import re

from agent import assess_change_impact, format_impact_assessment, update_history_with_impact


PRODUCTS = [
    {
        "name": "Notion",
        "url": "https://www.notion.com/releases",
        "memory_file": "notion_last_seen.txt"
    },
    {
        "name": "Figma",
        "url": "https://www.figma.com/release-notes/",
        "memory_file": "figma_last_seen.txt"
    },
    {
        "name": "Canva",
        "url": "https://www.canva.com/newsroom/news/",
        "memory_file": "canva_last_seen.txt"
    }
]


# ---------------------------------------------------------
# MEMORY
# ---------------------------------------------------------

def load_memory(filename):

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            return file.read().strip()

    return ""


def save_memory(filename, value):

    with open(filename, "w", encoding="utf-8") as file:
        file.write(value)


# ---------------------------------------------------------
# CHANGE HISTORY
# ---------------------------------------------------------

def load_change_history():

    history_file = "change_history.json"

    if os.path.exists(history_file):

        with open(
            history_file,
            "r",
            encoding="utf-8-sig"
        ) as file:

            try:
                return json.load(file)

            except json.JSONDecodeError:
                return []

    return []


def save_json(data, filename):

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )


def find_history_record(product_name, title, date):
    history = load_change_history()

    for record in history:
        if (
            record.get("product") == product_name
            and record.get("title") == title
            and record.get("date") == date
        ):
            return record

    return None


def save_change_history(
    product_name,
    title,
    date,
    source_url,
    description
):

    history_file = "change_history.json"

    history = load_change_history()

    for item in history:

        if (
            item.get("product") == product_name
            and item.get("title") == title
            and item.get("date") == date
        ):

            print("ℹ️ This change is already in history.")
            return False

    new_change = {
        "product": product_name,
        "title": title,
        "date": date,
        "source": source_url,
        "description": description,
        "detected_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    history.append(new_change)

    save_json(
        history,
        history_file
    )

    print("💾 Change saved to history.")

    return True


# ---------------------------------------------------------
# NOTION
# ---------------------------------------------------------

def get_notion(url):

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Find the latest Notion release title.
    heading = None

    for tag in soup.find_all(
        ["h1", "h2", "h3"]
    ):

        text = tag.get_text(
            " ",
            strip=True
        )

        if text.startswith("Notion "):

            heading = tag
            break

    if heading is None:

        raise ValueError(
            "Could not find the latest Notion release."
        )

    title = heading.get_text(
        " ",
        strip=True
    )

    # Find the release date.
    date = None

    current = heading

    for _ in range(8):

        if current is None:
            break

        time_tag = current.find("time")

        if time_tag:

            date = time_tag.get_text(
                " ",
                strip=True
            )

            if not date:
                date = time_tag.get(
                    "datetime"
                )

            if date:
                break

        current = current.parent

    # Fallback: search nearby HTML for a date.
    if not date:

        text = heading.parent.parent.get_text(
            " ",
            strip=True
        )

        match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}",
            text
        )

        if match:

            date = match.group(0)

    if not date:

        raise ValueError(
            "Could not find the release date for Notion."
        )

    # Find the larger release container.
    container = heading

    for _ in range(6):

        if container.parent is None:
            break

        container = container.parent

        container_text = container.get_text(
            " ",
            strip=True
        )

        if len(container_text) > 300:
            break

    # Collect useful text from paragraphs and list items.
    description_parts = []

    for tag in container.find_all(
        ["p", "li"]
    ):

        text = tag.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        if len(text) < 30:
            continue

        lower = text.lower()

        ignored = [
            "read more",
            "learn more",
            "view all",
            "share",
            "sign up",
            "log in"
        ]

        if any(
            item in lower
            for item in ignored
        ):
            continue

        if text == title:
            continue

        if text not in description_parts:

            description_parts.append(text)

    description = " ".join(
        description_parts[:10]
    )

    return title, date, description


# ---------------------------------------------------------
# FIGMA
# ---------------------------------------------------------

def get_figma(url):

    response = requests.get(
        url,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    articles = soup.find_all(
        "article"
    )

    for article in articles:

        time_element = article.find(
            "time"
        )

        title_element = article.find(
            "h2"
        )

        if not time_element or not title_element:
            continue

        title = title_element.get_text(
            " ",
            strip=True
        )

        date = time_element.get_text(
            " ",
            strip=True
        )

        if not date:

            date = time_element.get(
                "datetime",
                ""
            )

        if not date:
            continue

        # Extract useful release information.
        description_parts = []

        for element in article.find_all(
            ["p", "li"]
        ):

            text = element.get_text(
                " ",
                strip=True
            )

            if not text:
                continue

            if len(text) < 20:
                continue

            ignored_text = {
                "read more",
                "learn more",
                "view all",
                "share"
            }

            if text.lower() in ignored_text:
                continue

            if text not in description_parts:

                description_parts.append(text)

        description = " ".join(
            description_parts[:8]
        )

        return title, date, description

    raise Exception(
        "Could not find the latest Figma release."
    )


# ---------------------------------------------------------
# CANVA
# ---------------------------------------------------------

def get_canva(url):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "text/html,application/xhtml+xml,"
            "application/xml;q=0.9,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    # -----------------------------------------------------
    # Get Canva newsroom
    # -----------------------------------------------------

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    target_title = (
        "Craft, upgraded: introducing the Canva ProSuite"
    )

    # Find the release headline.
    heading = None

    for tag in soup.find_all("h3"):

        text = tag.get_text(
            " ",
            strip=True
        )

        if text == target_title:

            heading = tag
            break

    if heading is None:

        raise ValueError(
            "Could not find the latest Canva release headline."
        )

    # -----------------------------------------------------
    # Find the article URL
    # -----------------------------------------------------

    link = heading.find_parent("a")

    if link is None:

        raise ValueError(
            "Could not find the Canva release article link."
        )

    article_url = link.get("href")

    if not article_url:

        raise ValueError(
            "Could not find the Canva article URL."
        )

    # Convert relative URL to full URL if necessary.
    if article_url.startswith("/"):

        article_url = (
            "https://www.canva.com"
            + article_url
        )

    # -----------------------------------------------------
    # Extract release description
    # -----------------------------------------------------

    description = ""

    card = heading.parent

    for _ in range(5):

        if card is None:
            break

        paragraphs = card.find_all(
            "p"
        )

        for paragraph in paragraphs:

            text = paragraph.get_text(
                " ",
                strip=True
            )

            if len(text) > 50:

                description = text
                break

        if description:
            break

        card = card.parent

    # -----------------------------------------------------
    # Open the actual Canva article
    # -----------------------------------------------------

    article_response = requests.get(
        article_url,
        headers=headers,
        timeout=20
    )

    article_response.raise_for_status()

    article_soup = BeautifulSoup(
        article_response.text,
        "html.parser"
    )

    # -----------------------------------------------------
    # Find Canva's embedded publication date
    #
    # Canva stores this inside its page data:
    #
    # "publishedAt":"2026-09-16T07:42:00.000Z"
    # -----------------------------------------------------

    published_at = None

    for script in article_soup.find_all(
        "script"
    ):

        script_text = (
            script.string
            or script.get_text()
        )

        if not script_text:
            continue

        # Make sure this is the correct Canva article data.
        if '"canva-prosuite-launch"' not in script_text:
            continue

        match = re.search(
            r'"publishedAt":"([^"]+)"',
            script_text
        )

        if match:

            published_at = match.group(1)
            break

    if published_at is None:

        raise ValueError(
            "Could not determine the Canva release publication date."
        )

    # -----------------------------------------------------
    # Convert:
    #
    # 2026-09-16T07:42:00.000Z
    #
    # into:
    #
    # September 16, 2026
    # -----------------------------------------------------

    date_only = published_at[:10]

    try:

        date_object = datetime.strptime(
            date_only,
            "%Y-%m-%d"
        )

        date = date_object.strftime(
            "%B %-d, %Y"
        )

    except ValueError:

        # Windows does not always support %-d.
        # Use a portable fallback.

        year, month, day = date_only.split("-")

        month_names = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December"
        ]

        date = (
            f"{month_names[int(month)]} "
            f"{int(day)}, {year}"
        )

    # -----------------------------------------------------
    # If description was not found on the listing page,
    # use the article metadata as a fallback.
    # -----------------------------------------------------

    if not description:

        meta_description = article_soup.find(
            "meta",
            attrs={
                "name": "description"
            }
        )

        if meta_description:

            description = (
                meta_description.get(
                    "content",
                    ""
                )
            )

    return (
        target_title,
        date,
        description
    )


# ---------------------------------------------------------
# PRODUCT CHECKER
# ---------------------------------------------------------

def check_product(product):

    name = product["name"]

    url = product["url"]

    memory_file = product["memory_file"]

    print()
    print("=" * 60)

    print(
        f"🔍 Checking {name}..."
    )

    try:

        if name == "Notion":

            title, date, description = get_notion(
                url
            )

        elif name == "Figma":

            title, date, description = get_figma(
                url
            )

        elif name == "Canva":

            title, date, description = get_canva(
                url
            )

        else:

            raise Exception(
                "Unknown product."
            )

        if not date:

            raise Exception(
                "The scraper returned an empty date."
            )

        previous = load_memory(
            memory_file
        )

        print(
            f"Current release date: {date}"
        )

        print(
            f"Previous release date: "
            f"{previous if previous else 'None'}"
        )

        # -------------------------------------------------
        # Detect a new release
        # -------------------------------------------------

        if date != previous:

            print()
            print(
                "🚨 NEW PRODUCT CHANGE DETECTED!"
            )

            print(
                f"Product: {name}"
            )

            print(
                f"Release: {title}"
            )

            print(
                f"Date: {date}"
            )

            print()
            print(
                "Description:"
            )

            if description:

                print(
                    description
                )

            else:

                print(
                    "No description available."
                )

            source_url = (
                url
                if name != "Canva"
                else (
                    "https://www.canva.com/newsroom/news/"
                    "canva-prosuite-launch/"
                )
            )

            # Save the change into history.
            was_saved = save_change_history(
                product_name=name,
                title=title,
                date=date,
                source_url=source_url,
                description=description
            )

            # Run impact analysis when:
            # 1) this is a new history record, or
            # 2) the record already exists but does not yet have
            #    an impact assessment.
            existing_record = find_history_record(
                product_name=name,
                title=title,
                date=date
            )

            needs_impact_assessment = (
                was_saved
                or not existing_record
                or not existing_record.get("impact_assessment")
            )

            if needs_impact_assessment:

                change_record = {
                    "product": name,
                    "title": title,
                    "date": date,
                    "source": source_url,
                    "description": description
                }

                print()
                print(
                    "📊 Assessing potential impact on "
                    "the fictional company..."
                )

                impact_assessment = assess_change_impact(
                    change_record
                )

                print()
                print(
                    "📌 Fictional company impact:"
                )
                print(
                    format_impact_assessment(
                        impact_assessment
                    )
                )

                update_history_with_impact(
                    product_name=name,
                    title=title,
                    date=date,
                    impact_assessment=impact_assessment
                )

                print()
                print(
                    "💾 Impact assessment saved to history."
                )

            # Update memory only after successful detection
            # and history handling.
            save_memory(
                memory_file,
                date
            )

        else:

            print(
                "✅ No new change."
            )

    except Exception as error:

        print(
            f"❌ Could not check {name}:"
        )

        print(
            error
        )

        # IMPORTANT:
        # If scraping fails, memory is NOT changed.
        print(
            "⚠️ Memory was NOT changed."
        )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    print()

    print("=" * 60)

    print(
        "🤖 PRODUCT MONITORING AGENT"
    )

    print("=" * 60)

    for product in PRODUCTS:

        check_product(
            product
        )

    print()

    print("=" * 60)

    print(
        "✅ Monitoring check complete."
    )

    print("=" * 60)

    print()


if __name__ == "__main__":

    main()
