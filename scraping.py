import requests
from bs4 import BeautifulSoup
import re
from dateutil import parser
import time
import os
import google.generativeai as genai
from decouple import config

# --- Configuration ---
# It's highly recommended to store your API key securely.
# For quick testing only (NOT recommended for production):
genai.configure(api_key=config("GOOGLE_GENERATIVE_AI_API_KEY"))


# -------------------------------
# Utility Functions
# -------------------------------
def remove_unwanted_tags(soup_element):
    """Remove <script> and <ins> tags from a BeautifulSoup element."""
    for tag in soup_element.find_all(["script", "ins"]):
        tag.decompose()
    return soup_element


def clean_html(soup):
    """Strip class, id, style, and data-* attributes from all tags."""
    for tag in soup.find_all(True):
        attrs_to_remove = ["class", "id", "style"] + [
            attr for attr in tag.attrs if attr.startswith("data-")
        ]
        for attr in attrs_to_remove:
            tag.attrs.pop(attr, None)
    return soup


def remove_empty_list_items(soup):
    """Remove any <li> that has no text."""
    for li in soup.find_all("li"):
        if not li.get_text(strip=True):
            li.decompose()
    return soup


def format_date(date_str):
    """Convert a date string into YYYY-MM-DD, if possible."""
    try:
        dt = parser.parse(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str


# -------------------------------
# AI Paraphrasing Function
# -------------------------------
def paraphrase(description_html: str) -> str:
    """
    Paraphrase only the text within HTML tags, preserving structure.
    """
    sys_instruct = (
        "You are an AI paraphraser. Rephrase only the human-readable text inside HTML, "
        "keeping tags/attributes exactly as-is. Return just the HTML string."
    )
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-lite", system_instruction=sys_instruct
        )
        resp = model.generate_content(contents=[description_html])
        out = resp.text.replace("```html", "").replace("```", "").strip()
        return out
    except Exception as e:
        print(f"[Paraphrase error] {e}")
        return description_html


# -------------------------------
# Detail Page Extraction
# -------------------------------
def extract_detail_page_info(detail_url: str, headers: dict):
    """
    Fetch detail page and extract:
      - Full cleaned description HTML
      - List of application links (external)
      - og:image URL from meta tag
    """
    try:
        r = requests.get(detail_url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[Detail fetch failed] {detail_url} → {r.status_code}")
            return "", [], ""

        soup = BeautifulSoup(r.text, "html.parser")

        # Strategy 1: Try specific content selectors first
        content_selectors = [
            "div.elementor-widget-theme-post-content .elementor-widget-container",
            "div.entry-content",
            "article .elementor-widget-container",
            "div.post-content",
            ".elementor-text-editor .elementor-widget-container",
            "main .elementor-widget-container",
        ]

        container = None
        for selector in content_selectors:
            found = soup.select_one(selector)
            if found and len(found.get_text(strip=True)) > 100:
                container = found
                print(f"[Found content using] {selector}")
                break

        # Strategy 2: If no specific selector worked, find the largest meaningful container
        if not container:
            containers = soup.find_all("div", class_="elementor-widget-container")

            def is_likely_content(cont):
                text = cont.get_text(strip=True).lower()
                text_length = len(text)

                # Skip very short content (likely navigation/breadcrumbs)
                if text_length < 50:
                    return False

                # Skip if it looks like breadcrumbs
                if "/" in text and any(
                    word in text for word in ["home", "category", "internships"]
                ):
                    if text_length < 200:  # Allow longer breadcrumb-containing content
                        return False

                # Skip if it's mostly just links without substantial text
                link_ratio = len(cont.find_all("a")) / max(text_length / 50, 1)
                if link_ratio > 0.5 and text_length < 200:
                    return False

                return True

            # Filter and find the largest content container
            content_containers = [c for c in containers if is_likely_content(c)]

            if content_containers:
                container = max(
                    content_containers, key=lambda x: len(x.get_text(strip=True))
                )
                print(f"[Found content using] largest container strategy")
            else:
                print("[Warning] No suitable content container found")
                return "", [], ""

        # Clean the container
        remove_unwanted_tags(container)
        clean_html(container)
        remove_empty_list_items(container)

        # Additional cleanup: remove breadcrumb-like elements
        for elem in container.find_all(["nav", "ol", "ul"]):
            text = elem.get_text(strip=True).lower()
            if "/" in text and any(
                word in text for word in ["home", "category", "internships"]
            ):
                if len(text) < 100:  # Only remove short breadcrumb-like elements
                    elem.decompose()

        description_html = str(container)

        # Debug: Print first 200 chars to verify content
        preview = BeautifulSoup(description_html, "html.parser").get_text(strip=True)[
            :200
        ]
        print(f"[Content preview] {preview}...")

        # 2) Application links
        app_links = []
        for a in container.find_all("a", href=True):
            href = a["href"]
            if (
                href.startswith("http")
                and "dixcoverhub.com" not in href
                and any(
                    kw in a.get_text(strip=True).lower()
                    for kw in ["apply", "form", "register"]
                )
            ):
                app_links.append(href)

        # fallback: scan whole page
        if not app_links:
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if (
                    href.startswith("http")
                    and "dixcoverhub.com" not in href
                    and any(
                        kw in a.get_text(strip=True).lower()
                        for kw in ["apply", "form", "register"]
                    )
                ):
                    app_links.append(href)
        # NOW remove _all_ <a> tags from your container and
        for a in container.find_all("a"):
            a.decompose()
        description_html = str(container)

        # 3) OG image
        og_img = ""
        meta_img = soup.find("meta", property="og:image")
        if meta_img and meta_img.get("content"):
            og_img = meta_img["content"]

        return description_html, app_links, og_img

    except Exception as e:
        print(f"[Detail error] {e}")
        return "", [], ""


# -------------------------------
# API Posting Function
# -------------------------------
def post_to_api(data: dict) -> bool:
    """Post opportunity data to your Django REST endpoint."""
    # api_url = "http://127.0.0.1:8000/api/v1/opportunities/"
    api_url = "https://oppu-link.onrender.com/api/v1/opportunities/"

    try:
        res = requests.post(api_url, json=data, timeout=10)
        if res.status_code == 201:
            print(f"[Posted] {data['title']}")
            return True
        else:
            print(f"[Post failed] {res.status_code} {res.text}")
            return False
    except Exception as e:
        print(f"[Post error] {e}")
        return False


# -------------------------------
# Main Scraper
# -------------------------------
def main():
    base = "https://dixcoverhub.com.ng/category/graduate-programs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    total_pages = 4  # adjust as needed

    for p in range(3, total_pages + 1):
        page_url = base if p == 1 else f"{base}page/{p}/"
        print(f"\n→ Page {p}: {page_url}")

        try:
            r = requests.get(page_url, headers=headers, timeout=10)
            if r.status_code != 200:
                print(f"[List fetch failed] {r.status_code}")
                continue
            list_soup = BeautifulSoup(r.text, "html.parser")
        except Exception as e:
            print(f"[List error] {e}")
            continue

        cards = list_soup.find_all("div", class_="elementor-post__card")
        print(f"Found {len(cards)} posts.")

        for card in cards:
            # Title & link
            h3 = card.find("h3", class_="elementor-post__title")
            if not h3 or not (a := h3.find("a", href=True)):
                continue
            title = a.get_text(strip=True)
            link = a["href"]

            # Date
            date_txt = card.find("span", class_="elementor-post-date")
            date_posted = format_date(date_txt.get_text(strip=True)) if date_txt else ""

            # Slug
            slug = re.sub(r"[^\w-]", "", title.lower().replace(" ", "-"))

            # Thumbnail fallback
            og_image_url = ""
            thumb_div = card.find("div", class_="elementor-post__thumbnail__link")
            if thumb_div and (img := thumb_div.find("img")):
                og_image_url = img.get("src") or img.get("data-lazy-src", "")

            print(f"→ Scraping detail: {title}")
            desc_html, app_links, og_meta_img = extract_detail_page_info(link, headers)

            # Use meta if listing thumbnail missing
            if og_meta_img:
                og_image_url = og_meta_img

            # Paraphrase
            para_desc = paraphrase(desc_html)

            # Derive OG description
            plain = BeautifulSoup(para_desc, "html.parser").get_text(strip=True)
            og_desc = plain[:50].rsplit(" ", 1)[0] + "..." if len(plain) > 50 else plain

            payload = {
                "title": title,
                "category": "Graduate-programs",
                "link": link,
                "description": para_desc,
                "date_posted": date_posted,
                "application_link_urls": app_links,
                "og_image_url": og_image_url,
                "og_description": og_desc,
                "slug": slug,
            }

            post_to_api(payload)
            time.sleep(2)


if __name__ == "__main__":
    main()


# Base URL
# base_url = "https://dixcoverhub.com.ng/category/internships/"
# base_url = "https://dixcoverhub.com.ng/category/jobs/"
# base_url = "https://dixcoverhub.com.ng/category/scholarships-2/"
# base_url = "https://dixcoverhub.com.ng/category/bootcamps/"
# base_url = "https://dixcoverhub.com.ng/category/graduate-programs/"
# base_url = "https://dixcoverhub.com.ng/category/trainings/"
