import json
import time
import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from dataclasses import asdict, dataclass

url = "https://habr.com/ru/articles/top/daily/"


def get_url_html(url: str) -> str:
    res = requests.get(url, headers={"User-Agent": UserAgent().google})
    return res.text


def get_soup(html_text: str) -> BeautifulSoup:
    return BeautifulSoup(html_text, features="lxml")


@dataclass
class ArticleDATA:
    title: str
    views: str
    url: str
    text: str


def get_article_text(article_url: str) -> str:
    html = requests.get(article_url, headers={"User-Agent": UserAgent().google}).text
    soup = BeautifulSoup(html, "lxml")
    article_body = soup.find("div", class_="tm-article-body")
    for element in article_body.find_all(["script", "style", "code"]):
        element.decompose()
    return article_body.get_text(separator="\n", strip=True)


def get_all_habr_posts(soup: BeautifulSoup) -> list[ArticleDATA]:
    posts_data = []
    all_articles_soup = soup.find_all(name="article", class_="tm-articles-list__item")
    for article_soup in all_articles_soup:
        article_title = (
            article_soup.find("a", class_="tm-title__link").find("span").text
        )
        article_views = article_soup.find("span", class_="tm-icon-counter__value").text
        article_url_tag = article_soup.find("a", class_="tm-title__link")
        article_url = article_url_tag.get("href")
        article_url = f"https://habr.com{article_url}"
        try:
            article_text = get_article_text(article_url)
        except Exception as e:
            print(f"Error parsing {article_url}: {e}")
            continue
        time.sleep(0.5)
        posts_data.append(
            ArticleDATA(
                title=article_title,
                views=article_views,
                url=article_url,
                text=article_text,
            )
        )
    return posts_data


def main():
    html = get_url_html(url)
    soup = get_soup(html)
    posts_data = get_all_habr_posts(soup)
    with open("articles.json", "w", encoding="utf-8") as file:
        json.dump(
            [asdict(post) for post in posts_data], file, ensure_ascii=False, indent=4
        )


if __name__ == "__main__":
    main()
