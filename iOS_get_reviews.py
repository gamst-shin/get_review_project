#!/usr/bin/env python3
 
import time , boto3 , json, jwt , requests, os, subprocess
 
session = boto3.session.Session(profile_name={aws_profile})
s3 = session.resource('s3')
s3_client = session.client('s3')
json_noti_url=''
 
# get s3 contents
def s3_get_object(bucketname , key):
    s3_object = s3_client.get_object(
        Bucket=bucketname,
        Key=key
    )
    return s3_object['Body'].read().decode('utf-8')
 
def s3_get_packageName():
    global json_noti_url
    packagelist = s3_get_object({s3_bucket_name}, 'marketCrawling/IOS/config/appstore_crawling_appleid.json')
    dict_package = json.loads(packagelist)
    authinfo = s3_get_object({s3_bucket_name}, 'marketCrawling/AOS/config/kakaogames_googleplaystore_authinfo.json')
    dict = json.loads(authinfo)
    json_noti_url = dict['noti']
#    for h in dict1['packagename']:
#        print(h['name'])
    return dict_package
#dict1 = s3_get_packageName()
 
def get_ios_review(appleId):
    cur_time = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
    filename = cur_time + "review.json"
    filepath = "/home/svc-admin/iosCrawling/reviews/"
    # url에 앱스토어에서 제공하는 Apple ID 넣기
    url = 'https://itunes.apple.com/kr/rss/customerreviews/sortBy=mostRecent/id=' + appleId + '/json'
    req = requests.get(url).json()
    first_review_id = req["feed"]["entry"][0]["id"]["label"]
 
 
#ios는 리뷰 json에 시간 필드가 없어서 두 개의 파일 비교(현재 가져온 json 파일에서 첫 번째 아이디를 가지고 비교)
    with open(filepath + filename, 'w', encoding="utf-8") as make_file:
        json.dump(req, make_file, ensure_ascii=False)
 
    return first_review_id
 
def review_parse(first_review_id):
    filepath = "/home/svc-admin/iosCrawling/reviews/"
    filename = os.listdir(filepath)[1]
    target_file = os.listdir(filepath)[0]
    with open(filepath + filename, 'r', encoding="utf-8") as json_file:
        data = json.load(json_file)
 
        id = []
        text = []
        star_rating = []
        name = []
        link_addr = []
        sendmsg = []
        first_id = data["feed"]["entry"][0]["id"]["label"]
 
        if first_review_id == first_id:
            print("same id")
        else:
            length = len(data["feed"]["entry"])
 
            for i in range(0, length):
                id.append(data["feed"]["entry"][i]["id"]["label"])
                name.append(data["feed"]["entry"][i]["author"]["name"]["label"])
                star_rating.append(data["feed"]["entry"][i]["im:rating"]["label"])
                link_addr.append(data["feed"]["entry"][i]["link"]["attributes"]["href"])
                text.append(data["feed"]["entry"][i]["content"]["label"])
                 
                if first_review_id == id[i]:
                    break
 
                rate = (int(star_rating[i]) * "★") + ((5 - int(star_rating[i])) * "☆")
                msg = "이름 : " + name[i] + '\n' + "별점 : " + rate + "\n" + text[i] + "\n\n"
                sendmsg.append(msg)
    subprocess.run(['rm' + ' ' + filepath + target_file], shell=True)
 
    return sendmsg


"""
def send_watchtower(msg, watchtowerid):
    global json_noti_url
    data = {
     'from': 'watchtower.bot',
     'to': watchtowerid,
     'msg': msg,
     'ps': 'false'
    }
    response = requests.post(json_noti_url, data=data)
    return response.text
"""
 
if __name__ == "__main__":
    var_dict_packagename = s3_get_packageName()
 
    for h in var_dict_packagename['AppleId']:
        first_review_id = get_ios_review(str(h["appleId"]))
        var_reviews = review_parse(first_review_id)
        print(h["watchtowerid"])
        #send_watchtower(var_reviews, str(h['watchtowerid']))
        #time.sleep(1)