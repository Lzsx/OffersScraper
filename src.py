import aiohttp
import asyncio
from bs4 import BeautifulSoup, SoupStrainer
import pandas as pd

STRAINER = SoupStrainer("div", class_="promotion-item__description")

async def get_products(div) -> str:
    products = map(lambda x: x.text,div.find_all("p", class_="promotion-item__title"))
    return list(products)

async def get_prices(div) -> str:
    prices_area = div.find_all("div",class_="andes-money-amount-combo__main-container")
    a = []
    for area in prices_area:
        price = area.find("span", class_="andes-money-amount__fraction")
        if (cents := area.find("span",class_="andes-money-amount__cents andes-money-amount__cents--superscript-24")):
            a.append(f"R$ {price.text},{cents.text}")
        else:
            a.append(f"R$ {price.text}")
    return a

async def get_response(client: aiohttp.ClientSession, url: str) -> aiohttp.ClientResponse:
    r = await client.get(url)
    return r


async def scrape(pricelist: list, productlist: list, r: aiohttp.ClientResponse) -> None:
    soup = BeautifulSoup(await r.text(), "lxml", parse_only=STRAINER)
    pricelist.extend(await get_prices(soup))
    productlist.extend(await get_products(soup))


async def save_file(prices: list, products: list, filename="result.xlsx") -> None:
    data = {"Produto": products, "Preço Unitário": prices}
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
