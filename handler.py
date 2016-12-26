import json
from bs4 import BeautifulSoup
import urllib2


def getna(event, context):

    udt_1149_param_page = 1
    udt_1149_param_search2 = 2016
    site = "http://www.na.cuhk.edu.hk/zh-hk/aboutnewasia/news-zhhk.aspx?udt_1149_param_page={" \
           "}&udt_1149_param_search2={} "

    if "year" in event:
        udt_1149_param_search2 = int(event["year"])
    if "page" in event:
        udt_1149_param_page = int(event["page"])
    if "lang" in event:
        if "en" == event["lang"]:
            site = "http://www.na.cuhk.edu.hk/en-us/aboutnewasia/news.aspx?udt_1148_param_page={" \
                   "}&udt_1148_param_search2={} "

    url = site.format(udt_1149_param_page, udt_1149_param_search2)
    data = urllib2.urlopen(url).read()

    soup = BeautifulSoup(data)
    soup.prettify()
    table__paging_table = soup.find('table', {'class': 'news'})
    if table__paging_table is None:
        return data
    soup2 = BeautifulSoup(str(table__paging_table), 'html.parser')
    data2 = soup2.findAll("tr", {'class': None})
    result = []
    for row in data2:
        data3 = row.find_all("td")
        result.append({"date": data3[1].string, "type": data3[0].img.get("alt"), "title": data3[2].a.string,
                       "link": data3[2].a.get("href")})

    body = {
        "titles": result
    }

    # response = {
    #     "statusCode": 200,
    #     "body": json.dumps(body)
    # }

    return body
