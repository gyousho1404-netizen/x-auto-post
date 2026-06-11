import os
import tweepy
import anthropic
import urllib.request
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv("C:/x_auto_post/.env")

BLOG_URL = "https://gyouseishosi-sakai.com"
JIZOKUKA_URL = "https://r3.jizokukahojokin.info/"
OSAKA_URL = "https://osaka-profit.com/"

def get_jst_now():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)

def get_utc_hour():
    return datetime.now(timezone.utc).hour

def is_weekday():
    return get_jst_now().weekday() < 5

def generate_tweet(post_type):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    base = "あなたは行政書士・岡本一希です。以下の条件でXの投稿文を1つだけ作成してください。必ず1つの投稿文のみを出力し、選択肢や複数案は絶対に出力しないでください。ハッシュタグを含めて140文字以内に収めてください。"

    if post_type == "blog":
        prompt = base + f"テーマ：ブログ更新のお知らせ。「本日のブログ更新しました！」で始め、補助金・行政書士に関する内容を1文添えてURL（{BLOG_URL}）を含める。ハッシュタグは#補助金と#行政書士の2つ。絵文字1〜2個。"
    elif post_type == "jizokuka":
        prompt = base + f"テーマ：小規模事業者持続化補助金第20回が公募中。対象は小規模事業者。相談を促す内容。URL（{JIZOKUKA_URL}）を含める。最適なハッシュタグ2〜3個。絵文字1〜2個。"
    elif post_type == "osaka":
        prompt = base + f"テーマ：大阪府「利益率向上賃上げ事業」の案内。大阪府の制度であることを明記。URL（{OSAKA_URL}）を含める。#大阪 #賃上げ #補助金などのハッシュタグ2〜3個。絵文字1〜2個。"
    else:
        prompt = base + "テーマ：補助金・助成金の役立ち情報。親しみやすいトーン。最適なハッシュタグ2〜3個。絵文字1〜2個。"

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    tweet = msg.content[0].text.strip()
    # 280文字を超える場合は切り詰め
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    return tweet

def get_post_type():
    hour = get_utc_hour()
    if hour == 23:
        return "blog" if is_weekday() else "general"
    elif hour == 3:
        return "jizokuka"
    elif hour == 9:
        return "osaka"
    else:
        return "general"

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
    pt = get_post_type()
    print(f"投稿開始... タイプ:{pt}")
    tweet = generate_tweet(pt)
    print(f"文字数:{len(tweet)}")
    print(f"生成文:{tweet}")
    tid = post_to_x(tweet)
    print(f"完了! https://x.com/i/web/status/{tid}")

if __name__ == "__main__":
    main()
