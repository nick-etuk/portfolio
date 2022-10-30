import logging
from bs4 import BeautifulSoup
import re


def find_product(product, html):
    log = logging.getLogger(__name__)

    def subtotal():
        div = html.find("div", class_=re.compile("HeaderInfo_totalAsset.*"))
        result = div.text
        return result

    def wallet():
        div = html.find("div", title='Wallet').find_next_sibling(
            "div", class_=re.compile("ProjectCell_assetsItemWorth.*"))
        result = div.text
        return result

    def beefy_v2(protocol_label, pool):
        div = html.find("div", id=protocol_label)
        if not div:
            return ""
        d2 = div.find_next(
            "div", text=pool)
        if not d2:
            return ""
        d3 = d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def beefy_v1(protocol_label):
        div = html.find("img", src=re.compile(protocol_label))
        if not div:
            return ""
        div.find_next(
            "div", class_=re.compile("ProjectCell_assetsItemWorth.*")
        result=div.text
        return result

    def beefy_bsc():
        return beefy_v2("bsc_beefy", "USDT + BUSD")

    def beefy_fantom():
        return beefy_v2("ftm_beefy", "USDC + DAI")

    def aave(coin):
        div=html.find("div", id="avax_aave3")
        if not div:
            return ""
        d2=div.find_next(
            "div", text=coin)
        if not d2:
            return ""
        d3=d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result=d3.text
        return result

    def aave_usdt():
        return aave('USDt')

    def aave_usdc():
        return aave('USDC')

    def spooky(pool):
        div=html.find("div", id="ftm_spookyswap")
        if not div:
            return ""
        d2=div.find_next(
            "div", text=pool)
        if not d2:
            return ""
        d3=d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result=d3.text
        return result

    def spooky_usdc_dai():
        return spooky("USDC + DAI")

    def quickswap(pool):
        div=html.find("div", id="matic_quickswap")
        if not div:
            return ""
        d2=div.find_next(
            "div", text=pool)
        if not d2:
            return ""
        d3=d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result=d3.text
        return result

    def quickswap_usdc_dai():
        return quickswap("USDC + DAI")

    prod_search={
        'HTML Subtotal': subtotal,
        'Wallet': wallet,
        'Beefy USDC DAI': beefy_bsc,
        'Beefy USDT USD': beefy_fantom,
        'Aave Avlanche USDT': aave_usdt,
        'Aave Avlanche USDC': aave_usdc,
        'SpookySwap USDC + DAI': spooky_usdc_dai,
        'QuickSwap USDC + DAI': quickswap_usdc_dai
    }

    result=prod_search[product]()
    amount=0
    if result:
        amount=result.replace("$", "").replace(",", "")

    return float(amount)
