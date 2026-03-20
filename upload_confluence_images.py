#!/usr/bin/env python3
"""
upload_confluence_images.py

Uploads PNG charts from an analysis folder as Confluence page attachments,
then replaces 📎 placeholder lines in the page body with embedded images.

Usage:
    source .venv/bin/activate
    python upload_confluence_images.py --page-id PAGE_ID --images-dir PATH/TO/FOLDER/
    python upload_confluence_images.py --page-id PAGE_ID --images-dir PATH/TO/FOLDER/ --dry-run

Requirements:
    - .env file at project root containing: ATLASSIAN_API_TOKEN, ATLASSIAN_EMAIL, ATLASSIAN_BASE
    - requests, python-dotenv (already in .venv)
"""

import argparse
import base64
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# ── Config ─────────────────────────────────────────────────────────────────────

ATLASSIAN_BASE = os.environ.get("ATLASSIAN_BASE", "")
REST_API = f"{ATLASSIAN_BASE}/wiki/rest/api"
EMAIL = os.environ.get("ATLASSIAN_EMAIL", "")
IMAGE_WIDTH = 760  # px — matches Confluence default table width


# ── Auth ───────────────────────────────────────────────────────────────────────

def load_token() -> str:
    token = os.environ.get("ATLASSIAN_API_TOKEN", "")
    missing = [k for k, v in {"ATLASSIAN_API_TOKEN": token, "ATLASSIAN_EMAIL": EMAIL, "ATLASSIAN_BASE": ATLASSIAN_BASE}.items() if not v]
    if missing:
        print(f"Error: {', '.join(missing)} not found in .env or environment.")
        sys.exit(1)
    return token


def auth_headers(token: str) -> dict:
    creds = base64.b64encode(f"{EMAIL}:{token}".encode()).decode()
    return {"Authorization": f"Basic {creds}"}


# ── Attachment upload ───────────────────────────────────────────────────────────

def upload_attachment(page_id: str, png_path: Path, headers: dict) -> bool:
    """Upload a PNG as a page attachment. Returns True on success."""
    url = f"{REST_API}/content/{page_id}/child/attachment"
    with open(png_path, "rb") as f:
        resp = requests.post(
            url,
            headers={**headers, "X-Atlassian-Token": "no-check"},
            files={"file": (png_path.name, f, "image/png")},
        )
    if resp.status_code in (200, 201):
        print(f"  ✓ Uploaded:       {png_path.name}")
        return True
    # Confluence returns 400 with "already exists" for duplicate attachment names
    if resp.status_code == 400 and "already exists" in resp.text.lower():
        print(f"  ~ Already exists: {png_path.name}")
        return True
    print(f"  ✗ Failed ({resp.status_code}): {png_path.name} — {resp.text[:200]}")
    return False


# ── Page fetch / update ────────────────────────────────────────────────────────

def get_page(page_id: str, headers: dict) -> dict:
    """Fetch page title, version number, and body in storage (XHTML) format."""
    url = f"{REST_API}/content/{page_id}?expand=body.storage,version,title"
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return {
        "title": data["title"],
        "version": data["version"]["number"],
        "body": data["body"]["storage"]["value"],
    }


def update_page(page_id: str, title: str, version: int, body: str, headers: dict):
    """Push updated page body back to Confluence in storage format."""
    url = f"{REST_API}/content/{page_id}"
    payload = {
        "version": {"number": version + 1},
        "type": "page",
        "title": title,
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    resp = requests.put(
        url,
        json=payload,
        headers={**headers, "Content-Type": "application/json"},
    )
    if resp.status_code == 200:
        print("✓ Page updated successfully.")
        page_url = f"{ATLASSIAN_BASE}/wiki/spaces/TAI/pages/{page_id}"
        print(f"  → {page_url}")
    else:
        print(f"✗ Page update failed ({resp.status_code}): {resp.text[:400]}")
        sys.exit(1)


# ── Placeholder replacement ────────────────────────────────────────────────────
#
# From inspecting the live page ADF, Confluence storage format renders our
# markdown placeholders as:
#
#   Blockquote form (most images):
#   <blockquote local-id="..."><p local-id="...">📎 <em>[Placeholder &mdash; </em><code>filename.png</code> should be uploaded here]</p></blockquote>
#
#   Paragraph form (e.g. TL;DR section):
#   <p local-id="...">📎 <em>[Placeholder &mdash; </em><code>filename.png</code> should be uploaded here]</p>
#
# IMPORTANT: Do NOT use .*? with re.DOTALL here. When the full page body is
# searched, a greedy-enough wildcard will span across multiple placeholders and
# consume a huge section of the document in one match, wiping out all the other
# placeholders. Instead, use [^<]* and (?:<[^>]*>[^<]*)* which can only advance
# within the current tag structure and cannot cross </p> or </blockquote>.

def _placeholder_pattern(filename: str) -> re.Pattern:
    # "Tempered dot": matches any character that does NOT start a <p>, </p>,
    # <blockquote>, or </blockquote> tag. This prevents the pattern from ever
    # spanning across paragraph/blockquote boundaries — the root cause of the
    # earlier bug where one match consumed thousands of characters including
    # multiple other placeholders.
    safe = r"(?:(?!</?(?:p|blockquote)[\s>\/]).)*"
    return re.compile(
        r"(?:<blockquote[^>]*>)?"      # optional blockquote open
        r"<p[^>]*>"                    # paragraph open
        + safe +                       # safe content before "Placeholder"
        r"Placeholder"                 # literal anchor
        + safe +                       # safe content before filename
        re.escape(filename)            # exact filename
        + safe                         # safe content after filename
        + r"</p>"                      # paragraph close
        r"(?:</blockquote>)?",         # optional blockquote close
        re.IGNORECASE | re.DOTALL,     # DOTALL safe now — tempered dot limits scope
    )


def replace_placeholders(body: str, filenames: list) -> tuple:
    """Replace each placeholder with an embedded Confluence image tag."""
    count = 0
    for fn in filenames:
        pattern = _placeholder_pattern(fn)
        image_tag = (
            f'<ac:image ac:width="{IMAGE_WIDTH}">'
            f'<ri:attachment ri:filename="{fn}" />'
            f'</ac:image>'
        )
        new_body, n = pattern.subn(image_tag, body)
        if n > 0:
            body = new_body
            count += n
            print(f"  ✓ Replaced ({n}x): {fn}")
        else:
            print(f"  ~ No match found: {fn}  (already embedded, or filename mismatch)")
    return body, count


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Upload PNGs to Confluence and replace 📎 placeholders with embedded images."
    )
    parser.add_argument("--page-id", required=True, help="Confluence page ID (from the page URL)")
    parser.add_argument("--images-dir", required=True, help="Folder containing PNG files to upload")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview replacements without uploading or modifying the page",
    )
    args = parser.parse_args()

    token = load_token()
    headers = auth_headers(token)

    images_dir = Path(args.images_dir)
    if not images_dir.exists():
        print(f"Error: --images-dir '{images_dir}' does not exist.")
        sys.exit(1)

    pngs = sorted(images_dir.glob("*.png"))
    if not pngs:
        print(f"No PNG files found in {images_dir}")
        sys.exit(1)

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"\n{prefix}Found {len(pngs)} PNG(s) in {images_dir}")

    # 1. Upload attachments
    if args.dry_run:
        uploaded = [p.name for p in pngs]
        print(f"\n[DRY RUN] Would upload: {', '.join(uploaded)}\n")
    else:
        print(f"\nUploading attachments to page {args.page_id}...")
        uploaded = [p.name for p in pngs if upload_attachment(args.page_id, p, headers)]
        if not uploaded:
            print("No files uploaded successfully. Aborting.")
            sys.exit(1)

    # 2. Fetch page
    print(f"\nFetching page {args.page_id}...")
    page = get_page(args.page_id, headers)
    print(f"  Title  : {page['title']}")
    print(f"  Version: {page['version']}")

    # 3. Replace placeholders
    print("\nReplacing placeholders...")
    new_body, replaced = replace_placeholders(page["body"], uploaded)

    if replaced == 0:
        print("\nNo placeholders matched — page not updated.")
        print("Tip: run with --dry-run and check that filenames match the placeholder text exactly.")
        sys.exit(0)

    print(f"\n{replaced} placeholder(s) replaced.")

    if args.dry_run:
        print("[DRY RUN] Page not updated. Re-run without --dry-run to apply changes.")
        sys.exit(0)

    # 4. Update page
    print(f"\nUpdating page (v{page['version']} → v{page['version'] + 1})...")
    update_page(args.page_id, page["title"], page["version"], new_body, headers)


if __name__ == "__main__":
    main()