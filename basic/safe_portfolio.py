from .imports import *
from .assets import *


class SafePortfolio:
    """
    Portfel nastawiony na bezpieczeństwo (obligacje + złoto).
    Możesz dodać np. stablecoiny, gotówkę, itp. zależnie od potrzeb.
    """
    def __init__(self, bonds_pro=0.7, gold_pro=0.3):
        self.bonds_pro = bonds_pro
        self.gold_pro = gold_pro
        self.bonds = 0
        self.gold_units = 0
        self.gold_price = 0

    def allocate_investment(self, total_investment):
        """
        Dokładamy do portfela odpowiednie kwoty w złocie i obligacjach
        zgodnie z zadanymi proporcjami.
        """
        gold_investment = total_investment * self.gold_pro
        bonds_investment = total_investment * self.bonds_pro

        # Przeliczamy, ile jednostek złota można kupić, jeśli jest cena > 0
        if self.gold_price > 0:
            self.gold_units += gold_investment / self.gold_price

        self.bonds += bonds_investment

    def calculate_total_value(self):
        """
        Suma wartości wszystkich aktywów w portfelu.
        """
        return (self.gold_units * self.gold_price) + self.bonds


class SafeSimulation:
    """
    Klasa do uruchamiania symulacji dla portfela 'SafePortfolio'.
    """
    def __init__(self, portfolio, bond_asset, strategy, start_year=2015, years=10):
        self.portfolio = portfolio
        self.bond_asset = bond_asset
        self.strategy = strategy
        self.start_year = start_year
        self.years = years

        # np. co 0.085 roku (ok. 31 dni) robimy update cen i inwestycje
        self.recalibration_period = 0.085
        self.recalibration_bool = True

        # zapamiętujemy datę startową
        self.previous_check = f"{self.start_year}-01-01"

    def update_prices(self, current_date):
        """
        Pobiera cenę złota + aktualizuje wartości obligacji.
        """
        try:
            # Dla złota np. "GC=F" (Gold Futures)
            asset = Asset("GC=F")
            self.portfolio.gold_price = asset.fetch_price(current_date)
        except ValueError as e:
            print(e)
            self.portfolio.gold_price = 0

        # Obligacje rosną zgodnie z inflacją i yieldem
        growth_factor = self.bond_asset.calculate_growth_factor(self.recalibration_period)
        self.portfolio.bonds *= growth_factor

    def run(self, yearly_investment):
        """
        Główna pętla symulacji.
        Zwraca listę słowników z przebiegiem (do łatwego zrzucenia w DataFrame).
        """
        results = []
        start_date = self.previous_check
        current_date = self.previous_check
        end_date = (datetime.strptime(current_date, "%Y-%m-%d")
                    + timedelta(days=int(self.years * 365))).strftime("%Y-%m-%d")

        recalibration_days = int(self.recalibration_period * 365)
        total_invested = yearly_investment

        while current_date < end_date:
            current_datetime = datetime.strptime(current_date, "%Y-%m-%d")

            # 1) Pierwsza iteracja: "skip" aktualizacji, bo dopiero zaczynamy
            if current_date == start_date:
                # Nie wprowadzamy jeszcze inwestycji w "zerowym" dniu
                print(f"Data startowa {start_date} - pomijam aktualizację i inwestycję.")
                current_date = (
                    datetime.strptime(current_date, "%Y-%m-%d")
                    + timedelta(days=recalibration_days)
                ).strftime("%Y-%m-%d")
                # Ale zaktualizujemy ceny i kupimy pierwsze aktywa
                self.update_prices(current_date)
                self.portfolio.allocate_investment(yearly_investment * self.strategy.rise_investment)
                continue

            # 2) Aktualizacja cen aktywów
            self.update_prices(current_date)

            # 3) Jeżeli to styczeń, dokładamy roczną inwestycję
            if current_datetime.month == 1:
                self.portfolio.allocate_investment(yearly_investment * self.strategy.rise_investment)

            # 4) Rebalancing proporcji w styczniu (jeśli włączony)
            if current_datetime.month == 1 and self.recalibration_bool:
                total_value = self.portfolio.calculate_total_value()
                if self.portfolio.gold_price > 0:
                    self.portfolio.gold_units = (total_value * self.portfolio.gold_pro) / self.portfolio.gold_price
                self.portfolio.bonds = total_value * self.portfolio.bonds_pro

            # Zapis do listy wyników
            total_value = self.portfolio.calculate_total_value()
            results.append({
                "Date": current_date,
                "Gold Price": self.portfolio.gold_price,
                "Gold Units": self.portfolio.gold_units,
                "Bonds": self.portfolio.bonds,
                "Total": total_value,
                "Invested": total_invested
            })

            # Przesuwamy się o recalibration_days dni
            current_date = (
                datetime.strptime(current_date, "%Y-%m-%d")
                + timedelta(days=recalibration_days)
            ).strftime("%Y-%m-%d")

            # 5) Rozwój strategii (np. roczny wzrost inwestycji)
            self.strategy.investment_growth()

            # Dodajemy do total_invested (opcjonalnie tylko w styczniu)
            if current_datetime.month == 1:
                total_invested += yearly_investment * self.strategy.rise_investment

        return results
