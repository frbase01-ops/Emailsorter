#!/usr/bin/env python3
"""
Email Sorter — MX & Autodiscover Classifier
-------------------------------------------
Sorts email lists by their hosting provider using DNS lookups.

Detects:
- Microsoft 365 Direct Tenant
- Microsoft 365 Partner Tenant (partners.outlook.com)
- Hosted Exchange (OWA)
- Google Workspace
- Zoho Mail
- Other/Unknown

Author: Joah + GPT-5
License: MIT
"""

import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# === CONFIG ===
INPUT_FILE = Path("emails.txt")
OUTPUT_FILE = Path("results.csv")
MAX_THREADS = 30  # Increase for faster processing


def run_cmd(cmd):
    """Execute a shell command and return decoded output."""
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return ""


def get_mx(domain):
    """Return MX records for a given domain."""
    result = run_cmd(f"nslookup -type=mx {domain}")
    return re.findall(r"mail exchanger = (.+)", result)


def get_autodiscover(domain):
    """Return autodiscover CNAME records."""
    result = run_cmd(f"nslookup -type=cname autodiscover.{domain}")
    return re.findall(r"canonical name = (.+)", result)


def classify(mx_records, autodiscover_records):
    """Classify provider based on MX and autodiscover patterns."""
    mx_str = " ".join(mx_records).lower()
    auto_str = " ".join(autodiscover_records).lower()

    if "partners.outlook.com" in mx_str or "partner.outlook.com" in auto_str:
        return "Microsoft 365 Partner Tenant"
    elif "mail.protection.outlook.com" in mx_str or "autodiscover.outlook.com" in auto_str:
        return "Microsoft 365 Direct Tenant"
    elif any(x in mx_str for x in [
        "serverdata.net", "emailsrvr.com", "appriver.com",
        "sherwebcloud.com", "hostedemail.com", "hostway.com", "exchange", "exch"
    ]) or any(x in auto_str for x in [
        "serverdata.net", "emailsrvr.com", "appriver.com",
        "sherwebcloud.com", "exchange"
    ]):
        return "Hosted Exchange (OWA)"
    elif "google.com" in mx_str:
        return "Google Workspace"
    elif "zoho.com" in mx_str:
        return "Zoho Mail"
    else:
        return "Other / Unknown"


def process_email(email):
    """Perform lookups and classification for one email."""
    email = email.strip()
    if not email or "@" not in email:
        return None

    domain = email.split("@")[1]
    mx_records = get_mx(domain)
    autodiscover_records = get_autodiscover(domain)
    category = classify(mx_records, autodiscover_records)

    return {
        "email": email,
        "mx": " ".join(mx_records),
        "autodiscover": " ".join(autodiscover_records),
        "category": category,
    }


def main():
    print("\n🔍 Sorting emails by MX / Autodiscover provider...\n")
    print(f"{'Email':40} | {'Classification'}")
    print("-" * 80)

    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    with open(INPUT_FILE) as f:
        emails = [line.strip() for line in f if "@" in line]

    results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(process_email, email): email for email in emails}
        for future in as_completed(futures):
            result = future.result()
            if result:
                print(f"{result['email']:40} | {result['category']}")
                results.append(result)

    with open(OUTPUT_FILE, "w") as f:
        f.write("Email,Classification,MX,Autodiscover\n")
        for r in results:
            f.write(f"{r['email']},{r['category']},{r['mx']},{r['autodiscover']}\n")


    print(f"\n✅ Done! Results saved to: {OUTPUT_FILE}")
    print("💡 Tip: Open results.csv and filter by 'Microsoft 365 Partner Tenant' or 'Hosted Exchange (OWA)'.\n")


if __name__ == "__main__":
    main()
