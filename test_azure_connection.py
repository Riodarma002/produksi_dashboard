"""
Test Azure AD Connection - Delegated Flow (Device Code)
Login via browser, then access OneDrive files.
"""
import sys, json, os

# Force UTF-8 and unbuffered output
os.environ["PYTHONIOENCODING"] = "utf-8"

import msal
import requests

CLIENT_ID = "6bdcbc2d-fcbf-44dd-8d6d-2c2e71acea76"
TENANT_ID = "8ffa37be-d63e-457d-9eed-f8033d43de7b"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Files.Read.All", "User.Read"]
CACHE_FILE = "token_cache.bin"

def p(msg):
    """Print with flush"""
    print(msg, flush=True)

def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache.deserialize(f.read())
    return cache

def save_cache(cache):
    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as f:
            f.write(cache.serialize())

def get_token():
    cache = load_cache()
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )
    
    # Try cached token first
    accounts = app.get_accounts()
    if accounts:
        p(f"[CACHE] Found: {accounts[0]['username']}")
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            save_cache(cache)
            return result["access_token"]
    
    # Device code flow
    p("[LOGIN] Starting device code login...")
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        p(f"[FAIL] Device flow error: {json.dumps(flow, indent=2)}")
        return None
    
    p("")
    p("=" * 50)
    p(flow["message"])
    p("=" * 50)
    p("")
    p("Waiting for login...")
    
    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        save_cache(cache)
        return result["access_token"]
    else:
        p(f"[FAIL] {result.get('error')}")
        p(f"  {result.get('error_description')}")
        return None

# === MAIN ===
p("AZURE AD DELEGATED FLOW TEST")
p("-" * 40)

# 1. AUTH
p("\n1. Authentication")
token = get_token()
if not token:
    p("[FAIL] No token")
    sys.exit(1)

p("[OK] Token acquired!")
headers = {"Authorization": f"Bearer {token}"}

# 2. USER INFO
p("\n2. User Info")
r = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
if r.status_code == 200:
    me = r.json()
    p(f"[OK] {me.get('displayName')} ({me.get('mail', me.get('userPrincipalName', '?'))})")
else:
    p(f"[WARN] {r.status_code}: {r.text[:150]}")

# 3. ONEDRIVE ROOT
p("\n3. OneDrive Root")
r = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/children?$top=20", headers=headers)
if r.status_code == 200:
    items = r.json().get("value", [])
    p(f"[OK] {len(items)} items:")
    for it in items:
        tp = "[DIR ]" if "folder" in it else "[FILE]"
        p(f"  {tp} {it.get('name')}")
else:
    p(f"[FAIL] {r.status_code}: {r.text[:200]}")

# 4. EXCEL FILES
p("\n4. Excel Files")
r = requests.get("https://graph.microsoft.com/v1.0/me/drive/root/search(q='.xlsx')?$top=15", headers=headers)
if r.status_code == 200:
    items = r.json().get("value", [])
    p(f"[OK] {len(items)} Excel files:")
    for it in items:
        path = it.get("parentReference", {}).get("path", "").replace("/drive/root:", "")
        p(f"  {path}/{it.get('name')}")
else:
    p(f"[WARN] {r.status_code}: {r.text[:150]}")

p("\n" + "-" * 40)
p("DONE")
