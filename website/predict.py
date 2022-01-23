import re
import requests
import pandas as pd
import pickle
import urllib3
import time
import json
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from collections import Counter, OrderedDict
from bs4 import BeautifulSoup
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, log_loss, classification_report
urllib3.disable_warnings()
warnings.filterwarnings('ignore')

def shopeeScraper (url):
    url = url
    r = re.search(r'i\.(\d+)\.(\d+)', url)
    shop_id, item_id = r[1], r[2]
    ratings_url = 'https://shopee.co.id/api/v2/item/get_ratings?filter=0&flag=1&itemid={item_id}&limit=20&offset={offset}&shopid={shop_id}&type=0'
    data_scrape = []

    offset = 0
    print('Scraping Process...')
    while True:    
        data = requests.get(ratings_url.format(shop_id=shop_id, item_id=item_id, offset=offset)).json()

        i = 1
        try :
            for i, rating in enumerate(data['data']['ratings'], 1):
                if rating['comment'] == '':
                    pass
                else:
                    data_scrape.append([rating['rating_star'], rating['comment']])
        except :
            pass

        if i % 20:
            break

        offset += 20
    print('Scraping Done.')
    df = pd.DataFrame(data_scrape, columns=['rating', 'reviews'])
    df = df.dropna(axis=0)
    return df

# TO DO: Function Tokopedia Scraper
def tokopediaScraper(link):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36")

    driver = webdriver.Chrome(executable_path="chromedriver", options=chrome_options)
    driver.get(link)

    pageSource = driver.page_source
    soup = BeautifulSoup(pageSource, 'html')
    get_prod_id = soup.find( 'meta', attrs={'name': 'branch:deeplink:$ios_deeplink_path'})
    prod_id_raw = get_prod_id['content']
    prod_id = prod_id_raw.replace('product/','')
    print(prod_id)

    ############################### PAYLOAD ###############################################


    pay_tr1 =  r'[{"operationName":"PDPGetProductRatingQuery","variables":{"productId":"'
    pay_tr2 = str(prod_id)
    pay_tr3 = r'"},"query":"query PDPGetProductRatingQuery($productId: String!) {\n  productrevGetProductRating(productID: $productId) {\n    ratingScore\n    totalRating\n    totalRatingWithImage\n    detail {\n      rate\n      totalReviews\n      percentage\n      __typename\n    }\n    __typename\n  }\n}\n"}]'
    payload_total_rating = f'{pay_tr1}{pay_tr2}{pay_tr3}'
    data = json.loads(payload_total_rating)[0]
    err = True
    count = 0
    while err:
        try:
            res = requests.post('https://gql.tokopedia.com/', json=data)
            err = False
        except:
            err = True
            count += 1
            print(count, 'try')

    num_rate = res.json()['data']['productrevGetProductRating']['totalRating']# ambil dari respon gql
    page = round(num_rate/10)
    
    mess = []
    rate = []
    for x in range(page):
        tmp = {}
        pay1 = r'[{"operationName": "ProductReviewListQueryV2","variables": {"page": '
        pay2 = str(x+1)
        for star in range(5):
            pay3 = r',"rating": '
            pay4 = str(star)
            pay5 = r',"withAttachment": 0,'
            pay6 = r'"productID": "'
            pay7 = str(prod_id)
            pay8 = r'","perPage": 10 },"query": "query ProductReviewListQueryV2($productID: String!, $page: Int!, $perPage: Int!, $rating: Int!, $withAttachment: Int!) {\n  ProductReviewListQueryV2(productId: $productID, page: $page, perPage: $perPage, rating: $rating, withAttachment: $withAttachment) {\n    shop {\n      shopIdStr\n      name\n      image\n      url\n      __typename\n    }\n    list {\n      reviewIdStr\n      message\n      productRating\n      reviewCreateTime\n      reviewCreateTimestamp\n      isReportable\n      isAnonymous\n      imageAttachments {\n        attachmentId\n        imageUrl\n        imageThumbnailUrl\n        __typename\n      }\n      reviewResponse {\n        message\n        createTime\n        __typename\n      }\n      likeDislike {\n        totalLike\n        likeStatus\n        __typename\n      }\n      user {\n        userId\n        fullName\n        image\n        url\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n"}]'
            payload = f'{pay1}{pay2}{pay3}{pay4}{pay5}{pay6}{pay7}{pay8}'
            data = json.loads(payload)[0]
        
            
            data['variables']['params'] = f'https://www.tokopedia.com/bricksid/lego-71395-super-mario-peach-s-castle'
            err = True
            count = 0
            while err:
                try:
                    res = requests.post('https://gql.tokopedia.com/',json=data)
                    
                    err = False
                except:
                    err = True
                    count += 1
                    print(count, 'try')
                
                
                product_desc = res.json()['data']['ProductReviewListQueryV2']['list']# ambil dari respon gql
                
                print(f'page: {x} rate {star}')
                for i in range(len(product_desc)):
                    if product_desc[i]['message'] != '':
                        a = product_desc[i]['message']
                        b = product_desc[i]['productRating']
                        mess.append(a)
                        rate.append(b)

    df = pd.DataFrame(list(zip(mess, rate)),
                columns =['reviews', 'rating'])
    return df

def trainingData(X, y):
    #membangun vector space model/pembobotan dengan tfidf
    vectorizer = TfidfVectorizer(ngram_range=(1,4), min_df=10)
    features = vectorizer.fit_transform(X)

    #melakukan split data training untuk mengetahui akurasi
    X_train, X_test, y_train, y_test = train_test_split(features, y, test_size=0.1, random_state=4)

    #modeling sentiment
    LR_ = LogisticRegression(C=3, solver='liblinear', max_iter=150).fit(X_train, y_train)

    # melakukan evaluasi
    yhat = LR_.predict(X_test)

    yhat_prob = LR_.predict_proba(X_test)
    
    return LR_, vectorizer

def importDataModel(path):
    df_model = pd.read_csv(path)
    df_model = df_model.dropna(axis=0)
    return df_model

def splitFeatures(df_model): 
    X = df_model['reviews']
    y = df_model['label']
    return X, y

def makeModel(X, y):
    model, vectorizer = trainingData(X, y)
    return model, vectorizer

def makeDataset(url):
    URL = url
    df = shopeeScraper(URL)
    return df

def predictData(df, model, vectorizer):
    features = vectorizer.transform(df.reviews)
    result = model.predict(features)
    df['label'] = result
    return df

def countLabel(df):
    label_positive = Counter(df.label)[1]
    label_negative = Counter(df.label)[0]
    total_label = label_positive + label_negative
    return label_positive, label_negative

def filterNegativeLabel(df):
    df_negative = df[df['label'] == 0]
    return df_negative

def cosineSimilarity(df_negative, vectorizer):
    X = df_negative['reviews']
    tfidf_matrix = vectorizer.transform(X)
    cos_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    return cos_sim

def recommenderSystem(cos_sim, df_negative):
    matrix = pd.DataFrame(cos_sim)
    similarity = []

    for i in range (len(matrix)):
        similarity.append(matrix[i].mean())
    df_negative['similarity'] = similarity
    df_negative = df_negative.sort_values(by='similarity', ascending=False)
    df_negative = df_negative.reset_index(drop=True)
    
    recommend = []
    if len(df_negative.reviews) <= 5:
        for i in range(2):
            recommend.append(df_negative.reviews[i])
    elif len(df_negative.reviews) <= 3:
        for i in range(1):
            recommend.append('Produk anda sudah sangat baik')
    else:
        for i in range(4):
            recommend.append(df_negative.reviews[i])
    return recommend

def runApp(path, df):
    PATH_DF_MODEL = path
    df_model = importDataModel(PATH_DF_MODEL)
    X, y = splitFeatures(df_model)
    model, vectorizer = makeModel(X, y)
    df = predictData(df, model, vectorizer)
    pos, neg = countLabel(df)
    df_negative = filterNegativeLabel(df)
    cos_sim = cosineSimilarity(df_negative, vectorizer)
    recommend = recommenderSystem(cos_sim, df_negative)
    return pos, neg, recommend