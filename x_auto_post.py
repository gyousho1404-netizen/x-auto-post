import os
import tweepy
import anthropic
import urllib.request
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv("C:/x_auto_post/.env")

BLOG_URL = "https://gyouseishosi-sakai.com"
BLOG_DAYS = [1, 2, 3]

SUBSIDY_CASES = [
    {"name": "ものづくり補助金", "industry": "製造業（金属加工）", "detail": "設備投資で生産性30%向上"},
    {"name": "持続化補助金", "industry": "飲食業（ラーメン店）", "detail": "テイクアウト設備導入で売上増加"},
    {"name": "IT導入補助金", "industry": "小売業（雑貨店）", "detail": "POSシステム導入で業務効率化"},
    {"name": "事業再構築補助金", "industry": "宿泊業（旅館）", "detail": "新事業へ転換成功"},
    {"name": "持続化補助金", "industry": "美容業（サロン）", "detail": "SNS集客強化で新規顧客獲得"},
    {"name": "IT導入補助金", "industry": "建設業", "detail": "工程管理システムで残業削減"},
    {"name": "キャリアアップ助成金", "industry": "介護業", "detail": "パート社員の正社員化を実現"},
]

def get_jst_now():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)

def get_utc_hour():
    return datetime.now(timezone.utc).hour

def is_morning_post():
    return get_utc_hour() == 23

def is_noon_post():
    return get_utc_hour() == 3

def is_blog_day():
    return get_jst_now().weekday() in BLOG_DAYS

def is_monday():
    return get_jst_now().weekday() == 0

def fetch_news():
    try:
        url = "https://news.google.com/rss/search?q=%E8%A3%9C%E5%8A%A9%E9%87%91%20%E5%8A%A9%E6%88%90%E9%87%91&hl=ja&gl=JP&ceid=JP:ja"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as res:
            root = ET.fromstring(res.read())
        items = root.findall(".//item")[:3]
        news = []
        for item in items:
            title = item.find("title")
            if title is not None:
                news.append(title.text)
        return news
    except:
        return []

def generate_tweet(post_type):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    if post_type == "case":
        case = SUBSIDY_CASES[get_jst_now().day % len(SUBSIDY_CASES)]
        prompt = f"""あなたは行政書士・岡本一希です。補助金活用事例のXポスト文を1つ作成してください。
補助金名：{case["name"]}、業種：{case["industry"]}、成果：{case["detail"]}
ルール：140文字以内、補助金名と業種を必ず入れる、相談を促す、最適なハッシュタグ2〜3個、絵文字1〜2個、本文のみ出力"""
    elif post_type == "news":
        news = fetch_news()
        news_text = "\n".join(news) if news else "補助金・助成金に関する最新情報"
        prompt = f"""あなたは行政書士・岡本一希です。以下のニュースを参考にXポスト文を1つ作成してください。
最新ニュース：{news_text}
ルール：140文字以内、わかりやすく発信、相談を促す、最適なハッシュタグ2〜3個、絵文字1〜2個、本文のみ出力"""
    elif post_type == "weekly":
        prompt = """あなたは行政書士・岡本一希です。月曜の今週の補助金まとめ投稿を作成してください。
ルール：140文字以内、「今週も」から始める、注目補助金2〜3つ紹介、相談促進、最適なハッシュタグ2〜3個、絵文字1〜2個、本文のみ出力"""
    elif post_type == "blog":
        prompt = f"""あなたは行政書士・岡本一希です。ブログ更新のXポスト文を作成してください。
ブログURL：{BLOG_URL}
ルール：140文字以内、「本日のブログ更新しました！」から始める、URLを含める、ハッシュタグ2個、絵文字1〜2個、本文のみ出力"""
    else:
        themes = ["補助金豆知識", "申請の注意点", "相談促進", "最新制度紹介", "成功事例"]
        theme = themes[get_jst_now().day % len(themes)]
        prompt = f"""あなたは行政書士・岡本一希です。テーマ：{theme}
ルール：140文字以内、親しみやすいトーン、最適なハッシュタグ2〜3個、絵文字1〜2個、本文のみ出力"""
    msg = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=300,
        messages=[{"role": "user", "content": prompt}])
    return msg.content[0].text.strip()

def get_post_type():
    if is_morning_post(): return "case"
    elif is_noon_post():
        if is_monday(): return "weekly"
        elif is_blog_day(): return "blog"
        else: return "news"
    else: return "evening"

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
