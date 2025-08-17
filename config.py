import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込み
load_dotenv()

class Config:
    # Chatwork設定
    CHATWORK_API_TOKEN = os.getenv('CHATWORK_API_TOKEN')
    CHATWORK_ROOM_ID = os.getenv('CHATWORK_ROOM_ID')
    
    # テスト時報実行権限者設定
    TEST_NOTIFICATION_USER_ID = os.getenv('TEST_NOTIFICATION_USER_ID')
    
    # Webhook設定
    WEBHOOK_ENABLED = os.getenv('WEBHOOK_ENABLED', 'true').lower() == 'true'
    # Railwayでは環境変数PORTが自動で設定される
    WEBHOOK_PORT = int(os.getenv('PORT', os.getenv('WEBHOOK_PORT', '8080')))
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')
    
    # 通知設定
    NOTIFICATION_TIME = "00:00"  # 日付変更時刻（24時間形式）
    
    # メッセージ設定
    DATE_CHANGE_MESSAGE = "🎉 新しい日が始まりました！今日も一日頑張りましょう！"
    
    # API設定
    CHATWORK_API_BASE_URL = "https://api.chatwork.com/v2"
