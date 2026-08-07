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

    base = (
        "あなたは堺・南大阪で活動する行政書士・岡本一希です。"
        "中小企業や個人事業主の経営者に向けて、Xの投稿文を1つだけ作成してください。"
        "必ず1つの投稿文のみを出力し、選択肢・複数案・前置き・説明文は一切出力しないこと。"
        "ハッシュタグと絵文字を含めて必ず140文字以内に収めること。"
        "【伸ばすためのルール】"
        "(1)最初の一行を強いフックにする(具体的な数字や『知らないと損』『実は』など、読み手が思わず手を止める書き出し)。"
        "(2)保存・リポストしたくなる、具体的で役立つ情報を1点だけ入れる。"
        "(3)売り込み口調は避け、読者の味方として語りかける親しみやすいトーン。"
        "(4)絵文字は多くても1〜2個、ハッシュタグは効果的なものを2〜3個。"
        "(5)締切日や金額上限などの数字は、確実なもの以外は断定せず『締切が近づいています』"
        "『最大◯百万円規模』のような表現に留め、詳細は相談・確認を促す(誤情報を避ける)。"
        "(6)本文にURL・リンクは絶対に含めないこと。詳細へ誘導する場合は『プロフィールのリンクから』と書くこと。"
    )

    if post_type == "blog":
        prompt = base + "【型:金額インパクト+ブログ誘導】補助金にまつわる意外な数字や『知らないと損』な一言でフックを作り、続けて本日ブログを更新した旨とその記事で分かることを1文で伝える。詳しくは『プロフィールのリンクから』と誘導する(本文にURLは書かない)。ハッシュタグは#補助金 #行政書士 を基本に。"
    elif post_type == "jizokuka":
        prompt = base + "【型:30秒チェックリスト】小規模事業者持続化補助金について、『あなたの事業は対象かも』と読者が自己診断できるチェック項目を□付きで2つ示し、当てはまれば気軽に相談してほしいと促す。"
    elif post_type == "it_intro":
        prompt = base + "【型:締切カウントダウン】デジタル化・AI導入補助金(旧IT導入補助金)について、公募には締切があり、GビズID取得など準備に時間がかかるため今から動く必要がある旨を緊張感を持って伝え相談を促す。具体的な締切日は断定しない。"
    elif post_type == "it_detail":
        prompt = base + "【型:金額インパクト】デジタル化・AI導入補助金の魅力を、補助率の高さ(最大4/5規模)や対象になるツール(会計・販売管理・AI活用ツール等)のうち1点に絞って紹介し、『自腹で買う前に一度検討を』と促す。"
    elif post_type == "osaka":
        prompt = base + "【型:失敗あるある】小規模事業者持続化補助金でやりがちな失敗(例:先に発注して対象外になる/後払いだと知らない/締切ギリギリで書類が間に合わない)から1つを取り上げ、『こうならないために早めの相談を』と促す。"
    else:
        prompt = base + "【型:業種特化】建設業・飲食店・美容室・小売店など特定の業種を1つ選び、『◯◯の方へ』と名指しで、その業種が使える補助金や具体的な活用例を1点紹介して相談を促す。"

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
    # 1日1回・曜日で投稿タイプをローテーション（コスト最適化）
    # 月:締切カウントダウン(AI導入) 火:チェックリスト(持続化)
    # 水:金額インパクト(AI導入)   木:失敗あるある(持続化)
    # 金:ブログ誘導               土日:業種特化
    weekday = get_jst_now().weekday()  # 月=0 ... 日=6
    rotation = {
        0: "it_intro",
        1: "jizokuka",
        2: "it_detail",
        3: "osaka",
        4: "blog",
        5: "general",
        6: "general",
    }
    return rotation.get(weekday, "general")

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
