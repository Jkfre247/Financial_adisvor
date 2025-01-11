from .imports import *
import yfinance as yf
import pandas as pd

def fetch_financial_data(ticker):
    stock = yf.Ticker(ticker)
    return {
        "info": stock.info,
        "financials": stock.financials,
        "balance_sheet": stock.balance_sheet,
        "cashflow": stock.cashflow,
        "history": stock.history(period="1d"),
    }

def extract_key_metrics(data):
    # Obecna cena akcji
    try:
        current_price = data["history"]["Close"][-1]
    except (IndexError, KeyError):
        current_price = None

    # Net Income (zysk netto)
    try:
        net_income = data["financials"].loc["Net Income"].iloc[0]
    except (KeyError, IndexError):
        net_income = None

    # Revenue (przychód)
    try:
        revenue = data["financials"].loc["Total Revenue"].iloc[0]
    except (KeyError, IndexError):
        revenue = None

    # EBITDA
    try:
        ebitda = data["financials"].loc["Ebitda"].iloc[0]
    except (KeyError, IndexError):
        ebitda = data["info"].get("ebitda", None)

    # Koszty roczne (Operating Expense)
    try:
        operating_expense = data["financials"].loc["Operating Expense"].iloc[0]
    except (KeyError, IndexError):
        operating_expense = None

    # Wolne przepływy pieniężne (FCF)
    try:
        operating_cf = data["cashflow"].loc["Total Cash From Operating Activities"].iloc[0]
        capex = data["cashflow"].loc["Capital Expenditures"].iloc[0]
        free_cash_flow = operating_cf + capex  # capex jest zwykle ujemny
    except (KeyError, IndexError):
        free_cash_flow = data["info"].get("freeCashflow", None)

    # Dodatkowe wskaźniki
    shares_outstanding = data["info"].get("sharesOutstanding", None)
    market_cap = data["info"].get("marketCap", None)
    total_debt = data["info"].get("totalDebt", None)
    total_cash = data["info"].get("totalCash", None)

    return {
        "current_price": current_price,
        "net_income": net_income,
        "revenue": revenue,
        "ebitda": ebitda,
        "operating_expense": operating_expense,
        "free_cash_flow": free_cash_flow,
        "shares_outstanding": shares_outstanding,
        "market_cap": market_cap,
        "total_debt": total_debt,
        "total_cash": total_cash,
    }

def calculate_ratios(metrics):
    # P/E i EPS
    try:
        eps = metrics["net_income"] / metrics["shares_outstanding"]
        pe = metrics["current_price"] / eps if (metrics["current_price"] and eps) else None
    except (TypeError, ZeroDivisionError):
        eps, pe = None, None

    # P/S
    ps = (metrics["market_cap"] / metrics["revenue"]) if (
        metrics["market_cap"] and metrics["revenue"]) else None

    # EV/EBITDA
    if (metrics["market_cap"] and metrics["total_debt"] is not None
        and metrics["total_cash"] is not None and metrics["ebitda"]):
        enterprise_value = metrics["market_cap"] + metrics["total_debt"] - metrics["total_cash"]
        try:
            ev_ebitda = enterprise_value / metrics["ebitda"]
        except ZeroDivisionError:
            ev_ebitda = None
    else:
        ev_ebitda = None

    # P/FCF
    p_fcf = (metrics["market_cap"] / metrics["free_cash_flow"]) if (
        metrics["market_cap"] and metrics["free_cash_flow"]) else None

    return {
        "P/E": pe,
        "P/S": ps,
        "EV/EBITDA": ev_ebitda,
        "P/FCF": p_fcf,
        "EPS": eps
    }

def calculate_fair_values(metrics, ratios):
    fair_prices = []

    # Cena fair_value według P/E
    if ratios["EPS"] is not None:
        fair_price_pe = 15 * ratios["EPS"]
        fair_prices.append(fair_price_pe)
    else:
        fair_price_pe = None

    # Cena fair_value według P/S
    if metrics["revenue"] and metrics["shares_outstanding"]:
        revenue_per_share = metrics["revenue"] / metrics["shares_outstanding"]
        fair_price_ps = revenue_per_share * 3
        fair_prices.append(fair_price_ps)
    else:
        fair_price_ps = None

    # Cena fair_value według EV/EBITDA
    if (metrics["ebitda"] and metrics["total_debt"] is not None
        and metrics["total_cash"] is not None and metrics["shares_outstanding"]):
        fair_ev = 8 * metrics["ebitda"]
        fair_mc = fair_ev - metrics["total_debt"] + metrics["total_cash"]
        if metrics["shares_outstanding"]:
            fair_price_ev_ebitda = fair_mc / metrics["shares_outstanding"]
            fair_prices.append(fair_price_ev_ebitda)
        else:
            fair_price_ev_ebitda = None
    else:
        fair_price_ev_ebitda = None

    # Cena fair_value według P/FCF
    if metrics["free_cash_flow"] and metrics["shares_outstanding"]:
        fair_mc_fcf = metrics["free_cash_flow"] * 15
        fair_price_fcf = fair_mc_fcf / metrics["shares_outstanding"]
        fair_prices.append(fair_price_fcf)
    else:
        fair_price_fcf = None

    # Średnia z dostępnych fair_price
    fair_price_average = sum(fair_prices) / len(fair_prices) if fair_prices else None

    return {
        "fair_price_PE": fair_price_pe,
        "fair_price_PS": fair_price_ps,
        "fair_price_EV_EBITDA": fair_price_ev_ebitda,
        "fair_price_P_FCF": fair_price_fcf,
        "fair_price_average": fair_price_average,
    }

def fair_price_estimation(ticker):
    data = fetch_financial_data(ticker)
    metrics = extract_key_metrics(data)
    ratios = calculate_ratios(metrics)
    fair_values = calculate_fair_values(metrics, ratios)

    # Łączymy wszystko w jeden słownik:
    return {
        **metrics,
        **ratios,
        **fair_values,
    }
