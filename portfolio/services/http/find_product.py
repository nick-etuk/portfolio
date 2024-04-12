# from bs4 import BeautifulSoup
import re
from icecream import ic
from portfolio.utils.init import log
from portfolio.utils.utils import first_number


def find_product(html, instrument):
    amount_class = "ProjectCell_assetsItemWorth"

    def subtotal(project, product):
        div = html.find("div", class_=re.compile("HeaderInfo_totalAsset.*"))
        result = div.text
        return result

    def wallet(project, product):
        """
        <div title="Wallet" class="ProjectCell_assetsItemNameText__l9fan view_ellipsis__Z0mvR">Wallet</div>
        <div class="ProjectCell_assetsItemWorth__EMwu2">$561</div>
        """
        result = ""
        div = html.find("div", title="Wallet")
        if div:
            # d2 = div.select(f"div[class^={amount_class}]")
            next_div = div.find_next_sibling(
                "div", class_=re.compile("ProjectCell_assetsItemWorth.*")
            )
            if next_div:
                result = next_div.text
        return result

    def beefy_v2(protocol_label, pool):
        div = html.find("div", id=protocol_label)
        if not div:
            return ""
        d2 = div.find_next("div", text=pool)
        if not d2:
            return ""
        d3 = d2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def beefy_v1(protocol_label):
        div = html.find("img", src=re.compile(protocol_label))
        if not div:
            return ""
        next_div = div.find_next("div", class_=re.compile(f"{amount_class}.*"))
        if next_div:
            result = next_div.text
        return result

    def beefy_ape_usdt(project, product):
        result = beefy_v2("bsc_beefy", "USDT + BUSD")
        # prevent clash with Babyswap, which has the same silouette (bsc_beefy, "USDT + BUSD")
        # but will have smaller balance of around $500
        if not result:
            return result
        amount = first_number(result.replace("$", "").replace(",", ""))
        return "" if float(amount) < 1500 else result

    def beefy_fantom(project, product):
        return beefy_v2("ftm_beefy", "USDC + DAI")

    def beefy_usd_plus(project, product):
        return beefy_v2("op_beefy", "USD+ + USDC")

    def beefy_baby_usdt(project, product):
        result = beefy_v2("bsc_beefy", "USDT + BUSD")
        # prevent clash with Apeswap, which has the same silouette (bsc_beefy, "USDT + BUSD")
        if not result:
            return result
        amount = first_number(result.replace("$", "").replace(",", ""))
        return "" if float(amount) > 1500 else result

    def aave(coin):
        div = html.find("div", id="avax_aave3")
        if not div:
            return ""
        d2 = div.find_next("div", text=coin)
        if not d2:
            return ""
        d3 = d2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def aave_usdt(project, product):
        return aave("USDt")

    def aave_usdc(project, product):
        return aave("USDC")

    def spooky(pool):
        div = html.find("div", id="ftm_spookyswap")
        if not div:
            return ""
        d2 = div.find_next("div", text=pool)
        if not d2:
            return ""
        d3 = d2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def spooky_usdc_dai(project, product):
        return spooky("USDC + DAI")

    def quickswap(pool):
        div = html.find("div", id="matic_quickswap")
        if not div:
            return ""
        d2 = div.find_next("div", text=pool)
        if not d2:
            return ""
        d3 = d2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def liquidity_pool(project, product):
        div1 = html.find("div", id=project)
        if not div1:
            return ""
        div2 = div1.find_next("div", text=product)
        if not div2:
            return ""
        span = div2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if project == "matic_stargate":
            span = div2.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not span:
            return ""
        result = span.text
        return result

    def liquidity_pool_4_col(project, product):
        div1 = html.find("div", id=project)
        if not div1:
            return ""
        div2 = div1.find_next("div", text=re.compile(product))
        div3 = div2.find_next("div", text=re.compile(product))
        div4 = div3.find_next("div", text=re.compile(product))
        if not div4:
            return ""
        result = div4.text
        return result

    def liquidity_pool_n_col(inst):
        text_before = ""
        if inst.product_id in ["UD_LP"]:
            text_before = "Liquidity Pool"
        cols = inst.html_table_columns
        project = inst.project

        if text_before:
            div0 = html.find(text=text_before).parent
            if div0:
                div1 = html.find_next("div", id=project)
                print("***** bp  1 *****")
                ic(div1)
            else:
                div1 = None
        else:
            div1 = html.find("div", id=project)
        if not div1:
            return ""
        row = div1.find_next("div", class_=re.compile("table_contentRow.*"))

        next_col = row.find_next("div")
        # print("col1:", next_col)
        for col in range(2, cols + 1):
            next_col = next_col.find_next_sibling("div")
            # print(f"col{col}: {next_col}")

        if not next_col:
            return ""
        result = next_col.text
        return result

    def liquidity_pool_5_col(project, product):
        return liquidity_pool_n_col(5, project, product)

    def liquidity_pool_3_col(project, product):
        return liquidity_pool_n_col(3, project, product)

    def z_liquidity_pool_5_col(project, product):
        div1 = html.find("div", id=project)
        if not div1:
            return ""
        row = div1.find_next("div", class_=re.compile("table_contentRow.*"))
        col1 = row.find_next("div")
        print("col1:", col1)

        col2 = col1.find_next_sibling("div")
        print("col2:", col2)

        col3 = col2.find_next_sibling("div")
        print("col3:", col3)

        col4 = col3.find_next_sibling("div")
        print("col4:", col4)

        col5 = col4.find_next_sibling("div")
        print("col5:", col5)

        if not col5:
            return ""
        result = col5.text
        return result

    def quickswap_usdc_dai(project, product):
        # return quickswap("USDC + DAI")
        return liquidity_pool("matic_quickswap", "USDC + DAI")

    def yearn_dai(project, product):
        # return quickswap("USDC + DAI")
        return liquidity_pool("ftm_yearn2", "DAI")

    prod_search = {
        "HTML total": subtotal,
        "Wallet": wallet,
        "Beefy Spiritswap DAI USDC": beefy_fantom,
        "Beefy Apeswap USDT BUSD": beefy_ape_usdt,
        "Beefy Veladrome USD Plus": beefy_usd_plus,
        "Aave Avlanche USDT": aave_usdt,
        "Aave Avlanche USDC": aave_usdc,
        "SpookySwap USDC + DAI": spooky_usdc_dai,
        "QuickSwap USDC + DAI": quickswap_usdc_dai,
        "Yearn DAI": yearn_dai,
        "Beefy Babyswap USDT BUSD": beefy_baby_usdt,
        "Stargate USDT": liquidity_pool_4_col,
        "Curve aave": liquidity_pool_5_col,
        "TETU USDC": liquidity_pool_3_col,
        "Penrose DAI": liquidity_pool_5_col,
        "Dystopia DAI": liquidity_pool_3_col,
    }

    prod_descr = instrument.product
    chain = instrument.chain
    project = instrument.project
    prod_label = instrument.html_label
    html_table_columns = instrument.html_table_columns

    project_label = chain + "_" + project
    if html_table_columns:
        search_results = liquidity_pool_n_col(instrument)
    else:
        search_results = prod_search[prod_descr](
            project=project_label, product=prod_label
        )

    product_amount_str = ""
    if search_results:
        product_amount_str = first_number(
            search_results.replace("$", "").replace(",", "")
        )

    return float(product_amount_str) if product_amount_str else 0
