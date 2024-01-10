from dotenv import dotenv_values
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class Article:
    def __init__(
        self,
        id: int,
        url: str,
        title: str = None,
        subtitle: str = None,
        authors: List[str] = None,
        published: str = None,
        content: str = None,
    ):
        self.id = id
        self.url = url
        self.title = title
        self.subtitle = subtitle
        self.authors = authors
        self.published = published
        self.content = content


def get_archive(
    base_url: str, sid_cookie: str, limit: int = 50, offset: int = 0
) -> List[dict]:
    base_url_with_slash = base_url if base_url.endswith("/") else base_url + "/"
    archive_url = (
        base_url_with_slash + f"api/v1/archive?sort=new&limit={limit}&offset={offset}"
    )
    headers = {"cookie": f"substack.sid={sid_cookie}"}
    response = requests.get(archive_url, headers=headers)
    return response.json()


def getArticleUrls(base_url: str, sid_cookie: str) -> Dict[int, Article]:
    articles = {}
    limit = 50  
    offset = 0
    is_last_page = False
    while(not is_last_page):
        archive = get_archive(base_url, sid_cookie, offset=offset, limit=limit)
        is_last_page = len(archive) < limit
        for article in archive:
            parsed_article = Article(
                id=article["id"],
                url=article["canonical_url"],
                title=article["title"],
                subtitle=article["subtitle"],
                authors=[author["name"] for author in article["publishedBylines"]],
                published=article["post_date"]
            )
            if parsed_article.id not in articles:
                articles[parsed_article.id] = parsed_article
        offset += limit
    return articles


def main():
    env = dotenv_values(".env")
    articles = getArticleUrls(env["SUBSTACK_BASE_URL"], env["SUBSTACK_SID_COOKIE"])
    print(f"Found {len(articles)} articles")


if __name__ == "__main__":
    main()
