"""
OneDrive Sharing Link → Excel Download
Converts OneDrive/SharePoint sharing links to direct download URLs.
No API credentials or admin consent required.
"""
import io
import base64
import requests
import pandas as pd
import streamlit as st


def _convert_share_link_to_download_url(share_link: str) -> str:
    """
    Convert a OneDrive/SharePoint sharing link to a direct download URL.
    
    Uses the official base64 encoding method from Microsoft:
    https://learn.microsoft.com/en-us/graph/api/shares-get
    
    This works WITHOUT authentication for links shared as "Anyone with the link".
    For org-only links, it returns the URL but may need auth cookies from browser.
    """
    # Method 1: Direct download manipulation (works for most OneDrive links)
    if "1drv.ms" in share_link or "onedrive.live.com" in share_link:
        # Replace share indicator with download
        download_url = share_link.replace("redir?", "download?")
        if "download?" not in download_url:
            download_url = share_link + "&download=1"
        return download_url
    
    if "sharepoint.com" in share_link:
        # SharePoint: change sharing link to download
        download_url = share_link.replace(":x:/", ":x:/").split("?")[0]
        download_url += "?download=1"
        return download_url
    
    # Method 2: Microsoft Graph shares API (for encoded links)
    # Encode the sharing URL using base64
    encoded = base64.urlsafe_b64encode(share_link.encode()).decode()
    encoded = "u!" + encoded.rstrip("=")
    
    api_url = f"https://api.onedrive.com/v1.0/shares/{encoded}/root/content"
    return api_url


def download_excel_from_link(
    share_link: str,
    sheet_name: str | int | None = 0,
    timeout: int = 30,
) -> pd.DataFrame | None:
    """
    Download an Excel file from a OneDrive sharing link and return as DataFrame.
    
    Args:
        share_link: OneDrive/SharePoint sharing link
        sheet_name: Sheet to read (name or index, default=first sheet)
        timeout: Request timeout in seconds
    
    Returns:
        DataFrame or None if failed
    """
    if not share_link or not share_link.strip():
        return None
    
    download_url = _convert_share_link_to_download_url(share_link.strip())
    
    try:
        response = requests.get(
            download_url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        response.raise_for_status()
        
        # Parse Excel bytes
        excel_bytes = io.BytesIO(response.content)
        df = pd.read_excel(excel_bytes, sheet_name=sheet_name, engine="openpyxl")
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"Download failed: {e}")
        return None
    except Exception as e:
        st.error(f"Excel parse error: {e}")
        return None


def download_excel_all_sheets(
    share_link: str,
    timeout: int = 30,
) -> dict[str, pd.DataFrame] | None:
    """
    Download Excel and return ALL sheets as dict of DataFrames.
    """
    if not share_link or not share_link.strip():
        return None
        
    download_url = _convert_share_link_to_download_url(share_link.strip())
    
    try:
        response = requests.get(
            download_url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        )
        response.raise_for_status()
        
        excel_bytes = io.BytesIO(response.content)
        sheets = pd.read_excel(excel_bytes, sheet_name=None, engine="openpyxl")
        return sheets
        
    except Exception as e:
        st.error(f"Download error: {e}")
        return None


def read_local_excel(
    file_path: str,
    sheet_name: str | int | None = 0,
) -> pd.DataFrame | None:
    """
    Read Excel from local path (e.g., OneDrive sync folder).
    Fallback method when sharing links don't work.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"Local file read error: {e}")
        return None
