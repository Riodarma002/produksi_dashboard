"""
Verification Script for Azure API Integration
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

import msal
from typing import Optional
from backend.azure_api import get_access_token, download_excel_from_graph
from config import ONEDRIVE_LINKS, AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET

AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

def get_access_token_debug() -> Optional[str]:
    """Get Azure AD access token and print full result on error."""
    app = msal.ConfidentialClientApplication(
        AZURE_CLIENT_ID,
        authority=AUTHORITY,
        client_credential=AZURE_CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=SCOPES)
    if "access_token" in result:
        return result["access_token"]
    print(f"DEBUG AUTH RESULT: {result}")
    return None

def verify():
    print("--- AZURE INTEGRATION VERIFICATION ---")
    
    # 1. Test Token
    print("\n1. Testing Auth Token...")
    token = get_access_token_debug()
    if token:
        print("[OK] Access token acquired successfully!")
    else:
        print("[FAIL] Could not acquire access token.")
        return

    # 2. Test Data Fetch (one file)
    print("\n2. Testing Data Fetch (db_hourly)...")
    url = ONEDRIVE_LINKS["db_hourly"]
    sheets = download_excel_from_graph(url)
    
    if sheets:
        print(f"[OK] Successfully fetched workbook via Azure API!")
        print(f"     Sheets found: {', '.join(sheets.keys())}")
    else:
        print("[FAIL] Could not download data via Azure API.")

if __name__ == "__main__":
    verify()
