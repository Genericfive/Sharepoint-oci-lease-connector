SharePoint Lease Connector

A small Python connector that provides read-only access to lease documents stored in SharePoint.

The connector uses Microsoft Entra authentication and Microsoft Graph to:

Browse the authorized SharePoint folder
List available files
Let the user select a file
Read the selected document into memory
Avoid creating a local copy of the lease
Avoid copying lease documents into OCI Object Storage
Flow

SharePoint
→ Microsoft Graph
→ SharePoint Lease Connector
→ Select Document
→ Read Selected File in Memory
→ Pass to Lease-AI

Setup
1. Clone the repository
git clone https://github.com/Genericfive/sharepoint-lease-connector.git
cd sharepoint-lease-connector
2. Create .env

Add the approved Microsoft / SharePoint configuration:

MS_AUTH_MODE=device_code
MS_TENANT_ID=<tenant-id>
MS_CLIENT_ID=<client-id>
ONEDRIVE_SHARED_FOLDER_URL=<sharepoint-folder-url>
MS_TOKEN_CACHE_FILE=.auth/msal_token_cache.json
LOG_LEVEL=INFO

Do not commit .env to GitHub.

3. Install dependencies
python -m pip install -r requirements.txt
4. Run
python main.py

The connector will:

Authenticate the user
Display the SharePoint files
Ask for a file number
Read only the selected document into memory

Example:

Select file number (or Q to quit): 1

Selected document:
abc.lease.pdf

SUCCESS
Document is currently held in memory only.
No local PDF was created.
Main Files
main.py — runs the SharePoint browser and file selection
microsoft_auth.py — Microsoft Entra authentication
onedrive_client.py — read-only SharePoint / OneDrive access
config.py — loads environment settings
models.py — file metadata model

Security
SharePoint remains the source of truth
Microsoft Graph access is read-only
Lease files are not copied into OCI Object Storage
Selected files are not permanently saved to the local device
.env and authentication data are excluded from GitHub

Next Step
Integrate the selected in-memory document with the Lease-AI processing pipeline.