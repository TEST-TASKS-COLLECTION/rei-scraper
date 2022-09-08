import asyncio
import itertools
import aiohttp
import requests
import time
import pandas as pd
from bs4 import BeautifulSoup as bs

base_url = "https://www.rei.com"
query = "bags"

def fetch_urls(x, query):
    params = {
        "q": query,
        "json": True,
        "page": x
    }
    # r = requests.get(f"{base_url}/search", params = params).json()
    r = requests.get(f"{base_url}/search", params = params).json()
    results = r['searchResults']["results"]
    return [base_url + result['link'] for result in results]


# def parse_page_data(url) -> dict:
def parse_page_data(res) -> dict:
    # res = requests.get(url).text
    soup = bs(res, "html.parser")
    try:
        price = soup.select_one(".price-value").text.strip()
        title = soup.select_one(".product-title").text.strip()
        rating = soup.find("span", class_="cdr-rating__number_11-3-1").text.strip()
        reviewers = soup.select_one(".cdr-rating__count_11-3-1 :nth-child(2)").text
        data = {
            # "url": url,
            "title": title,
            "price": price,
            "rating": rating,
            "reviewers": reviewers
        }
        return data
    except AttributeError as e:
        # price = soup.find("title").text
        # print(price)
        # # price = soup.find("span", class_="compare-price__display").text.strip()
        # title = soup.select_one(".main-product-details-header__brand").text.strip()
        # rating = soup.find("div", class_="bv_avgRating_component_container notranslate").text.strip()
        # reviewers = soup.select_one(".bv_numReviews_text").text
        # data = {
        #     "url": url,
        #     "title": title,
        #     "price": price,
        #     "rating": rating,
        #     "reviewers": reviewers
        # }
        # return data
        print("COULDN'T PARSE")
        # data = {
        #     # "url": url,
        #     "error": str(e)
        # }
        return None
        # return data

def sync_way():
    urls = [fetch_urls(i, query) for i in range(1,3)]
    urls = list(itertools.chain.from_iterable(urls))
    for url in urls:
        print(parse_page_data(url))
    # print(parse_page_data("https://www.rei.com/rei-garage/product/214560/osprey-archeon-28-pack"))

async def get_page(session, url):
    return await session.get(url)

async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url))
        task.customData = url
        tasks.append(task)
    
    return await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

async def main(urls):
    async with aiohttp.ClientSession() as session:
        data, _ = await get_all(session, urls)
        results = []
        for d in data:
            # print(d.result().status)
            result = parse_page_data(await d.result().text())
            if not result:
                print("THIS IS THE FAULTY URL", d.customData)
            else:
                results.append(result)

    return results


if __name__ == "__main__":
    # Target time: TIME TAKEN 47.44092607498169
    # OBTAINED TIME: TIME TAKEN 24.489693641662598
    then = time.time()
    # sync_way()
    # urls = []
    
    urls = [fetch_urls(i, query) for i in range(1,3)]
    urls = list(itertools.chain.from_iterable(urls))
    results = asyncio.run(main(urls))
    now = time.time()
    df = pd.DataFrame(results)
    df.to_csv("data/async_results.csv", index=False)
    print(results)
    print(f"TIME TAKEN {now - then}")