class TotalClass:
    def __init__(
        self, solomon: int, personal: int, totals_dict: dict, totals_table: list
    ):
        self.solomon = round(solomon)
        self.personal = round(personal)
        self.combined = round(solomon + personal)
        self.totals_dict = totals_dict
        self.totals_table = totals_table
