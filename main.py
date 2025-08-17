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
            
            if not data:
                print("❌ Webhookデータが空です")
                return jsonify({'status': 'error', 'message': 'No data received'}), 400
            
            # メッセージイベントをチェック
            if 'message' in data:
                message_data = data['message']
                
                # メッセージの内容をチェック
                if 'body' in message_data and 'account' in message_data:
                    message_body = message_data['body'].strip()
                    account_id = str(message_data['account']['account_id'])
                    account_name = message_data['account']['name']
                    
                    print(f"📨 Webhook受信: {account_name} -> {message_body}")
                    
                    # テスト時報コマンドをチェック
                    if (message_body == "テスト時報" and 
                        account_id == self.config.TEST_NOTIFICATION_USER_ID):
                        
                        print(f"🧪 ユーザー {account_name} からテスト時報コマンドを受信しました")
                        # 別スレッドでテスト時報を実行
                        threading.Thread(target=self.test_notification, daemon=True).start()
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            print(f"❌ Webhook処理エラー: {str(e)}")
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
    
    def notify_date_change(self):
        """日付変更通知を送信"""
        current_date = datetime.now().strftime("%Y年%m月%d日")
        message = f"{self.config.DATE_CHANGE_MESSAGE}\n📅 {current_date}"
        
        success = self.send_message(message)
        if success:
            print(f"📅 日付変更通知を送信しました: {current_date}")
        else:
            print(f"📅 日付変更通知の送信に失敗しました: {current_date}")
    
    def test_notification(self):
        """テスト時報を送信"""
        print("🧪 テスト時報を実行します...")
        self.notify_date_change()
    
    def schedule_daily_notification(self):
        """毎日の日付変更時刻に通知をスケジュール"""
        schedule.every().day.at(self.config.NOTIFICATION_TIME).do(self.notify_date_change)
        print(f"⏰ 毎日 {self.config.NOTIFICATION_TIME} に日付変更通知をスケジュールしました")
    
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

# Flaskアプリケーションをエクスポート（Gunicorn用）
app = bot.app

if __name__ == "__main__":
    bot.run()
