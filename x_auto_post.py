
import os
import tweepy
import anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

OFFICE_INFO = '岡本一希行政書士事務所 補助金専門 gyousho1404@gmail.com 全国対応'

POST_TYPES = ['補助金豆知識','申請の注意点','相談促進','最新制度紹介','成功のポイント']

def generate_tweet():
    client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    post_type = POST_TYPES[datetime.now().day % len(POST_TYPES)]
    msg = client.messages.create(model='claude-haiku-4-5-20251001',max_tokens=300,messages=[{'role':'user','content':f'行政書士・岡本一希として補助金情報のXポスト文を1つ作成。テーマ:{post_type}。140文字以内。ハッシュタグ2-3個。絵文字1-2個。本文のみ出力。'}])
    return msg.content[0].text.strip()

def post_to_x(t):
    c = tweepy.Client(consumer_key=os.getenv('X_API_KEY'),consumer_secret=os.getenv('X_API_SECRET'),access_token=os.getenv('X_ACCESS_TOKEN'),access_token_secret=os.getenv('X_ACCESS_TOKEN_SECRET'))
    r = c.create_tweet(text=t)
    return r.data['id']

def main():
    print('投稿開始...')
    tweet = generate_tweet()
    print(f'生成文:{tweet}')
    tid = post_to_x(tweet)
    print(f'完了! https://x.com/i/web/status/{tid}')

if __name__ == '__main__':
    main()
