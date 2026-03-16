"""
Azure API — Microsoft Graph Integration for Excel Data
Uses Client Credentials flow (Application Permissions) for background syncing.
"""
import requests
import msal
import io
import pandas as pd
import streamlit as st
from typing import Optional

from config import AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, CACHE_TTL_SECONDS

AUTHORITY = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

def get_access_token() -> Optional[str]:
    """Get Azure AD access token using Client Credentials flow."""
    app = msal.ConfidentialClientApplication(
        AZURE_CLIENT_ID,
        authority=AUTHORITY,
        client_credential=AZURE_CLIENT_SECRET,
    )
    
    # Try getting token from cache first
    result = app.acquire_token_silent(SCOPES, account=None)
    
    if not result:
        # Fetch new token
        result = app.acquire_token_for_client(scopes=SCOPES)
        
    if "access_token" in result:
        return result["access_token"]
    
    st.error(f"Azure Auth Error: {result.get('error_description', result.get('error'))}")
    return None

def download_excel_from_graph(url_or_id: str) -> Optional[dict[str, pd.DataFrame]]:
    """
    Download Excel workbook from Graph API and return all sheets.
    url_or_id can be a direct Graph content URL or a File ID.
    """
    token = get_access_token()
    if not token:
        return None
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # If it's a file ID, construct the Graph URL for content
    # For company-shared files, we usually use /sites/{site-id}/drive/items/{item-id}/content
    # or /users/{user-id}/drive/items/{item-id}/content
    # Since we have the share link, we can use the 'shares' API to get the content directly
    
    # Helper to convert share link to graph download URL
    import base64
    encoded_url = base64.urlsafe_b64encode(url_or_id.encode()).decode().rstrip("=")
    api_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded_url}/driveItem/content"
    
    try:
        response = requests.get(api_url, headers=headers, timeout=60)
        response.raise_for_status()
        
        excel_bytes = io.BytesIO(response.content)
        sheets = pd.read_excel(excel_bytes, sheet_name=None, engine="openpyxl")
        return sheets
    except Exception as e:
        st.error(f"Azure Download Error: {e}")
        return None
