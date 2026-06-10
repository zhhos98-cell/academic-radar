import requests

ACTOR = "karl-haohaozhang.bsky.social"

cursor = None
handles = []

while True:
    params = {"actor": ACTOR, "limit": 100}
    if cursor:
        params["cursor"] = cursor

    r = requests.get(
        "https://public.api.bsky.app/xrpc/app.bsky.graph.getFollows",
        params=params,
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()

    for f in data.get("follows", []):
        handle = f.get("handle", "")
        display = f.get("displayName", "")
        desc = f.get("description", "").replace("\n", " ")
        handles.append((handle, display, desc[:200]))

    cursor = data.get("cursor")
    if not cursor:
        break

with open("bsky_accounts.txt", "w", encoding="utf-8") as out:
    for handle, display, desc in handles:
        out.write(f"{handle}\t{display}\t{desc}\n")

print(f"Exported {len(handles)} follows")
print("BEGIN_BSKY_ACCOUNTS")
for handle, display, desc in handles:
    print(f"{handle}\t{display}\t{desc}")
print("END_BSKY_ACCOUNTS")
