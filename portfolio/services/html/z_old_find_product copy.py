# from bs4 import BeautifulSoup
import re
from icecream import ic
from portfolio.utils.init import info, log, warn
from portfolio.utils.utils import first_number
from portfolio.services.html.selectors import liquidity_pool_v2


def find_product(html, row):
    """
    row = product_id, p.descr as product, p.chain,
    p.project, p.html_label, p.html_table_columns,
    act.amount as old_amount
    ac.descr as account, ac.address
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
        d3 = d2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
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
        amount = parent.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
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
        d3 = d2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
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
        d3 = d2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def spooky_usdc_dai(product, chain, project, html_label):
        return spooky("USDC + DAI")

    def quickswap(pool):
        # non-standard selector. unused.
        div = html.find("div", id="matic_quickswap")
        if not div:
            return ""
        d2 = div.find_next("div", text=pool)
        if not d2:
            return ""
        d3 = d2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
        if not d3:
            return ""
        result = d3.text
        return result

    def old2_liquidity_pool(product, chain, project, html_label):
        project_label = chain + "_" + project

        div1 = html.find("div", id=project_label)
        if not div1:
            return ""
        div2 = div1.find_next("div", text=project_label)
        if not div2:
            return ""
        span = div2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
        if project_label == "matic_stargate":
            span = div2.find_next("span", text=re.compile(r"\$\d+(?:\.\d+)?"))
        if not span:
            return ""
        result = span.text
        return result

    def liquidity_pool_4_col(product, chain, project, html_label):
        return liquidity_pool(
            html_table_columns=4,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def z_liquidity_pool_4_col(product, chain, project, html_label):
        project_label = chain + "_" + project

        div1 = html.find("div", id=project_label)
        if not div1:
            return ""
        div2 = div1.find_next("div", text=re.compile(project_label, re.IGNORECASE))
        div3 = div2.find_next("div", text=re.compile(project_label, re.IGNORECASE))
        div4 = div3.find_next("div", text=re.compile(project_label, re.IGNORECASE))
        if not div4:
            return ""
        result = div4.text
        return result

    def liquidity_pool(html_table_columns, product, chain, project, html_label):
        print("=>liquidity_pool_n_col")
        ic(product, chain, project, html_label)
        # non-standard selector
        project_label = chain + "_" + project
        marker = html.find("div", id=re.compile(project_label, re.IGNORECASE))
        if not marker:
            print(f"Div not found for {product} {project_label}")
            return ""
        product_div = marker.find_parent("div")
        ic(product_div)
        pool_components = html_label.split("+")
        farm_or_pool = ""
        if "liquidity pool" in product.lower():
            farm_or_pool = "liquidity pool"
        if "farming" in product.lower():
            farm_or_pool = "farming"

        if farm_or_pool:
            farm_marker = product_div.find(text=re.compile(farm_or_pool, re.IGNORECASE))
            if not farm_marker:
                return ""
            parent1 = farm_marker.find_parent("div")
            if not parent1:
                return ""
            parent2 = parent1.find_parent("div")
            if not parent2:
                return ""
            parent3 = parent2.find_parent("div")
            if not parent3:
                return ""
            parent = parent3.find_parent("div")
            if not parent:
                return ""

            ic(parent)
            # div1 = html.find_next(
            #     "div", id=re.compile(project_label, re.IGNORECASE)
            # )
            # print("***** bp  1 *****")
            # ic(div1)
            for component in pool_components:
                link = parent.find_next(
                    "a", text=re.compile(component.strip(), re.IGNORECASE)
                )
                if not link:
                    print(f"Link not found for {product} pool component {component}")
                    return ""
        else:
            return ""  # todo: implement case where text_before is not found
            # parent = html.find("div", id=re.compile(project_label, re.IGNORECASE))
            parent = ""

        if not parent:
            return ""
        table_row = parent.find_next("div", class_=re.compile("table_contentRow.*"))

        next_col = table_row.find_next("div")
        # print("col1:", next_col)
        for col in range(2, html_table_columns + 1):
            next_col = next_col.find_next_sibling("div")
            # print(f"col{col}: {next_col}")

        if not next_col:
            return ""
        return next_col.text

    def liquidity_pool_5_col(product, chain, project, html_label):
        return liquidity_pool(
            html_table_columns=5,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def liquidity_pool_3_col(product, chain, project, html_label):
        return liquidity_pool(
            html_table_columns=3,
            product=product,
            chain=chain,
            project=project,
            html_label=html_label,
        )

    def z_liquidity_pool_5_col(product, chain, project, html_label):
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

    def quickswap_usdc_dai(product, chain, project, html_label):
        # return quickswap("USDC + DAI")
        return old2_liquidity_pool("matic", "quickswap", "USDC + DAI")

    def yearn_dai(product, chain, project, html_label):
        # return quickswap("USDC + DAI")
        return old2_liquidity_pool("ftm", "yearn2", "DAI")

    def asset_summary(product, chain, project, html_label):
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
        "Wallet": wallet,
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
        # prod_label = row.html_label
        # project_label = chain + "_" + project
        # search_results = prod_search[prod_descr](project=project_label, product=prod_label)
        if row.html_table_columns:
            search_results = liquidity_pool(
                html_table_columns=row.html_table_columns,
                product=row.product,
                chain=row.chain,
                project=row.project,
                html_label=row.html_label,
            )
        else:
            search_results = asset_summary(
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
        ic(product_amount_str)
    else:
        if row.old_amount:
            warn(f"{row.account} ({row.address}):")
            # product_amount_str = input(f"{row.product} ({row.old_amount}):")
            warn(f"{row.product} not found in HTML")

    return float(product_amount_str) if product_amount_str else 0
