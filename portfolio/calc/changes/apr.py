def calc_apr(principal: float, change: float, days: float):
    if days == 0 or principal == 0:
        return 0
    years = days / 365
    apr = (change / (years * principal)) * 100
    return apr
