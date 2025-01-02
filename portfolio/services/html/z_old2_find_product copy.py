from datetime import datetime
import re
from dateutil.parser import parse
from icecream import ic
from portfolio.calc.changes.days_ago import days_ago
from portfolio.utils.init import info, log, warn
from portfolio.utils.utils import first_number
from portfolio.utils.config import db
from portfolio.services.html.selectors.liquidity_pool_v2 import (
    select_liquidity_pool,
)
from portfolio.services.html.selectors.liquidity_pool_v1 import select_liquidity_pool_v1
import sqlite3 as sl
from portfolio.utils.lib import (
    named_tuple_factory,
)


def find_product(html, row, account_id):
    """
    row = product_id, p.descr as product, p.chain,
    p.project, p.html_label, p.html_table_columns,
    """
    # if row.product not in ["Tetu USDC"]:
    #     return 0
    # ic(row)

    amount_class = "ProjectCell_assetsItemWorth"

    def subtotal(product, chain, project, html_label):
        div = html.find("div", class_=re.compile("HeaderInfo_totalAsset.*"))
        result = div.text
        return result

    def wallet(product, chain, project, html_label):
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

    def beefy_v1(protocol_label):
        # non-standard selector
        div = html.find("img", src=re.compile(protocol_label, re.IGNORECASE))
        if not div:
            return ""
        next_div = div.find_next("div", class_=re.compile(f"{amount_class}.*"))
        if next_div:
            result = next_div.text
        return result

    def beefy_v2(protocol_label, pool):
        print("=>beefy_v2")
        ic(protocol_label, pool)
        # non-standard selector
        div = html.find("div", id=re.compile(protocol_label, re.IGNORECASE))
        ic(div)
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

    def beefy_separate_pool_links(protocol_label, pool):
        # print("=>beefy_separate_pool_links")
        # ic(protocol_label, pool)
        # non-standard selector
        child = html.find("div", id=re.compile(protocol_label, re.IGNORECASE))
        if not child:
            return ""
        parent = child.find_parent("div")
        # ic(parent)
        if not parent:
            return ""
        pool_components = pool.split("+")
        for component in pool_components:
            link = parent.find_next(
                "a", text=re.compile(component.strip(), re.IGNORECASE)
            )
            if not link:
                print(f"Link not found for {component}")
                return ""
        amount = parent.find_next("span", text=re.compile("\$\d+(?:\.\d+)?"))
        if not amount:
            print("Amount not found in parent div")
            return ""
        return amount.text

    def beefy_ape_usdt(product, chain, project, html_label):
        # result = beefy_v2("bsc_beefy", "USDT + BUSD")
        # result = beefy_separate_pool_links({chain}_{project}, html_label)
        result = beefy_separate_pool_links("bsc_beefy", "USDT + BUSD")
        # prevent clash with Babyswap, which has the same silouette (bsc_beefy, "USDT + BUSD")
        # but Babyswap will have smaller balance of around $500
        if not result:
            return 0
        amount = first_number(result.replace("$", "").replace(",", ""))
        return "" if float(amount) < 1500 else result

    def beefy_fantom(product, chain, project, html_label):
        # return beefy_v2("ftm_beefy", "USDC + DAI")
        return beefy_separate_pool_links("ftm_beefy", "USDC + DAI")

    def beefy_usd_plus(product, chain, project, html_label):
        return beefy_separate_pool_links("op_beefy", "USD+ + USDC")

    def beefy_baby_usdt(product, chain, project, html_label):
        # result = beefy_v2("bsc_beefy", "USDT + BUSD")
        result = beefy_separate_pool_links("bsc_beefy", "USDT + BUSD")

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

    def aave_usdt(product, chain, project, html_label):
        return aave("USDt")

    def aave_usdc(product, chain, project, html_label):
        return aave("USDC")

    def spooky(pool):
        # non-standard selector
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

    def spooky_usdc_dai(product, chain, project, html_label):
        return spooky("USDC + DAI")

    def liquidity_pool_4_col(product, chain, project, html_label):
        return select_liquidity_pool(
            html_table_columns=4,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def liquidity_pool_5_col(product, chain, project, html_label):
        return select_liquidity_pool(
            html_table_columns=5,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def liquidity_pool_3_col(product, chain, project, html_label):
        return select_liquidity_pool(
            html_table_columns=3,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def quickswap_usdc_dai(product, chain, project, html_label):
        # return quickswap("USDC + DAI")
        return select_liquidity_pool_v1(html, "matic_quickswap", "USDC + DAI")

    def yearn_dai(product, chain, project, html_label):
        # return quickswap("USDC + DAI")
        return select_liquidity_pool_v1(html, "ftm_yearn2", "DAI")

    def select_asset_summary(product, chain, project, html_label):
        """
        <div title="Tetu" class="ProjectCell_assetsItemNameText__l9fan view_ellipsis__Z0mvR">Tetu</div>
        <div class="ProjectCell_assetsItemWorth__EMwu2">$24</div>
        """
        result = ""
        div = html.find("div", title=re.compile(project, re.IGNORECASE))
        if div:
            next_div = div.find_next_sibling(
                "div", class_=re.compile("ProjectCell_assetsItemWorth.*")
            )
            if next_div:
                result = next_div.text
        return result

    prod_search = {
        "Aave Avlanche USDC": aave_usdc,
        "Aave Avlanche USDT": aave_usdt,
        "Beefy Babyswap USDT BUSD": beefy_baby_usdt,
        "Beefy Apeswap USDT BUSD": beefy_ape_usdt,
        "Beefy Spiritswap DAI USDC": beefy_fantom,
        # "Curve aave": liquidity_pool_5_col,
        # "Beefy Spiritswap DAI USDC": asset_summary,
        "Beefy Veladrome USD Plus": beefy_usd_plus,
        # "Dystopia DAI": liquidity_pool_3_col,
        # "Grizzly Pancacke USDT": asset_summary,
        "HTML total": subtotal,
        # "Penrose DAI": liquidity_pool_5_col,
        "QuickSwap USDC + DAI": quickswap_usdc_dai,
        "SpookySwap USDC + DAI": spooky_usdc_dai,
        # "Stargate USDT": liquidity_pool_4_col,
        # "Tetu USDC": asset_summary,
        "HTML Wallet Total": wallet,
        "Yearn DAI": yearn_dai,
    }

    prod_descr = row.product

    if prod_descr in prod_search:
        search_results = prod_search[prod_descr](
            product=row.product,
            chain=row.chain,
            project=row.project,
            html_label=row.html_label,
        )
    else:
        if row.html_table_columns:
            search_results = select_liquidity_pool(
                html=html,
                columns=row.html_table_columns,
                product=row.product,
                chain=row.chain,
                project=row.project,
                html_label=row.html_label,
            )
        else:
            search_results = select_asset_summary(
                product=row.product,
                chain=row.chain,
                project=row.project,
                html_label=row.html_label,
            )

    product_amount_str = ""
    if search_results:
        product_amount_str = first_number(
            search_results.replace("$", "").replace(",", "")
        )
    else:
        last_seen_sql = """
        select act.amount, act.timestamp,
        ac.descr as account, ac.address
        from actual_total act
        inner join product p
        on p.product_id=act.product_id
        inner join account ac
        on ac.account_id=act.account_id
        where act.seq=
            (select max(seq) from actual_total
            where account_id=act.account_id
            and product_id=act.product_id
            )
        and ac.account_id=?
        and p.product_id=?
        and act.status='A'
        """
        with sl.connect(db) as conn:
            conn.row_factory = named_tuple_factory
            c = conn.cursor()
            last_seen_row = c.execute(last_seen_sql, (account_id, row.product_id)).fetchone()

        # if last_seen_row and last_seen_row.amount:
        if last_seen_row:
            # info(f"{amount_row.account} {amount_row.address}")
            # product_amount_str = input(f"{row.product} ({amount_row.old_amount}):")
            warn(
                f"{row.product} not found in HTML. Last seen {days_ago(datetime.now(), parse(last_seen_row.timestamp))} ago - {last_seen_row.amount} {last_seen_row.account} {last_seen_row.address}"
            )

    return float(product_amount_str) if product_amount_str else 0
