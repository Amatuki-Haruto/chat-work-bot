import requests
import schedule
import time
import threading
import json
from datetime import datetime
from flask import Flask, request, jsonify
from config import Config

class ChatworkDateChangeBot:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'X-ChatWorkToken': self.config.CHATWORK_API_TOKEN
        })
        self.running = False
        
        # Flaskアプリの初期化
        if self.config.WEBHOOK_ENABLED:
            self.app = Flask(__name__)
            self.setup_webhook_routes()
    
    def setup_webhook_routes(self):
        """Webhookルートの設定"""
        @self.app.route('/webhook', methods=['POST'])
        def webhook_handler():
            return self.handle_webhook(request)
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
    
    def handle_webhook(self, request_data):
        """Webhookからの通知を処理"""
        try:
            # リクエストデータを取得
            data = request_data.get_json()
            
            print(f"🔍 Webhook受信開始")
            print(f"📨 リクエストヘッダー: {dict(request_data.headers)}")
            print(f"📨 リクエストボディ: {data}")
            
            if not data:
                print("❌ Webhookデータが空です")
                return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
            # ChatworkのWebhookデータ形式に対応
            message_body = None
            account_id = None
            account_name = None
            
            # 形式1: 標準的なメッセージ形式
            if 'message' in data:
                message_data = data['message']
                print(f"📝 メッセージデータ: {message_data}")
                
                if 'body' in message_data and 'account' in message_data:
                    message_body = message_data['body'].strip()
                    account_id = str(message_data['account']['account_id'])
                    account_name = message_data['account']['name']
            
            # 形式2: Chatwork特有の形式（`webhook_event_type`）
            elif 'webhook_event_type' in data and data['webhook_event_type'] == 'message_created':
                print(f"🔍 Chatwork特有の形式を検出: {data['webhook_event_type']}")
                message_data = data.get('webhook_event', {})
                print(f"📝 webhook_eventキーの内容: {message_data}")
                print(f"📝 webhook_eventの型: {type(message_data)}")
                print(f"📝 webhook_eventのキー: {list(message_data.keys()) if message_data else 'None'}")
                
                if 'body' in message_data and 'account_id' in message_data:
                    message_body = message_data['body'].strip()
                    account_id = str(message_data['account_id'])
                    account_name = f"User_{account_id}"  # 名前が含まれていない場合はIDを使用
                    print(f"✅ データ取得成功:")
                    print(f"   - message_body: {message_body}")
                    print(f"   - account_id: {account_id}")
                    print(f"   - account_name: {account_name}")
                else:
                    print(f"❌ webhook_event内に必要なデータがありません:")
                    print(f"   - body: {'body' in message_data}")
                    print(f"   - account_id: {'account_id' in message_data}")
                    print(f"   - 利用可能なキー: {list(message_data.keys()) if message_data else 'None'}")
            
            # 形式3: 直接的なメッセージ形式
            elif 'body' in data and 'account' in data:
                message_body = data['body'].strip()
                account_id = str(data['account']['account_id'])
                account_name = data['account']['name']
                print(f"📝 直接メッセージデータ: {data}")
            
            # データが取得できたかチェック
            if message_body and account_id and account_name:
                print(f"📨 Webhook受信: {account_name} -> {message_body}")
                print(f"👤 アカウントID: {account_id}")
                print(f"🔑 設定された権限者ID: {self.config.TEST_NOTIFICATION_USER_ID}")
                print(f"✅ ID一致: {account_id == self.config.TEST_NOTIFICATION_USER_ID}")
                
                # テスト時報コマンドをチェック
                if (message_body == "テスト時報" and 
                    account_id == self.config.TEST_NOTIFICATION_USER_ID):
                    
                    print(f"🧪 ユーザー {account_name} からテスト時報コマンドを受信しました")
                    # 別スレッドでテスト時報を実行
                    threading.Thread(target=self.test_notification, daemon=True).start()
                else:
                    print(f"❌ コマンドチェック失敗:")
                    print(f"   - メッセージ内容: '{message_body}' == 'テスト時報' → {message_body == 'テスト時報'}")
                    print(f"   - アカウントID: '{account_id}' == '{self.config.TEST_NOTIFICATION_USER_ID}' → {account_id == self.config.TEST_NOTIFICATION_USER_ID}")
            else:
                print(f"❌ メッセージデータの形式が不正:")
                print(f"   - message_body: {message_body}")
                print(f"   - account_id: {account_id}")
                print(f"   - account_name: {account_name}")
                print(f"   - 利用可能なキー: {list(data.keys()) if data else 'None'}")
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            print(f"❌ Webhook処理エラー: {str(e)}")
            import traceback
            print(f"📋 スタックトレース: {traceback.format_exc()}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    def send_message(self, message):
        """Chatworkの指定されたルームにメッセージを送信"""
        try:
            url = f"{self.config.CHATWORK_API_BASE_URL}/rooms/{self.config.CHATWORK_ROOM_ID}/messages"
            data = {
                'body': message
            }
            
            response = self.session.post(url, data=data)
            
            if response.status_code == 200:
                print(f"✅ メッセージを送信しました: {message}")
                return True
            else:
                print(f"❌ メッセージ送信に失敗しました: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            return False
    
    def schedule_daily_notification(self):
        """毎日の日付変更時刻に通知をスケジュール"""
        # ゲーム予告メッセージ（日付変更5分前）
        game_time = "23:55"  # 日付変更5分前
        schedule.every().day.at(game_time).do(self.send_game_announcement)
        print(f"🎮 毎日 {game_time} にゲーム予告メッセージをスケジュールしました")
        
        # 日付変更通知（0〜5分のランダムな遅延）
        schedule.every().day.at(self.config.NOTIFICATION_TIME).do(self.notify_date_change_with_delay)
        print(f"⏰ 毎日 {self.config.NOTIFICATION_TIME} に日付変更通知をスケジュールしました")
    
    def send_game_announcement(self):
        """ゲーム予告メッセージを送信"""
        print("🎮 ゲーム予告メッセージを送信します...")
        success = self.send_message(self.config.GAME_ANNOUNCEMENT_MESSAGE)
        if success:
            print("✅ ゲーム予告メッセージを送信しました")
        else:
            print("❌ ゲーム予告メッセージの送信に失敗しました")
    
    def notify_date_change_with_delay(self):
        """遅延時間を計算して日付変更通知を送信"""
        import random
        delay_minutes = random.randint(0, 5)  # 0〜5分のランダムな遅延
        
        print(f"🎯 日付変更予測ゲーム結果: {delay_minutes}分遅れ")
        
        # 遅延時間分待機（非同期で実行）
        if delay_minutes > 0:
            print(f"⏳ {delay_minutes}分後に日付変更通知を送信します...")
            threading.Timer(delay_minutes * 60, self.send_delayed_notification, args=[delay_minutes]).start()
        else:
            # 遅延なしの場合は即座に送信
            self.send_delayed_notification(delay_minutes)
    
    def send_delayed_notification(self, delay_minutes):
        """遅延後の日付変更通知を送信"""
        print(f"📅 遅延時間({delay_minutes}分)経過、日付変更通知を送信します...")
        
        # 日付変更通知を送信
        self.notify_date_change(delay_minutes)
        
        # 1分後に話題提供メッセージを送信
        print("⏰ 1分後に話題提供メッセージを送信します...")
        threading.Timer(60, self.send_topic_message).start()
    
    def notify_date_change(self, delay_minutes=0):
        """日付変更通知を送信"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        message = self.config.DATE_CHANGE_MESSAGE.format(date=current_date, delay=delay_minutes)
        
        success = self.send_message(message)
        if success:
            print(f"📅 日付変更通知を送信しました: {current_date} (遅延: {delay_minutes}分)")
        else:
            print(f"📅 日付変更通知の送信に失敗しました: {current_date}")
    
    def test_notification(self):
        """テスト時報を送信"""
        print("🧪 テスト時報を実行します...")
        
        # テスト用の一連のプロセスを実行
        import random
        delay_minutes = random.randint(0, 5)  # 0〜5分のランダムな遅延
        
        print(f"🎯 テスト時報予測ゲーム結果: {delay_minutes}分遅れ")
        
        # 遅延時間分待機（非同期で実行）
        if delay_minutes > 0:
            print(f"⏳ {delay_minutes}分後にテスト時報を送信します...")
            threading.Timer(delay_minutes * 60, self.send_test_delayed_notification, args=[delay_minutes]).start()
        else:
            # 遅延なしの場合は即座に送信
            self.send_test_delayed_notification(delay_minutes)
    
    def send_test_delayed_notification(self, delay_minutes):
        """遅延後のテスト時報を送信"""
        print(f"📅 テスト時報遅延時間({delay_minutes}分)経過、日付変更通知を送信します...")
        
        # 日付変更通知を送信
        self.notify_date_change(delay_minutes)
        
        # 1分後に話題提供メッセージを送信
        print("⏰ 1分後に話題提供メッセージを送信します...")
        threading.Timer(60, self.send_topic_message).start()
    
    def send_topic_message(self):
        """話題提供メッセージを送信"""
        print("💬 話題提供メッセージを送信します...")
        success = self.send_message(self.config.TOPIC_MESSAGE)
        if success:
            print("✅ 話題提供メッセージを送信しました")
        else:
            print("❌ 話題提供メッセージの送信に失敗しました")
    
    def start_webhook_server(self):
        """Webhookサーバーを開始"""
        try:
            print(f"🌐 Webhookサーバーをポート {self.config.WEBHOOK_PORT} で開始します")
            self.app.run(host='0.0.0.0', port=self.config.WEBHOOK_PORT, debug=False, use_reloader=False)
        except Exception as e:
            print(f"❌ Webhookサーバー起動エラー: {str(e)}")
    
    def run(self):
        """botを実行"""
        print("🚀 Chatwork日付変更botを開始しました")
        
        # 設定の確認
        if not self.config.CHATWORK_API_TOKEN:
            print("❌ CHATWORK_API_TOKENが設定されていません")
            return
        
        if not self.config.CHATWORK_ROOM_ID:
            print("❌ CHATWORK_ROOM_IDが設定されていません")
            return
        
        if not self.config.TEST_NOTIFICATION_USER_ID:
            print("❌ TEST_NOTIFICATION_USER_IDが設定されていません")
            return
        
        # スケジュール設定
        self.schedule_daily_notification()
        
        print("⏳ 日付変更時刻まで待機中...")
        print(f"👤 テスト時報実行権限者ID: {self.config.TEST_NOTIFICATION_USER_ID}")
        
        if self.config.WEBHOOK_ENABLED:
            print(f"🌐 Webhook機能が有効です (ポート: {self.config.WEBHOOK_PORT})")
            print("📋 ChatworkのWebhook設定で以下のURLを設定してください:")
            print(f"   https://your-domain.com/webhook")
            print("   またはローカルテスト用:")
            print(f"   http://localhost:{self.config.WEBHOOK_PORT}/webhook")
            
            # Webhookサーバーを別スレッドで開始
            webhook_thread = threading.Thread(target=self.start_webhook_server)
            webhook_thread.daemon = True
            webhook_thread.start()
        else:
            print("⚠️ Webhook機能が無効です")
        
        # スケジュール実行ループ
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1分ごとにチェック
        except KeyboardInterrupt:
            print("\n🛑 botを停止しました")

# Flaskアプリケーションのインスタンスを作成
bot = ChatworkDateChangeBot()

# botの初期化を完了
if bot.config.CHATWORK_API_TOKEN and bot.config.CHATWORK_ROOM_ID and bot.config.TEST_NOTIFICATION_USER_ID:
    # スケジュール設定
    bot.schedule_daily_notification()
    print("⏰ 毎日 00:00 に日付変更通知をスケジュールしました")
    print("⏳ 日付変更時刻まで待機中...")
else:
    print("❌ 必要な環境変数が設定されていません")
    print(f"   - CHATWORK_API_TOKEN: {'設定済み' if bot.config.CHATWORK_API_TOKEN else '未設定'}")
    print(f"   - CHATWORK_ROOM_ID: {'設定済み' if bot.config.CHATWORK_ROOM_ID else '未設定'}")
    print(f"   - TEST_NOTIFICATION_USER_ID: {'設定済み' if bot.config.TEST_NOTIFICATION_USER_ID else '未設定'}")

# Flaskアプリケーションをエクスポート（Gunicorn用）
app = bot.app

# Gunicorn起動時のログ出力（強制的に出力）
import sys
sys.stdout.write("🚀 Chatwork日付変更botを開始しました\n")
sys.stdout.write(f"👤 テスト時報実行権限者ID: {bot.config.TEST_NOTIFICATION_USER_ID}\n")
sys.stdout.write(f"🌐 Webhook機能が有効です (ポート: {bot.config.WEBHOOK_PORT})\n")
sys.stdout.write("📋 ChatworkのWebhook設定で以下のURLを設定してください:\n")
sys.stdout.write(f"   https://chat-work-bot-production.up.railway.app/webhook\n")
sys.stdout.write(f"🔐 Webhookトークン: {bot.config.WEBHOOK_SECRET}\n")
sys.stdout.flush()

if __name__ == "__main__":
    bot.run()
