# Email Sorter (MX & Autodiscover Analyzer)

A fast, multithreaded Python tool to detect the **email hosting provider** for large lists.

It identifies:
- Microsoft 365 Direct Tenants (`mail.protection.outlook.com`)
- Microsoft 365 Partner Tenants (`partners.outlook.com`)
- Hosted Exchange (OWA)
- Google Workspace
- Zoho Mail
- Others

## 🧰 Requirements
- CentOS 7, Ubuntu, or any Linux system
- Python 3.6+
- DNS tools: `nslookup` (from `bind-utils`)

Install prerequisites:
```bash
yum install -y bind-utils python3
```

## ⚙️ Usage
1. Place your email list in `emails.txt` (one per line)
2. Run:
```bash
python3 sort_emails.py
```
3. View results in:
```
results.csv
```

## 💡 Output Example
| Email | Classification |
|--------|----------------|
| john@company.com | Microsoft 365 Direct Tenant |
| mary@client.com | Hosted Exchange (OWA) |
| info@partnerco.com | Microsoft 365 Partner Tenant |

## ⚡ Performance
- Uses Python’s `ThreadPoolExecutor` for multithreading
- Default: 30 concurrent DNS lookups (change in `MAX_THREADS`)

## 📜 License
MIT License © 2025 Joah + GPT-5
