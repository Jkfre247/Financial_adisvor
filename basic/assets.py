from .imports import *

class BondAsset:
    """Bazowa klasa dla obligacji."""
    def __init__(self, inflation, yield_rate):
        self.inflation = inflation
        self.yield_rate = yield_rate

    def calculate_growth_factor(self, period):
        """
        Liczymy roczny wzrost obligacji, a następnie
        potęgujemy do okresu 'period' (np. 0.085 roku).
        """
        annual_growth = 1 + self.inflation + self.yield_rate
        return annual_growth ** period


class InvestmentStrategy:
    """Strategia inwestycyjna wspólna."""
    def __init__(self, rise_investment=1):
        # rise_investment - mnożnik rocznego wzrostu wkładu
        self.rise_investment = rise_investment
        self.rise = 1  # to może być użyte do sterowania wzrostem

    def yearly_investment_rise(self, rise):
        """Ustawiamy roczny wzrost inwestycji."""
        self.rise = rise

    def investment_growth(self):
        """Zwiększa inwestycję roczną o ustalony mnożnik, aby nie przekraczać pewnego progu."""
        if self.rise_investment * self.rise < 3:
            self.rise_investment *= self.rise


class Asset:
    """Bazowa klasa do pobierania cen aktywów z YF (np. złoto, ETFy, krypto)."""
    def __init__(self, ticker):
        self.ticker = ticker
        self.price = 0

    def fetch_price(self, date):
        """
        Pobiera cenę aktywa na dany 'date' (w przybliżeniu)
        posiłkując się 30 dniami do przodu.
        """
        end_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=30)).strftime("%Y-%m-%d")
        data = yf.download(self.ticker, start=date, end=end_date, progress=False)
        if not data.empty:
            # Pierwszy 'Close' który nie jest NaN
            return data['Close'].dropna().iloc[0].item()
        else:
            raise ValueError(f"Unable to fetch price for {self.ticker} on date: {date}")
