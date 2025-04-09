# 💹 Capitalized: Integrated Financial Intelligence Platform

**Capitalized** is a powerful web-based platform built with **Streamlit** for advanced financial analysis — from **equity and debt valuation** to **option pricing**, **project financing**, and **scenario analysis** — all in one seamless interface.

---

## 🚀 Key Features

### 📊 1. Equity Valuation
- Automatically fetches financial data via **Yahoo Finance**.
- Calculates key **valuation multiples**:
  - Price to Book Value
  - Price to Earnings Ratio
  - EV/EBITDA
  - EV/Revenue
- Interactive and editable data tables with auto-filling of missing values using averages.

### 💸 2. Debt Valuation (Bond)
- Performs fixed income valuation using:
  - Par value
  - Coupon rate & frequency
  - Market yield
  - Time to maturity
- Calculates:
  - Present Value of Cash Flows
  - Bond Pricing
  - Visualized cash flow breakdown with Plotly charts.

### 🧾 3. Option Pricing
- **European Options**: Black-Scholes model with batch table input.
- **American Options**: Binomial tree simulation with visual trees.
- **Monte Carlo Simulation**:
  - Option price estimation
  - Portfolio risk with VaR & CVaR metrics

### 🏗️ 4. Project Financing Model
A full-stack simulation engine with:
- **CAPEX Planning**: Equity/Loan split, provision fees, IDC calculation
- **Loan Amortization Schedule**: Equal Installments or Equal Principal
- **Cash Flow Tables**:
  - Operational, Investment, and Financing
- **Full Financial Statements**:
  - Profit & Loss (P&L)
  - Balance Sheet
  - Tax Calculation with carry-forward loss logic
- **Project KPIs**:
  - Net Present Value (NPV)
  - Internal Rate of Return (IRR)
  - Payback Period

### 📐 5. Scenario Analysis & Optimization
- Sensitivity and constraint-based optimization using:
  - `scipy.optimize.differential_evolution`
- Visual distribution of valid parameter combinations (Boxplots)
- Targets include:
  - Project IRR / NPV / Payback Period
  - Equity IRR / NPV
- Use **fixed values** or **range sliders** for input flexibility.

---

## 🧰 Tech Stack

| Layer      | Tech Used                                      |
|------------|------------------------------------------------|
| Frontend   | [Streamlit](https://streamlit.io)              |
| Backend    | Python (Pandas, NumPy, SciPy, yFinance, Plotly)|
| Data Fetch | `yfinance`, `selenium` (for bond data)         |
| Simulation | Monte Carlo, Binomial Trees, Black-Scholes     |

---

## 🗂️ Project Structure

```
.
├── main.py                                # Entry point for Streamlit app
├── sidebar.py                             # Sidebar navigation controller
├── equities.py                            # Equity valuation page
├── debt.py                                # Bond valuation page
├── option.py                              # Option pricing dashboard
├── monte_carlo.py                         # Monte Carlo simulation engine
├── american_option.py                     # American option valuation using binomial tree
├── european_option.py                     # European option pricing using Black-Scholes
├── financial_data_fetcher.py              # Real-time financial data fetcher (yFinance)
├── multiples_calculator.py                # Equity/Enterprise valuation multiples calculator
├── volatility_calculator.py               # Historical volatility computation
├── bond_data_fetcher.py                   # Web scraper for 10Y government bond yield
├── ticker_data_processor.py               # Wrapper for combining financials and multiples
├── project_financing.py                   # Core project financing module
├── project_financing_scenario.py          # Streamlit UI for scenario analysis
├── project_financing_scenario_function.py # All financial modelling functions (NPV, IRR, PBP)
└── README.md                              # You're reading this!
```

---

## 🛠️ How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/your-username/capitalized.git
cd capitalized

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
streamlit run main.py
```

> ⚠️ Make sure you have ChromeDriver installed if you want to use the bond yield scraper (used in `bond_data_fetcher.py`).

---

## 📸 Sample Screenshots

![ss1](https://github.com/user-attachments/assets/7e7e2fd5-9887-4948-a575-c2fdd0f9b5b8)
![ss2](https://github.com/user-attachments/assets/94ba39b4-2b3b-45a8-a0d5-ad63a4100d70)
![ss3](https://github.com/user-attachments/assets/9fecdcbf-5c4a-46e7-a1b2-38d232d30e0d)
![ss4](https://github.com/user-attachments/assets/206295da-4524-457f-9cd2-f82716aeef02)

---

## 🤝 Contributing

We welcome contributors! Open issues, suggest features, or submit a pull request.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](./LICENSE) file for details.
