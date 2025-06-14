from portfolio.utils.init import info

def match_check(matches, label):
    if len(matches) == 1:
        return True

    if len(matches) > 1:
        info(f"{label}: multiple matches found")
        for match in matches:
            info(f"{match['product_id']} {match['product']}")
        return False
    if len(matches) == 0:
        joined_input = " ".join(input)
        info(f"{label}: {joined_input} not found")
        return False
    return False