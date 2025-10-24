
import os
import requests
import subprocess

# 環境変数からトークンと組織名を取得
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("ORG_NAME")

API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

TEAM_DIR = "teams"

def get_team_slug(team_name):
    return team_name.lower().replace(" ", "-")

def add_member(org, team_slug, username):
    url = f"{API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
    response = requests.put(url, headers=HEADERS)
    print(f"✅ Added {username} to {team_slug}" if response.ok else f"❌ Failed to add {username}: {response.text}")

def remove_member(org, team_slug, username):
    url = f"{API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
    response = requests.delete(url, headers=HEADERS)
    print(f"🗑️ Removed {username} from {team_slug}" if response.status_code == 204 else f"❌ Failed to remove {username}: {response.text}")

def get_previous_file_content(filepath):
    try:
        result = subprocess.run(["git", "show", f"HEAD~1:{filepath}"], capture_output=True, text=True)
        return set(line.strip() for line in result.stdout.splitlines() if line.strip())
    except Exception as e:
        print(f"Error retrieving previous version of {filepath}: {e}")
        return set()

# メイン処理
for filename in os.listdir(TEAM_DIR):
    if filename.endswith(".txt"):
        team_name = os.path.splitext(filename)[0]
        team_slug = get_team_slug(team_name)
        filepath = os.path.join(TEAM_DIR, filename)

        with open(filepath, "r") as f:
            current_users = set(line.strip() for line in f if line.strip())

        previous_users = get_previous_file_content(filepath)

        added_users = current_users - previous_users
        removed_users = previous_users - current_users

        print(f"🔄 Syncing team: {team_name} ({team_slug})")
        for user in added_users:
            add_member(ORG_NAME, team_slug, user)
        for user in removed_users:
            remove_member(ORG_NAME, team_slug, user)
