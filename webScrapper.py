import re
import requests
import datetime
from bs4 import BeautifulSoup

# Retrieve the web page
URL = "https://dev.to/t/python"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")
result = soup.find(id="substories")

# Get all articles
articles = result.find_all("div", class_="crayons-story")

article_result = []
# Get today's date and the date from a week ago
today = datetime.datetime.today()
a_week_ago = today - datetime.timedelta(days=7)

for article in articles:

    # Get title and link
    title_element = article.find("a", id=re.compile("article-link-\d+"))
    title = title_element.text.strip()
    link = title_element["href"]

    # Get publish date
    pub_date_element = article.find("time")
    pub_date = pub_date_element.text

    # Get number of reactions
    reaction_element = article.find(string=re.compile("reaction"))

    # If no reaction found, reaction is set to 0
    if reaction_element != None:
        reaction_element = reaction_element.findParent("a")
        reaction = re.findall("\d+", reaction_element.text)
        reaction = int(reaction[0])
    else:
        reaction = 0

    # Get publish date in datetime type for comparison
    pub = datetime.datetime.strptime(pub_date + str(today.year), "%b %d%Y")

    # If an article has more than 5 reactions, and is published less than a week ago,
    # the article is added to article_result
    if reaction >= 5 and pub > a_week_ago:
        article_result.append(
            {"title": title, "link": link, "pub_date": pub_date, "reaction": reaction}
        )

# Sort articles by number of reactions
article_result = sorted(article_result, key=lambda d: d["reaction"], reverse=True)

# Write the result to python-latest.md
f = open("python-latest.md", "a", encoding="utf-8")

for i in article_result:

    f.write("[" + i["title"] + "]")
    f.write("(" + "https://dev.to" + i["link"] + ")")
    f.write(
        " | Published on " + i["pub_date"] + " | " + str(i["reaction"]) + " reactions"
    )
    f.write("\n\n")

f.close()

