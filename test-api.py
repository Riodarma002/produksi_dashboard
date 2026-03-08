import msal
import requests

# Config
CLIENT_ID = "6bdcbc2d-fcbf-44dd-8d6d-2c2e71acea76"
CLIENT_SECRET = "aa4dc725-27ed-4dae-8899-cce29ac01897"  
TENANT_ID = "8ffa37be-d63e-457d-9eed-f8033d43de7b"

# Karena Delegated, kita pakai Device Code Flow (paling mudah untuk testing)
app = msal.PublicClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}"
)

SCOPES = ["Files.ReadWrite.All", "User.Read"]

# Step 1: Minta device code
flow = app.initiate_device_flow(scopes=SCOPES)
print(flow["message"])  
# Akan muncul: "Go to https://microsoft.com/devicelogin and enter code XXXXXXXX"

# Step 2: Tunggu user login
input("Setelah login, tekan Enter...")
result = app.acquire_token_by_device_flow(flow)

# Step 3: Cek token
if "access_token" in result:
    print("✅ Token berhasil didapat!")
    
    # Step 4: Test panggil OneDrive
    token = result["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Cek info user
    me = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers).json()
    print(f"Login sebagai: {me.get('displayName')} ({me.get('mail')})")
    
    # List file di root OneDrive
    files = requests.get(
        "https://graph.microsoft.com/v1.0/me/drive/root/children",
        headers=headers
    ).json()
    
    print("\n📂 File di OneDrive root:")
    for item in files.get("value", []):
        icon = "📁" if "folder" in item else "📄"
        print(f"  {icon} {item['name']}")
else:
    print("❌ Gagal:", result.get("error_description"))