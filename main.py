# main.py
import streamlit as st
from analysis.analyze_company import analyze_company
from basic.run_safe_portfolio import run_defensive_portfolio
from basic.run_growth import run_growth_portfolio
from predictions.run_risky import run_risky
from predictions.run_roulette import run_roulette


def main():
    st.set_page_config(page_title="Dynamic Windows", layout="wide")

    # Menu options
    options = ["Welcome Menu", "Defensive", "Optimal", "Risky", "Roulette", "Custom Analysis"]
    choice = st.selectbox("Choose an option", options)

    # Default welcome menu
    if choice == "Welcome Menu":
        st.title("Welcome to the Investment Panel!")
        st.write("Explore the available options:")

        st.markdown("<h2><b>Defensive:</b> The safest investment option. Focused on government bonds and gold.</h2>", unsafe_allow_html=True)
        st.markdown("<h2><b>Optimal:</b> A diversified portfolio including cryptocurrencies, bonds, gold, ETFs of developed and emerging markets.</h2>", unsafe_allow_html=True)
        st.markdown("<h2><b>Risky:</b> A 20-day prediction to determine whether a company will experience an increase or decrease in stock value.</h2>", unsafe_allow_html=True)
        st.markdown("<h2><b>Roulette:</b> Day-to-day trading with suggestions on whether a company's stock will rise or fall the next day.</h2>", unsafe_allow_html=True)
        st.markdown("<h2><b>Custom Analysis:</b> The ability to independently analyze selected stocks.</h2>", unsafe_allow_html=True)

    # Handle individual options
    elif choice == "Defensive":
        st.title("Defensive")
        st.write("The safest investment option. Focused on government bonds and gold.")
        run_defensive_portfolio()

    elif choice == "Optimal":
        st.title("Optimal")
        st.write("A diversified portfolio including cryptocurrencies, bonds, gold, ETFs of developed and emerging markets.")
        run_growth_portfolio()

    elif choice == "Risky":
        st.title("Risky")
        st.write("A 20-day prediction to determine whether a company will experience an increase or decrease in stock value.")
        run_risky()

    elif choice == "Roulette":
        st.title("Roulette")
        st.write("Day-to-day trading with suggestions on whether a company's stock will rise or fall the next day.")
        run_roulette()

    elif choice == "Custom Analysis":
        st.title("Custom Analysis")
        st.write("The ability to independently analyze selected stocks.")
        analyze_company()


if __name__ == "__main__":
    main()