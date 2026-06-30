import os
import tweepy
import anthropic
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv("C:/x_auto_post/.env")

BLOG_URL = "https://gyouseishosi-sakai.com"
JIZOKUKA_URL = "https://r3.jizokukahojokin.info/"
OSAKA_URL = "https://osaka-profit.com/"

def get_jst_now():
    jst = timezone(timedelta(hours=9))
    return datetime.now(jst)

def is_weekday():
    return get_jst_now().weekday() < 5

def is_mwf():
    # 月(0)・水(2)・金(4)
    return get_jst_now().weekday() in [0, 2, 4]

def generate_tweet(post_type):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    base = "あなたは行政書士・岡本一希です。以下の条件でXの投稿文を1つだけ作成してください。必ず1つの投稿文のみを出力し、選択肢や複数案は絶対に出力しないでください。ハッシュタグを含めて140文字以内に収めてください。"

    if post_type == "blog":
        prompt = base + f"テーマ：ブログ更新のお知らせ。「本日のブログ更新しました！」で始め、補助金・行政書士に関する内容を1文添えてURL（{BLOG_URL}）を含める。ハッシュタグは#補助金と#行政書士の2つ。絵文字1〜2個。"
    elif post_type == "jizokuka":
        prompt = base + "テーマ：小規模事業者持続化補助金第20回が公募中。対象は小規模事業者。相談を促す内容。最適なハッシュタグ2〜3個。絵文字1〜2個。"
    elif post_type == "it_intro":
        prompt = base + "テーマ：IT導入補助金の公募案内。中小企業・小規模事業者向けITツール導入支援。補助率・対象ツールの概要を親しみやすく紹介。相談を促す内容。最適なハッシュタグ2〜3個。絵文字1〜2個。"
    elif post_type == "it_detail":
        prompt = base + "テーマ：IT導入補助金の具体的な内容紹介。補助率1/2〜3/4・上限額・対象ソフトウェア（会計・販売管理・ECなど）のうち1点を掘り下げて紹介。中小企業に役立つ実用的なトーン。最適なハッシュタグ2〜3個。絵文字1〜2個。"
    elif post_type == "osaka":
        prompt = base + "テーマ：小規模事業者持続化補助金の具体的な内容紹介。補助率2/3・上限50万円（条件により200万円）・対象経費（広告費・店舗改装など）のうち1点を掘り下げて紹介。小規模事業者に役立つ実用的なトーン。最適なハッシュタグ2〜3個。絵文字1〜2個。"
    else:
        prompt = base + "テーマ：補助金・助成金の役立ち情報。親しみやすいトーン。最適なハッシュタグ2〜3個。絵文字1〜2個。"

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    tweet = msg.content[0].text.strip()
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    return tweet

def get_post_type():
    # GitHub Actions の cron トリガーを元に投稿タイプを決定（遅延対策）
    schedule = os.getenv("SCHEDULE", "")
    if schedule == "0 1 * * *":
        return "blog" if is_weekday() else "general"
    elif schedule == "0 3 * * *":
        return "it_intro" if is_mwf() else "jizokuka"
    elif schedule == "0 10 * * *":
        return "it_detail" if is_mwf() else "osaka"
    # ローカル実行用フォールバック（時間で判定）
    hour = datetime.now(timezone.utc).hour
    if hour == 1:
        return "blog" if is_weekday() else "general"
    elif hour == 3:
        return "it_intro" if is_mwf() else "jizokuka"
    elif hour == 10:
        return "it_detail" if is_mwf() else "osaka"
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
    print(f"投稿開始... タイプ:{pt}, スケジュール:{os.getenv('SCHEDULE','未設定')}")
    tweet = generate_tweet(pt)
    print(f"文字数:{len(tweet)}")
    print(f"生成文:{tweet}")
    tid = post_to_x(tweet)
    print(f"完了! https://x.com/i/web/status/{tid}")

if __name__ == "__main__":
    main()
