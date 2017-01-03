from bs4 import BeautifulSoup
import urllib2
import re
import datetime
from urlparse import urlparse, urljoin


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


def getNAData(page, year, site, site_pram, infcount,lang):
    soup = BeautifulSoup(urllib2.urlopen((site + site_pram).format(page - infcount, year)).read())
    soup.prettify()
    if lang:
        last_page = int(
            re.findall(r"^\w+\xa0\d+\xa0\s+of\s\xa0(\d+)$",
                       soup.find('td', {'class': "Normal", 'align': "Left"}).string)[
                0])
    else:
        last_page = int(re.findall(u"\u7b2c\s\d+\s\u9801\uff0c\u5171\s(\d+)\s\u9801",
                                   soup.find('td', {'class': "Normal", 'align': "Left"}).prettify(), re.U)[0])

    if page > last_page:
        # return getNAData(page - infcount, year - 1, site, site_pram, infcount + last_page)
        # Get the last page number
        return None
    try:
        return soup.find('table', {'class': 'news'})
    except AttributeError:
        return None
    except IndexError:
        return getNAData(page, year - 1, site, site_pram, 0)


def getNA(event, context):
    udt_1149_param_page = 1
    udt_1149_param_search2 = datetime.datetime.now().year
    site = "http://www.na.cuhk.edu.hk/zh-hk/aboutnewasia/news-zhhk.aspx"
    site_pram = "?udt_1149_param_page={}&udt_1149_param_search2={}"

    try:
        if event["year"] != "":
            udt_1149_param_search2 = int(event["year"])
        if event["page"] != "":
            udt_1149_param_page = int(event["page"])
    except ValueError:
        pass
    isEN = False
    if event["lang"] != "":
        if "en" == event["lang"]:
            site = "http://www.na.cuhk.edu.hk/en-us/aboutnewasia/news.aspx"
            site_pram = "?udt_1148_param_page={}&udt_1148_param_search2={}"
            isEN = True

    try:
        data2 = getNAData(udt_1149_param_page, udt_1149_param_search2, site, site_pram, 0,isEN).findAll("tr",
                                                                                                   {'class': None})
    except AttributeError:
        return {"titles": []}
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
        for tag in soup3.findAll('a', href=True):
            tag['href'] = urljoin(parsed_uri.scheme + "://" + parsed_uri.netloc, tag['href'])
        for tag in soup3.findAll('img', src=True):
            tag['src'] = urljoin(parsed_uri.scheme + "://" + parsed_uri.netloc, tag['src'])
        newTitle = ""
        content = ""
        date = ""

        if parsed_uri.netloc == "www.na.cuhk.edu.hk":
            newTitleObj = soup3.find('h1', {'class': 'newsTitle'})
            newTitle = newTitleObj.string
            date = newTitleObj.parent.find("p").string
            soup3.find('h1', {'class': 'newsTitle'}).extract()
            soup3.find('p', {'class': 'newsDate'}).extract()
            soup3.find('div', {'style': 'float:right;'}).extract()
            content = str(soup3.find('div', {'class': 'DNNModuleContent'}).prettify())
            # content = newTitleObj.parent.span.string
        elif parsed_uri.netloc == "cumassmail.itsc.cuhk.edu.hk":
            newTitleObj = soup3.find('div', {'id': 'divMessageHeader'})
            newTitle = newTitleObj.text
            content = str(newTitleObj.parent.find("div", {'id': 'divMessageContent'}).prettify())
            # content = newTitleObj.parent.find("div", {'id': 'divMessageContent'}).text
            date = soup3.find('a', {'id': 'lnkDispatchDate'}).string

        body = {
            "date": date,
            "title": newTitle,
            "content": content
        }
    return body
