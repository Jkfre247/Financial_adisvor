# Financial Advisor App

This repository contains a **Streamlit-based application** designed to support financial decision-making.  

🎥 **Watch the app in action:** [YouTube Demo](https://youtu.be/iz4tmILiGx4)

The app offers **five investment strategies**, each presented in a dedicated interface. It is intuitive and user-friendly, catering to both beginner and advanced users.

## Key Features

### 1. Defensive Portfolio
Focused on **risk minimization** and protecting capital against inflation, this portfolio includes assets like gold and bonds.  
- Ideal for users prioritizing **stability** and **low volatility**.
- Aims to safeguard investments from significant market fluctuations.  
- **Simulation:** This feature shows how the portfolio would have performed if investments had started in a selected year with regular contributions over time.

### 2. Optimal Portfolio
Designed for **balanced growth** through diversification. This portfolio combines ETFs, bonds, gold, and cryptocurrency for optimal results.  
- Targets annual returns of **5-10%**.  
- Suitable for users seeking steady gains with **moderate risk**.  
- **Simulation:** This feature shows how the portfolio would have performed if investments had started in a selected year with regular contributions over time.

### 3. Investment Recommendations
Uses a **deep LSTM model (64-64-32)** to predict stock performance over the next 20 days.  
- Provides recommendations on whether stocks are likely to **rise** or **fall**.  
- Aimed at users making **medium-term** investment decisions.

### 4. Day Trading ("Roulette")
A high-risk, high-reward strategy for **short-term traders**, powered by the **same LSTM model (64-64-32)** used in the 20-day prediction.  
- Predicts whether a stock's price will **rise** or **fall** on a given day.  
- Visualizes how the portfolio performs when investing in daily **price increases** or **decreases**.  
- Enables users to test **day trading strategies**, showing the portfolio's behavior over time based on their daily decisions.

### 5. Manual Analysis Tools
Provides advanced users with tools for conducting a detailed analysis of selected companies.  
- **Key Financial Metrics Analyzed:**  
  - **Annual Profits:** Evaluate the company's profitability over the past year.  
  - **Annual Losses:** Identify periods of financial underperformance.  
  - **Available Investment Capital:** Understand how much capital the company has for reinvestment or expansion.  
  - **Revenue Trends:** Analyze growth or decline in company revenues over time.  
- **Functionality:**  
  - Access these metrics to better understand a company's financial health.  
  - Use the data to make well-informed investment decisions based on performance trends and capital allocation.

## How It Works
- The app uses **historical data** to simulate potential returns, helping users understand the principles of investing and managing risk.  
- Predictive models allow users to experiment with **riskier strategies** in a safe, simulated environment.

