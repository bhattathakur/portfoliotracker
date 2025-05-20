# Portfolio Tracker - Introduction

---

**i)** This program allows you to track changes in your Portfolio **minute by minute** over the **last five business days**, or **day by day** across a selected date range.

**ii)** You can input your Portfolio manually in the text box or, preferably, **upload a CSV file** containing your Portfolio information. **Uploading a CSV is the recommended method**, as it allows the session to retain and manage your data more effectively. When entering data, you can simply list the raw information — including instances where the **same Ticker** is purchased at **different prices and quantities**. The program will automatically generate an aggregated table that computes the **average price** for each Ticker.

**iii)** In the **'Portfolio Overview'** tab, you will find a comprehensive summary of your Portfolio, including both your **Portfolio Allocation (in monetary terms)** and the **number of shares** held for each Ticker.

**iv)** The **'Per Minute Portfolio Change'** tab displays the **minute-by-minute fluctuation** in your total Portfolio Market Value, along with the individual Market Values of the relevant Tickers.

**v)** In the **'Daily Portfolio Change'** tab, you can view the **day-by-day variation** in your overall Portfolio Market Value, as well as the Market Values of the associated Tickers.

---

> **Disclaimer:**  
> This tool is intended solely for informational and analytical purposes. It does **not** constitute investment advice or a recommendation to buy, sell, or hold any financial instruments. Always consult a qualified financial advisor before making any investment decisions.

---


**Data Source:**  
Market data is extracted using the **'yfinance'** library and is derived from **[Yahoo Finance](https://finance.yahoo.com)** ©. Accuracy and availability of data depend on Yahoo Finance services.