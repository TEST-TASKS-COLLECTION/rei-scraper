from requests_html import HTMLSession
import chompjs
import itertools
import pandas as pd

base_url = "https://www.rei.com/"
# "https://www.rei.com/search?json=true&page=2&q=bags"
def fetch(x, query):
    r = s.get(f"{base_url}/search?json=true&page={x}&q={query}").json()
    results = r['searchResults']["results"]
    return [result['cleanTitle'] for result in results]

def another_fetch(x):
    baseurl = "https//www.rei.com"
    r = s.get(f"{base_url}/c/hiking-backpacks?page={x}")
    results = [base_url + link.attrs['href'] for link in r.html.find("#search-results > ul > li > a")]
    return list(set(results))

def parseproduct(url):
    r = s.get(url)
    details = r.html.find('script[type="application/ld+json"]', first=True)
    data = chompjs.parse_js_object(details.text)
    return data

def main():
    urls = [another_fetch(x) for x in range(1,3)]
    product_urls = list(itertools.chain.from_iterable(urls))
    return [parseproduct(url) for url in product_urls]

if __name__ == "__main__":
    s = HTMLSession()
    # print(fetch(1, "bags"))
    # print(another_fetch(1))
    # print(parseproduct(another_fetch(1)[0]))
    df = pd.json_normalize(main())
    df = df[["name", "description", "brand.name", "aggregateRating.ratingValue", "aggregateRating.reviewCount"]]
    print(df.columns)
    df.to_csv("data/first.csv", index=False)
    print("DONE!!")