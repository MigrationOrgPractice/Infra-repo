# Infra-repo

このプロジェクトは、GitHub Organizationのチームメンバー管理を自動化するためのリポジトリです。`teams/`ディレクトリ内のテキストファイルでチームメンバーを管理し、GitHub ActionsとPythonスクリプトで差分を自動的にGitHubチームへ反映します。

## 役割
- `teams/`配下の各`*.txt`ファイルにGitHubユーザー名を記載し、チームごとのメンバーリストを管理
- 変更がmainブランチにマージされると、GitHub Actionsが自動で差分を検出し、追加・削除をGitHubチームに反映
- スクリプトは`/scripts/sync_teams.py`です

## 前提条件
- 管理対象のGitHub Organizationの管理者権限を持つPersonal Access Token (PAT)
- Organization Secretsに以下を登録済みであること
    - `ORG_ADMIN_PAT`: admin:org権限を持つPAT
    - `ORG_NAME`: Organization名
- Python 3.10以上（ローカルでスクリプトを手動実行する場合のみ。GitHub Actions上では自動セットアップされます）
- **対象となるGitHubチームは事前にOrganization上で作成しておく必要があります**

## GitHub Actionsの設定
- `.github/workflows/sync-teams.yml`で自動同期を実現
- mainブランチへのpush（マージ）時、`teams/*.txt`の変更がトリガー
- Actionsのcheckoutステップで`fetch-depth: 0`を指定し、全履歴を取得
- `ORG_ADMIN_PAT`と`ORG_NAME`はSecretsから環境変数としてスクリプトに渡されます

## 使い方
1. `teams/`配下の`<team名>.txt`にGitHubユーザー名（1行1名）を記載
2. ファイルを編集し、mainブランチにマージ
3. Actionsが自動で差分を検出し、GitHubチームに追加・削除を反映

## 注意事項
- 初回コミット時は全ユーザーが追加されます
- 2回目以降はmainブランチとの差分のみが反映されます
- チーム名はGitHubのteam slug（小文字・スペースはハイフン）に変換されます
- PATやSecretsの管理には十分ご注意ください

---

ご不明点があればOrganization管理者までご連絡ください。