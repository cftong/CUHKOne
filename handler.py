from bs4 import BeautifulSoup
import urllib2
import re
import datetime
from urlparse import urlparse


def getDigest(event, context):
    site = "http://cumassmail.itsc.cuhk.edu.hk/weekly/"
    site_param = ""

    try:
        if event["date"] != "":
            site_param = "/Digest/List/UG/{}/".format(int(event["date"]))
    except ValueError:
        pass

    data = urllib2.urlopen(site + site_param).read()
    soup = BeautifulSoup(data)
    soup.prettify()
    titles = soup.findAll('div', {'class': "digestSummaryTitleBar"})
    contents = soup.findAll('div', {'class': "digestSummaryContent"})
    date = datetime.datetime.strptime(
        soup.find('span', {'class': "digestSummaryDate", 'id': 'lblDigestSummaryDate'}).text, '%Y/%m/%d').strftime(
        '%d/%m/%Y')
    response = []
    for title, content in zip(titles, contents):
        txtTitle = title.text
        subtitles = content.findAll("li")
        for subtitle in subtitles:
            response.append(
                {"date": date, "type": txtTitle, "title": subtitle.a.string,
                 "link": "https://cumassmail.itsc.cuhk.edu.hk" + subtitle.a.get("href")})
    body = {
        "titles": response
    }
    return body


def getNA(event, context):
    udt_1149_param_page = 1
    udt_1149_param_search2 = 2016
    site = "http://www.na.cuhk.edu.hk/zh-hk/aboutnewasia/news-zhhk.aspx"
    site_pram = "?udt_1149_param_page={}&udt_1149_param_search2={}"

    try:
        if event["year"] != "":
            udt_1149_param_search2 = int(event["year"])
        if event["page"] != "":
            udt_1149_param_page = int(event["page"])
    except ValueError:
        pass

        if event["lang"] != "":
            if "en" == event["lang"]:
                site = "http://www.na.cuhk.edu.hk/en-us/aboutnewasia/news.aspx"
                site_pram = "?udt_1148_param_page={}&udt_1148_param_search2={}"

    url = (site + site_pram).format(udt_1149_param_page, udt_1149_param_search2)
    data = urllib2.urlopen(url).read()

    soup = BeautifulSoup(data)
    soup.prettify()

    # Get the last page number
    table__paging_table = soup.find('td', {'class': "Normal", 'align': "Right"})
    last_page = table__paging_table.find_all("a")[-1].get("href")
    mc = int(re.findall(r"(\?|\&)([^=]+)_param_page=([^&]+)", last_page)[0][2])

    table__paging_table = soup.find('table', {'class': 'news'})
    if udt_1149_param_page > mc + 1:
        return {"titles": []}
    data2 = table__paging_table.findAll("tr", {'class': None})
    result = []
    for row in data2:
        data3 = row.find_all("td")
        url = (site + data3[2].a.get("href")).format(udt_1149_param_page, udt_1149_param_search2)
        result.append({"date": data3[1].string, "type": data3[0].img.get("alt"), "title": data3[2].a.string,
                       "link": url})

    body = {
        "titles": result
    }
    return body


def getDetails(event, context):
    body = {}
    if event["url"] != "":
        parsed_uri = urlparse(event["url"])
        try:
            data = urllib2.urlopen(event["url"]).read()
        except urllib2.URLError:
            return {}
        soup3 = BeautifulSoup(data)
        soup3.prettify()
        newTitle = ""
        content = ""
        date = ""

        if parsed_uri.netloc == "www.na.cuhk.edu.hk":
            newTitleObj = soup3.find('h1', {'class': 'newsTitle'})
            newTitle = newTitleObj.string
            content = newTitleObj.parent.span.string
            date = newTitleObj.parent.find("p").string
        elif parsed_uri.netloc == "cumassmail.itsc.cuhk.edu.hk":
            newTitleObj = soup3.find('div', {'id': 'divMessageHeader'})
            newTitle = newTitleObj.text
            content = newTitleObj.parent.find("div", {'id': 'divMessageContent'}).text
            date = soup3.find('a', {'id': 'lnkDispatchDate'}).string

        body = {
            "date": date,
            "title": newTitle,
            "content": content
        }
    return body
