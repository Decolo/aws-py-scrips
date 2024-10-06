import requests
from bs4 import BeautifulSoup
import urllib.parse
import asyncio
from manipulate_dynamodb import insert_item_no_repeat_href
from scraper_lemon8_content import scrape_content
import db_utils

def scrape_page(**params):
    url = params["url"]
    keyword = params["keyword"]
    print(f"Scraping URL: {url}")
    print(f"Keyword: {keyword}")

    response = requests.get(url, allow_redirects=True)

    if response.status_code == 200:
        # print(response.content)
        soup = BeautifulSoup(response.content, "html.parser")

        posts = soup.find_all(class_="discover-immersive-article")

        # results = []

        for post in posts:
            if post and "href" in post.attrs:
                href = post.attrs["href"]
                if len(href) == 0:
                    continue

                imgCovers = post.select(".swiper-wrapper img")
                images = list(map(lambda img: img.attrs["src"], imgCovers))

                if len(images) == 0:
                    continue

                titleEls = post.select(".article-body .title")
                title = (
                    titleEls[0].text.strip() if (titleEls and len(titleEls) > 0) else ""
                )

                shortContentEls = post.select(".article-body .short-content")
                shortContent = (
                    shortContentEls[0].text.strip()
                    if (shortContentEls and len(shortContentEls) > 0)
                    else ""
                )
                
                id = insert_item_no_repeat_href(
                    {
                        "title": title,
                        "short_content": shortContent,
                        "href": href,
                        "images": images,
                    }
                )

                content_ready = scrape_content(id=id, href=href)
                
                if not content_ready:
                    db_utils.delete_item_by_id(id)
                else:
                    print(f"\n{href} item saved to dynamodb")

        # with open(f"../data/{keyword}-feed.json", "w", encoding="utf-8") as f:
        #     json.dump(results, f, ensure_ascii=False, indent=4)
        #     print(f"\nFull feed list saved to '{keyword}-feed.json'")

    else:
        print(f"Failed to fetch page: {response.status_code}")


async def scrape_run():
    keyword = [
        # "thailand",
        # "thailand trip",
        # "japan",
        # "japan trip",
        # "singapore",
        # "singapore trip",
        # "malaysia",
        # "malaysia trip",
        # "indonesia",
        # "indonesia trip",
        # "philippines",
        # "philippines trip",
        # "taiwan",
        # "taiwan trip",
        # "hong-kong",
        # "hong-kong trip",
        # "china",
        "china trip",
        "vietnam",
        "vietnam trip",
        "italy",
        "italy trip",
        "france",
        "france trip",
        "greece",
        "greece trip",
        "spain",
        "spain trip",
        "portugal",
        "portugal trip",
        "finland",
        "finland trip",
        "sweden",
        "sweden trip",
        "norway",
        "norway trip",
        "turkey",
        "turkey trip",
        "egypt",
        "egypt trip",
        "morocco",
        "morocco trip",
        "kenya",
        "kenya trip",
    ]
    regions = ["sg", "us"]

    for region in regions:
        for kw in keyword:
            _kw = urllib.parse.quote(kw)

            await asyncio.sleep(1)

            scrape_page(
                **{
                    "url": f"https://www.lemon8-app.com/discover/{_kw}?region={region}",
                    "keyword": _kw,
                }
            )


asyncio.run(scrape_run())
