from .assets import *
from .imports import *

class GrowthPortfolio:
    """
    Portfel „ryzykowny”: ETFy, krypto, złoto, obligacje.
    """
    def __init__(
        self,
        gold_pro=0.15,
        etf_em_pro=0.2,
        etf_msci_pro=0.3,
        bonds_pro=0.3,
        crypto_pro=0.05
    ):
        self.gold_pro = gold_pro
        self.etf_em_pro = etf_em_pro
        self.etf_msci_pro = etf_msci_pro
        self.bonds_pro = bonds_pro
        self.crypto_pro = crypto_pro

        # Liczba jednostek
        self.gold_units = 0
        self.etf_em_units = 0
        self.etf_msci_units = 0
        self.crypto_units = 0
        # Obligacje przetrzymujemy jako jedną wartość (PLN)
        self.bonds = 0

        # Bieżąca cena (aktualizowana w symulacji)
        self.gold_price = 0
        self.etf_em_price = 0
        self.etf_msci_price = 0
        self.crypto_price = 0

    def allocate_investment(self, total_investment):
        allocations = {
            "gold":     total_investment * self.gold_pro,
            "etf_em":   total_investment * self.etf_em_pro,
            "etf_msci": total_investment * self.etf_msci_pro,
            "bonds":    total_investment * self.bonds_pro,
            "crypto":   total_investment * self.crypto_pro
        }

        if self.gold_price > 0:
            self.gold_units += allocations["gold"] / self.gold_price
        if self.etf_em_price > 0:
            self.etf_em_units += allocations["etf_em"] / self.etf_em_price
        if self.etf_msci_price > 0:
            self.etf_msci_units += allocations["etf_msci"] / self.etf_msci_price
        if self.crypto_price > 0:
            self.crypto_units += allocations["crypto"] / self.crypto_price

        self.bonds += allocations["bonds"]

    def calculate_total_value(self):
        gold_value = self.gold_units * self.gold_price
        etf_em_value = self.etf_em_units * self.etf_em_price
        etf_msci_value = self.etf_msci_units * self.etf_msci_price
        crypto_value = self.crypto_units * self.crypto_price
        return gold_value + etf_em_value + etf_msci_value + crypto_value + self.bonds


class GrowthSimulation:
    """Symulacja dla portfela bardziej ryzykownego (growth)."""
    def __init__(self, portfolio, assets, bond_asset, strategy, start_year=2015, years=10):
        """
        :param portfolio: obiekt GrowthPortfolio
        :param assets: słownik Assetów, np. {"gold": Asset("GC=F"), ...}
        :param bond_asset: np. BondAsset(inflation, yield_rate)
        :param strategy: InvestmentStrategy
        :param start_year: rok startowy
        :param years: ile lat do przodu
        """
        self.portfolio = portfolio
        self.assets = assets   # np. {"gold": Asset("GC=F"), "crypto": Asset("BTC-USD"), ...}
        self.bond_asset = bond_asset
        self.strategy = strategy
        self.start_year = start_year
        self.years = years

        self.recalibration_period = 0.085
        self.recalibration_bool = True
        self.previous_check = f"{self.start_year}-01-01"

    def set_recalibration(self, bool_flag, period):
        """Ustawia, czy rebalancing portfela ma być wykonywany i co ile."""
        self.recalibration_bool = bool_flag
        self.recalibration_period = period

    def update_prices(self, current_date):
        """
        Pobiera ceny dla: gold, etf_em, etf_msci, crypto
        """
        for asset_name, asset_obj in self.assets.items():
            try:
                price = asset_obj.fetch_price(current_date)
                setattr(self.portfolio, f"{asset_name}_price", price)
            except ValueError as e:
                print(e)
                setattr(self.portfolio, f"{asset_name}_price", 0)

        # Obligacje rosną wedle inflacji i yield
        growth_factor = self.bond_asset.calculate_growth_factor(self.recalibration_period)
        self.portfolio.bonds *= growth_factor

    def run(self, yearly_investment):
        results = []
        start_date = self.previous_check
        current_date = self.previous_check
        end_date = (
            datetime.strptime(current_date, "%Y-%m-%d")
            + timedelta(days=int(self.years * 365))
        ).strftime("%Y-%m-%d")

        recalibration_days = int(self.recalibration_period * 365)
        total_invested = yearly_investment

        while current_date < end_date:
            current_datetime = datetime.strptime(current_date, "%Y-%m-%d")

            # Pierwsza iteracja: omijamy aktualizację i inwestycję
            if current_date == start_date:
                print(f"Data startowa {start_date} - pomijam aktualizację i inwestycję.")
                current_date = (
                    datetime.strptime(current_date, "%Y-%m-%d")
                    + timedelta(days=recalibration_days)
                ).strftime("%Y-%m-%d")

                self.update_prices(current_date)
                self.portfolio.allocate_investment(yearly_investment * self.strategy.rise_investment)
                continue

            # Aktualizacja cen
            self.update_prices(current_date)

            # Alokacja kapitału w styczniu
            if current_datetime.month == 1:
                self.portfolio.allocate_investment(yearly_investment * self.strategy.rise_investment)

            # Rebalancing w styczniu
            if current_datetime.month == 1 and self.recalibration_bool:
                total_value = self.portfolio.calculate_total_value()
                # Złoto
                if self.portfolio.gold_price > 0:
                    self.portfolio.gold_units = (total_value * self.portfolio.gold_pro) / self.portfolio.gold_price
                # ETF EM
                if self.portfolio.etf_em_price > 0:
                    self.portfolio.etf_em_units = (total_value * self.portfolio.etf_em_pro) / self.portfolio.etf_em_price
                # ETF MSCI
                if self.portfolio.etf_msci_price > 0:
                    self.portfolio.etf_msci_units = (total_value * self.portfolio.etf_msci_pro) / self.portfolio.etf_msci_price
                # Crypto
                if self.portfolio.crypto_price > 0:
                    self.portfolio.crypto_units = (total_value * self.portfolio.crypto_pro) / self.portfolio.crypto_price
                # Bonds
                self.portfolio.bonds = total_value * self.portfolio.bonds_pro

            total_value = self.portfolio.calculate_total_value()
            results.append({
                "Date": current_date,
                "Gold Units": self.portfolio.gold_units,
                "Gold Price": self.portfolio.gold_price,
                "ETF EM Units": self.portfolio.etf_em_units,
                "ETF EM Price": self.portfolio.etf_em_price,
                "ETF MSCI Units": self.portfolio.etf_msci_units,
                "ETF MSCI Price": self.portfolio.etf_msci_price,
                "Crypto Units": self.portfolio.crypto_units,
                "Crypto Price": self.portfolio.crypto_price,
                "Bonds": self.portfolio.bonds,
                "Total": total_value,
                "Invested": total_invested
            })

            # Przesunięcie czasu
            current_date = (
                datetime.strptime(current_date, "%Y-%m-%d")
                + timedelta(days=recalibration_days)
            ).strftime("%Y-%m-%d")

            # Roczny wzrost strategii + zainwestowana kwota
            if current_datetime.month == 1:
                self.strategy.investment_growth()
                total_invested += yearly_investment * self.strategy.rise_investment

        return results
