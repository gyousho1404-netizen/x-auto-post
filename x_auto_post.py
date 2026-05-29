import os
import tweepy
import anthropic
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv("C:/x_auto_post/.env")

BLOG_URL = "https://gyouseishosi-sakai.com"
BLOG_DAYS = [1, 2, 3]  # 火=1, 水=2, 木=3

POST_TYPES = [
    "補助金・助成金の豆知識（中小企業や個人事業主向け）",
    "補助金申請の注意点やよくある失敗",
    "行政書士への相談を促す親しみやすいポスト",
    "最新の補助金・助成金制度の紹介",
    "補助金を活用した成功のポイント",
]

def is_blog_post():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    utc_hour = datetime.now(timezone.utc).hour
    return utc_hour == 3 and now.weekday() in BLOG_DAYS

def generate_tweet():
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    if is_blog_post():
        prompt = f"""あなたは行政書士・岡本一希です。
今日ブログを公開しました。Xの投稿文を1つ作成してください。

ブログURL：{BLOG_URL}

ルール：
- 140文字以内（日本語）
- 「本日のブログ更新しました！」から始める
- 補助金・行政書士に関するブログの内容であることを示す
- URLを含める
- ハッシュタグ2個（#補助金 #行政書士）
- 絵文字1〜2個
- 本文のみ出力
"""
    else:
        post_type = POST_TYPES[datetime.now().day % len(POST_TYPES)]
        prompt = f"""あなたは行政書士・岡本一希です。
Xに投稿するツイートを1つ作成してください。

事務所情報：岡本一希行政書士事務所 補助金専門 全国対応

今日のテーマ：{post_type}

ルール：
- 140文字以内（日本語）
- お客様に寄り添う親しみやすいトーン
- ハッシュタグ2〜3個
- 絵文字1〜2個
- 本文のみ出力
"""

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()

def post_to_x(t):
    c = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
    )
    r = c.create_tweet(text=t)
    return r.data["id"]

def main():
    print("投稿開始...")
    if is_blog_post():
        print("ブログ紹介投稿モード")
    tweet = generate_tweet()
    print(f"生成文:{tweet}")
    tid = post_to_x(tweet)
    print(f"完了! https://x.com/i/web/status/{tid}")

if __name__ == "__main__":
    main()
