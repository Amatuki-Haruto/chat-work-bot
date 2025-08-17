# Chatwork日付変更bot

Chatworkで毎日の日付変更時に自動的に通知を送信するbotです。

## 機能

- 🕛 毎日00:00（デフォルト）に日付変更通知を自動送信
- 📅 現在の日付を含むメッセージを送信
- ⚙️ カスタマイズ可能な通知時刻とメッセージ
- 🧪 Chatwork上で特定の人が「テスト時報」と送信するとテスト実行
- 🌐 Webhook方式でリアルタイム通知（遅延なし）
- 📊 ヘルスチェックエンドポイント
- 🚀 Railway対応（自動デプロイ）

## セットアップ

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、以下の内容を設定してください：

```bash
# Chatwork API設定
CHATWORK_API_TOKEN=your_chatwork_api_token_here
CHATWORK_ROOM_ID=your_chatwork_room_id_here

# テスト時報実行権限者設定
TEST_NOTIFICATION_USER_ID=your_account_id_here

# Webhook設定
WEBHOOK_ENABLED=true
WEBHOOK_PORT=8080
WEBHOOK_SECRET=your_webhook_secret_here

# 通知時刻設定（24時間形式）
NOTIFICATION_TIME=00:00
```

### 3. Chatwork API設定

1. Chatworkにログインし、API設定ページにアクセス
2. APIトークンを生成
3. 通知を送信したいルームのIDを取得
4. テスト時報を実行したい人のアカウントIDを取得

### 4. Webhook設定

#### Railwayでの本番運用（推奨）
1. GitHubにコードをプッシュ
2. Railwayでプロジェクトを作成
3. 環境変数を設定
4. 自動デプロイ完了後、以下のURLが生成されます：
   ```
   https://your-app-name.railway.app/webhook

   
## Railwayでのデプロイ

### 1. GitHubにプッシュ
```bash
git add .
git commit -m "Webhook機能追加"
git push origin main
```

### 2. Railwayでプロジェクト作成
- [Railway](https://railway.app/)にログイン
- "New Project" → "Deploy from GitHub repo"
- リポジトリを選択

### 3. 環境変数設定
Railwayの環境変数で以下を設定：
```
CHATWORK_API_TOKEN=your_token
CHATWORK_ROOM_ID=your_room_id
TEST_NOTIFICATION_USER_ID=your_user_id
WEBHOOK_ENABLED=true
WEBHOOK_SECRET=your_secret
NOTIFICATION_TIME=00:00
```

**注意**: Railwayでは`PORT`環境変数が自動で設定されるため、`WEBHOOK_PORT`は不要です。

### 4. デプロイ完了
- 自動でビルドとデプロイが完了
- 生成されたURLをChatworkのWebhook設定に設定

## 使用方法

### 基本的な実行

```bash
python main.py
```

### テスト時報の実行

1. botを起動
2. Chatworkの指定されたルームで、設定した権限者が「テスト時報」とメッセージを送信
3. botがWebhookで即座にテスト時報を実行（遅延なし）

### ヘルスチェック

Webhookサーバーの状態を確認：

```bash
# ローカル
curl http://localhost:8080/health

# Railway
curl https://your-app-name.railway.app/health
```

## 動作の流れ

1. bot起動時に設定を確認
2. Webhookサーバーを開始（Railwayでは自動でポート設定）
3. 毎日指定時刻に自動日付変更通知
4. ChatworkからWebhookでリアルタイム通知を受信
5. 特定の人が「テスト時報」と送信すると即座にテスト実行

## Webhookの利点

- ⚡ **遅延なし**: メッセージ送信と同時に処理
- 🚀 **高効率**: APIポーリングが不要
- 💰 **低コスト**: サーバーリソース使用量が最小
- 🔒 **セキュア**: 設定可能なシークレットキー
- 🌐 **自動HTTPS**: RailwayでSSL証明書が自動設定

## 注意事項

- Chatwork APIトークンは機密情報です。`.env`ファイルをGitにコミットしないでください
- ルームIDは数値で指定してください
- 通知時刻は24時間形式（例：00:00、09:00）で指定してください
- テスト時報実行権限者のアカウントIDは数値で指定してください
- Webhook URLは外部からアクセス可能である必要があります
- Railwayでは`PORT`環境変数が自動で設定されます
- 本番環境では適切なセキュリティ設定を行ってください

## トラブルシューティング

### よくあるエラー

- **APIトークンエラー**: トークンが正しく設定されているか確認
- **ルームIDエラー**: ルームIDが正しい数値か確認
- **権限エラー**: 指定したルームにメッセージを送信する権限があるか確認
- **テスト時報実行権限者IDエラー**: アカウントIDが正しく設定されているか確認
- **Webhook接続エラー**: ポートが開放されているか、URLが正しく設定されているか確認

### Webhook設定の確認

1. Railwayでデプロイが完了しているか確認
2. 生成されたURLが正しくChatworkに設定されているか確認
3. ヘルスチェックエンドポイントにアクセスできるか確認
4. Railwayのログでエラーがないか確認

### Railway特有の確認事項

1. 環境変数が正しく設定されているか確認
2. ビルドログでエラーがないか確認
3. デプロイログでWebhookサーバーが起動しているか確認

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。
