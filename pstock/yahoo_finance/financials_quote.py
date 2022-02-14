import typing as tp


def get_income_statement_data_from_financials_quote(
    financials_quote: tp.Dict[str, tp.Any],
    key: tp.Literal[
        "incomeStatementHistory", "incomeStatementHistoryQuarterly"
    ] = "incomeStatementHistory",
) -> tp.List[tp.Dict[str, tp.Any]]:

    statement_history = financials_quote.get(key, {}).get("incomeStatementHistory", [])
    if not statement_history:
        return []

    return [
        {
            "date": statement.get("endDate", {}).get("raw"),
            "ebit": statement.get("ebit", {}).get("raw"),
            "total_revenue": statement.get("totalRevenue", {}).get("raw"),
            "gross_profit": statement.get("grossProfit", {}).get("raw"),
        }
        for statement in statement_history
    ]
