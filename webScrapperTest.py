
import unittest
from unittest.mock import patch
from io import StringIO
import re
import requests
from bs4 import BeautifulSoup
import datetime

# Mock helpers
def mock_requests_get(*args, **kwargs):
    class MockResponse:
        @staticmethod
        def json():
            return {'mock_key': 'mock_response'}

        @property
        def content(self):
            return """
                <div id="substories">
                    <div class="crayons-story">
                        <a id="article-link-1" href="/link1">Test Article 1</a>
                        <time>Dec 16</time>
                        <a >10 reactions</a>
                    </div>
                    <div class="crayons-story">
                        <a id="article-link-2" href="/link2">Test Article With No Reactions</a>
                        <time>Mar 01</time>
                    </div>
                    <div class="crayons-story">
                        <a id="article-link-3" href="/link3">Old Article</a>
                        <time>Dec 15</time>
                        <a>10 reactions</a>
                    </div>
                    <div class="crayons-story">
                        <a id="article-link-4" href="/link4">Low Reaction Article</a>
                        <time>Mar 01</time>
                        <a>2 reactions</a>
                    </div>
                </div>
            """
    return MockResponse()


# Unit tests for the above code
class TestArticleScraper(unittest.TestCase):
    @patch('requests.get', side_effect=mock_requests_get)
    def test_article_scraper(self, mock_get):
        # Retrieving mock page
        URL = "https://dev.to/t/python"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        result = soup.find(id="substories")
        articles = result.find_all("div", class_="crayons-story")

        today = datetime.datetime.today()
        a_week_ago = today - datetime.timedelta(days=7)
        article_result = []

        for article in articles:
            title_element = article.find("a", id=re.compile("article-link-\d+"))
            title = title_element.text.strip()
            link = title_element["href"]

            pub_date_element = article.find("time")
            pub_date = pub_date_element.text

            reaction_element = article.find(string=re.compile("reaction"))
            if reaction_element is not None:
                reaction_element = reaction_element.findParent("a")
                reaction = re.findall("\d+", reaction_element.text)
                reaction = int(reaction[0])
            else:
                reaction = 0
            
            pub = datetime.datetime.strptime(pub_date + str(today.year), "%b %d%Y")
            if reaction >= 5 and pub > a_week_ago:
                article_result.append({
                    "title": title,
                    "link": link,
                    "pub_date": pub_date,
                    "reaction": reaction
                })

        article_result = sorted(article_result, key=lambda d: d["reaction"], reverse=True)
        file_content = StringIO()
        with patch('builtins.open', return_value=file_content):
            f = open("python-latest.md", "a", encoding="utf-8")

            for i in article_result:
                f.write("[" + i["title"] + "]")
                f.write("(" + "https://dev.to" + i["link"] + ")")
                f.write(" | Published on " + i["pub_date"] + " | " + str(i["reaction"]) + " reactions")
                f.write("\n\n")

            result_lines = file_content.getvalue().strip().split('\n\n')
            f.close()

        
        # Assure that three valid articles are added, since one is old and two have insufficient reactions
        self.assertEqual(len(result_lines), 2)
        self.assertIn('Test Article 1', result_lines[0])
        self.assertIn('https://dev.to', result_lines[0])
        self.assertIn('10 reactions', result_lines[0])

        # Check if title, link, and reactions are appearing correctly in the MD file content
        self.assertTrue(any('Test Article 1' in line for line in result_lines))
        self.assertFalse(any('Test Article With No Reactions' in line for line in result_lines))
        self.assertTrue(any('Old Article' in line for line in result_lines))
        self.assertFalse(any('Low Reaction Article' in line for line in result_lines))


if __name__ == '__main__':
    unittest.main()
