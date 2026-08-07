# SharePoint to OCI Connector

This connector reads lease files from SharePoint and copies new or updated files into OCI Object Storage.

Flow:

SharePoint → OCI Object Storage → Lease-AI

## Setup

Open PowerShell in the project folder.

Create a virtual environment:
py -3.12 -m venv .venv


Install dependencies:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

Ask for  Configure .env Setup

Run:
.\.venv\Scripts\python.exe main.py



'''End Goal'''

SharePoint
    ↓
Lease OneDrive OCI Connector
    ↓
OCI Object Storage
    ↓
Lease-AI
    ↓
Canonical JSON
    ↓
Processed JSON
    ↓
Excel / future PeopleSoft integration

Lease-AI should read its input lease from OCI Object Storage rather than connecting directly to SharePoint.