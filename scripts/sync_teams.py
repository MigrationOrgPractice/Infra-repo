import os
import subprocess
import requests

# 環境変数からトークンと組織名を取得
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
ORG_NAME = os.getenv("ORG_NAME")

# GitHub APIの基本設定
API_BASE = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

TEAM_DIR = "teams"

# チーム名からslugを生成
def get_team_slug(team_name):
    return team_name.lower().replace(" ", "-")

# ユーザーをチームに追加
def add_member(org, team_slug, username):
    url = f"{API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
    response = requests.put(url, headers=HEADERS)
    if response.status_code in [200, 201]:
        print(f"✅ Added {username} to {team_slug}")
    else:
        print(f"❌ Failed to add {username}: {response.text}")

# ユーザーをチームから削除
def remove_member(org, team_slug, username):
    url = f"{API_BASE}/orgs/{org}/teams/{team_slug}/memberships/{username}"
    response = requests.delete(url, headers=HEADERS)
    if response.status_code == 204:
        print(f"🗑️ Removed {username} from {team_slug}")
    else:
        print(f"❌ Failed to remove {username}: {response.text}")

# 前回コミットのファイル内容を取得
def get_previous_file_content(filepath):
    try:
        # git showにはリポジトリルートからの相対パスが必要
        repo_root = os.path.abspath(os.getcwd())
        rel_path = os.path.relpath(filepath, repo_root)
        result = subprocess.run(["git", "show", f"HEAD~1:{rel_path}"], capture_output=True, text=True)
        if result.returncode == 0:
            return set(line.strip() for line in result.stdout.splitlines() if line.strip())
        else:
            print(f"git show failed for {rel_path}: {result.stderr}")
            return set()
    except Exception as e:
        print(f"Error retrieving previous version of {filepath}: {e}")
        return set()

# メイン処理
for filename in os.listdir(TEAM_DIR):
    if filename.endswith(".txt"):
        team_name = os.path.splitext(filename)[0]
        team_slug = get_team_slug(team_name)
        filepath = os.path.join(TEAM_DIR, filename)

        # 現在のユーザーリスト
        with open(filepath, "r") as f:
            current_users = set(line.strip() for line in f if line.strip())

        # 前回のユーザーリスト
        previous_users = get_previous_file_content(filepath)

        # 差分を計算
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
        print(f"✅ Completed syncing team: {team_name}\n")