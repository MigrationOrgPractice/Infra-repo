import os
import subprocess
import requests

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
    if response.status_code in [200, 201]:
        print(f"✅ Added {username} to {team_slug}")
    else:
        print(f"❌ Failed to add {username}: {response.text}")

def remove_member(org, team_slug, username):
    url = f"{API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        print(f"🗑️ Removed {username} from {team_slug}")
    else:
        print(f"❌ Failed to remove {username}: {response.text}")

def get_previous_file_content(filepath):
    try:
        result = subprocess.run(["git", "show", f"HEAD~1:{filepath}"], capture_output=True, text=True)
        if result.returncode == 0:
            return set(line.strip() for line in result.stdout.splitlines() if line.strip())
        else:
            return set()
    except Exception as e:
        print(f"Error retrieving previous version of {filepath}: {e}")
        return set()

def get_changed_team_files():
    result = subprocess.run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], capture_output=True, text=True)
    changed_files = result.stdout.splitlines()
    return [f for f in changed_files if f.startswith(TEAM_DIR + "/") and f.endswith(".txt")]

# 差分のあるファイルだけ処理
changed_team_files = get_changed_team_files()

for filepath in changed_team_files:
    filename = os.path.basename(filepath)
    team_name = os.path.splitext(filename)[0]
    team_slug = get_team_slug(team_name)

    with open(filepath, "r") as f:
        current_users = set(line.strip() for line in f if line.strip())

    previous_users = get_previous_file_content(filepath)

    added_users = current_users - previous_users
    removed_users = previous_users - current_users

    print(f"current_users: {current_users}")
    print(f"previous_users: {previous_users}")
    print(f"added_users: {added_users}")
    print(f"removed_users: {removed_users}")

    print(f"🔄 Syncing team: {team_name} ({team_slug})")
    for user in added_users:
        add_member(ORG_NAME, team_slug, user)
    for user in removed_users:
        remove_member(ORG_NAME, team_slug, user)
