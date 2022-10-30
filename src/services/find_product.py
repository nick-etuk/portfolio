from bs4 import BeautifulSoup
import re
from init import log
from utils import first_number


def find_product(html, prod_descr, chain, project, prod_label):

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
            "div", class_=re.compile("ProjectCell_assetsItemWorth.*"))
        result = div.text
        return result

    def beefy_bsc():
        return beefy_v2("bsc_beefy", "USDT + BUSD")

    def beefy_fantom():
        return beefy_v2("ftm_beefy", "USDC + DAI")

    def beefy_usd_plus():
        return beefy_v2("op_beefy", "USD+ + USDC")

    def beefy_baby_usdt():
        return beefy_v2("bsc_beefy", "USDT + BUSD")

    def aave(coin):
        div = html.find("div", id="avax_aave3")
        if not div:
            return ""
        d2 = div.find_next(
            "div", text=coin)
        if not d2:
            return ""
        d3 = d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def aave_usdt():
        return aave('USDt')

    def aave_usdc():
        return aave('USDC')

    def spooky(pool):
        div = html.find("div", id="ftm_spookyswap")
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

    def spooky_usdc_dai():
        return spooky("USDC + DAI")

    def quickswap(pool):
        div = html.find("div", id="matic_quickswap")
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

    def liquidity_pool(parent_label, child_label):
        div = html.find("div", id=parent_label)
        if not div:
            return ""
        d2 = div.find_next(
            "div", text=child_label)
        if not d2:
            return ""
        d3 = d2.find_next(
            "span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def quickswap_usdc_dai():
        # return quickswap("USDC + DAI")
        return liquidity_pool("matic_quickswap", "USDC + DAI")

    def yearn_dai():
        # return quickswap("USDC + DAI")
        return liquidity_pool("ftm_yearn2", "DAI")

    prod_search = {
        'HTML Subtotal': subtotal,
        'Wallet': wallet,
        'Beefy Spiritswap DAI USDC': beefy_fantom,
        'Beefy Apeswap USDT BUSD': beefy_bsc,
        'Beefy Veladrome USD Plus': beefy_usd_plus,
        'Aave Avlanche USDT': aave_usdt,
        'Aave Avlanche USDC': aave_usdc,
        'SpookySwap USDC + DAI': spooky_usdc_dai,
        'QuickSwap USDC + DAI': quickswap_usdc_dai,
        'Yearn DAI': yearn_dai,
        'Beefy Babyswap USDT BUSD': beefy_baby_usdt
    }

    project_label = chain + '_' + project
    result = prod_search[prod_descr]()
    amount = ""
    if result:
        amount = first_number(result.replace("$", "").replace(",", ""))
        return float(amount)
    return 0
