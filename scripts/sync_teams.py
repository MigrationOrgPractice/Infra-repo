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

# 差分抽出関数（git diff利用）
def get_file_diff_users(filepath):
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rel_path = os.path.relpath(filepath, repo_root)
    # HEAD~1が存在しない場合（初回コミット）は全ユーザー追加
    result = subprocess.run([
        "git", "rev-parse", "HEAD~1"
    ], capture_output=True, text=True)
    if result.returncode != 0:
        # ファイルの全ユーザーを追加
        with open(filepath, "r") as f:
            added = set(line.strip() for line in f if line.strip())
        removed = set()
        print(f"初回コミット: 全ユーザー追加対象: {added}")
        return added, removed
    # mainブランチとの差分抽出
    result = subprocess.run([
        "git", "diff", "origin/main", "HEAD", "--", rel_path
    ], capture_output=True, text=True)
    added = set()
    removed = set()
    if result.returncode == 0:
        for line in result.stdout.splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                user = line[1:].strip()
                if user:
                    added.add(user)
            elif line.startswith("-") and not line.startswith("---"):
                user = line[1:].strip()
                if user:
                    removed.add(user)
    else:
        print(f"git diff failed for {rel_path}: {result.stderr}")
    return added, removed

# メイン処理
for filename in os.listdir(TEAM_DIR):
    if filename.endswith(".txt"):
        team_name = os.path.splitext(filename)[0]
        team_slug = get_team_slug(team_name)
        filepath = os.path.join(TEAM_DIR, filename)

        # 差分ユーザーを取得
        added_users, removed_users = get_file_diff_users(filepath)

        print(f"added_users: {added_users}")
        print(f"removed_users: {removed_users}")

        print(f"🔄 Syncing team: {team_name} ({team_slug})")
        for user in added_users:
            add_member(ORG_NAME, team_slug, user)
        for user in removed_users:
            remove_member(ORG_NAME, team_slug, user)
        print(f"✅ Completed syncing team: {team_name}\n")
