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
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', 'YQMXkrEged4QTepDiaJyma/CIojyOZpCFVEdXhphQpU=')
    
    # 通知設定
    NOTIFICATION_TIME = "00:00"  # 日付変更時刻（24時間形式）
    
    # メッセージ設定
    GAME_ANNOUNCEMENT_MESSAGE = "[info][title]日付変更予測ゲームのお知らせ[/title]\nどもども、みんな大好き遅れ時報君だよ、遅くまで起きてるみんなにゲームを用意したんだ\n前は意図せず遅れてたけど今回からはわざと遅れてゲーム風になるようにしたよ\n今回はまだ改造途中で本格的にはスタートしないけど、一応追加しましたぁ\n正式の実装されたら何回正解したら変人に一つ命令できるとかくだらないものが手に入るかもね\n\nでは予測スタート！0〜5分の間だよ！[/info]"
    DATE_CHANGE_MESSAGE = "[info][title]日付変更！[/title]\n今日も元気にお知らせ！新しい一日の始まりだね！\n今日、{date}は{delay}分遅れ！当てられたかな？[/info]"
    
    # API設定
    CHATWORK_API_BASE_URL = "https://api.chatwork.com/v2"
