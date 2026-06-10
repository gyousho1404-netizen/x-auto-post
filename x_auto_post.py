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
    if post_type == "blog":
        prompt = f"あなたは行政書士・岡本一希です。ブログ更新のXポスト文を作成。URL:{BLOG_URL}。140文字以内、本日のブログ更新しました！から始める、URL含める、#補助金 #行政書士のハッシュタグ2個、絵文字1～2個、本文のみ"
    elif post_type == "jizokuka":
        prompt = f"あなたは行政書士・岡本一希です。小規模事業者持続化補助金第20回公募中の案内ポスト。URL:{JIZOKUKA_URL}。140文字以内、第20回公募中であること、小規模事業者対象、URL含む、相談促進、最適なハッシュタグ2～3個、絵文字1～2個、本文のみ"
    elif post_type == "osaka":
        prompt = f"あなたは行政書士・岡本一希です。大阪府「利益率向上賃上げ事業」の案内ポスト。URL:{OSAKA_URL}。140文字以内、大阪府の制度であること明記、URL含む、#大阪 #賃上げ #補助金のハッシュタグ2～3個、絵文字1～2個、本文のみ"
    else:
        prompt = "行政書士・岡本一希。補助金情報のXポスト。140文字以内、ハッシュタグ2～3個、本文のみ"
    msg = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=300, messages=[{"role":"user","content":prompt}])
    return msg.content[0].text.strip()

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
    c = tweepy.Client(consumer_key=os.getenv("X_API_KEY"), consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"), access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"))
    r = c.create_tweet(text=t)
    return r.data["id"]

def main():
    pt = get_post_type()
    print(f"投稿開始... タイプ:{pt}")
    tweet = generate_tweet(pt)
    print(f"生成文:{tweet}")
    tid = post_to_x(tweet)
    print(f"完了! https://x.com/i/web/status/{tid}")

if __name__ == "__main__":
    main()
