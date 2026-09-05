"""
Financial Analysis Engine — provides educational stock insights, company comparisons,
and financial metric explanations using synthetic/demo market data.
Disclaimer: Educational only — NOT personalized financial advice.
"""
import re
from typing import Dict, Any, List, Optional

# Supported Indian Companies Database (Demo Market Data)
STOCKS_DB: Dict[str, Dict[str, Any]] = {
    "TCS": {
        "ticker": "TCS.NS",
        "name": "Tata Consultancy Services Ltd",
        "sector": "Information Technology",
        "price": "₹3,850.50",
        "raw_price": 3850.50,
        "market_cap": "₹13.92 Lakh Cr",
        "pe_ratio": "29.4",
        "pb_ratio": "12.8",
        "dividend_yield": "1.35%",
        "revenue_growth": "+8.2% YoY",
        "profit_growth": "+10.1% YoY",
        "operating_margin": "24.5%",
        "52_week_high": "₹4,254.75",
        "52_week_low": "₹3,313.00",
        "risk_level": "Low to Moderate",
        "strengths": [
            "Global leader in IT services with massive multi-billion dollar order pipeline",
            "Consistently industry-leading operating margins (~24-25%)",
            "Strong dividend payout ratio & cash generation capabilities",
            "Robust enterprise client retention rate (>98%)"
        ],
        "risks": [
            "Global tech spending slowdown in key Western markets (US & Europe)",
            "Disruption risks from generative AI if client pricing models shift",
            "Foreign exchange volatility against USD and EUR",
            "Attrition and wage inflation pressures in tech talent"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 3420},
            {"month": "Nov 25", "price": 3550},
            {"month": "Jan 26", "price": 3710},
            {"month": "Mar 26", "price": 3680},
            {"month": "May 26", "price": 3820},
            {"month": "Jul 26", "price": 3940},
            {"month": "Sep 26", "price": 3850},
        ],
        "summary": "TCS maintains a solid balance sheet with top-tier margins and steady client execution. It remains a bellwether for the Indian IT sector."
    },
    "INFY": {
        "ticker": "INFY.NS",
        "name": "Infosys Limited",
        "sector": "Information Technology",
        "price": "₹1,620.25",
        "raw_price": 1620.25,
        "market_cap": "₹6.72 Lakh Cr",
        "pe_ratio": "25.8",
        "pb_ratio": "8.4",
        "dividend_yield": "2.10%",
        "revenue_growth": "+6.8% YoY",
        "profit_growth": "+8.5% YoY",
        "operating_margin": "20.8%",
        "52_week_high": "₹1,780.00",
        "52_week_low": "₹1,355.50",
        "risk_level": "Low to Moderate",
        "strengths": [
            "Strong digital transformation & cloud capabilities (Cobalt platform)",
            "High dividend yield and proactive capital return strategy",
            "Large deal wins exceeding $2B+ total contract value per quarter",
            "Agile talent re-skilling initiatives in AI and cloud native"
        ],
        "risks": [
            "Slower discretionary tech spend from BFSI clients",
            "Executive leadership churn in key growth regions",
            "Sub-21% margins relative to peer benchmark (TCS)",
            "Geopolitical uncertainty impacting cross-border delivery"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 1420},
            {"month": "Nov 25", "price": 1480},
            {"month": "Jan 26", "price": 1540},
            {"month": "Mar 26", "price": 1590},
            {"month": "May 26", "price": 1650},
            {"month": "Jul 26", "price": 1710},
            {"month": "Sep 26", "price": 1620},
        ],
        "summary": "Infosys demonstrates strong digital agility and large-deal momentum, offering attractive capital return via dividends despite near-term demand headwinds."
    },
    "RELIANCE": {
        "ticker": "RELIANCE.NS",
        "name": "Reliance Industries Limited",
        "sector": "Conglomerate (Oil, Retail, Telecom)",
        "price": "₹2,980.00",
        "raw_price": 2980.00,
        "market_cap": "₹20.16 Lakh Cr",
        "pe_ratio": "27.1",
        "pb_ratio": "2.6",
        "dividend_yield": "0.35%",
        "revenue_growth": "+11.4% YoY",
        "profit_growth": "+9.2% YoY",
        "operating_margin": "16.2%",
        "52_week_high": "₹3,217.90",
        "52_week_low": "₹2,220.30",
        "risk_level": "Moderate",
        "strengths": [
            "Dominant market position in Telecom (Jio) and Retail (Reliance Retail)",
            "Integrated O2C (Oil-to-Chemicals) business providing strong cash flow anchor",
            "Massive capital investments in Green Energy (solar, hydrogen, energy storage)",
            "High entry barriers and unmatched distribution scale in India"
        ],
        "risks": [
            "High net debt load due to aggressive ongoing Capex cycles",
            "Global refining margin volatility (GRM swings)",
            "Regulatory shifts in telecom spectrum or retail FDI policies",
            "Execution risks in scaling nascent green energy gigafactories"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 2450},
            {"month": "Nov 25", "price": 2600},
            {"month": "Jan 26", "price": 2780},
            {"month": "Mar 26", "price": 2890},
            {"month": "May 26", "price": 3050},
            {"month": "Jul 26", "price": 3150},
            {"month": "Sep 26", "price": 2980},
        ],
        "summary": "Reliance Industries combines cash-generative energy businesses with hyper-growth consumer digital retail arms, positioning it as India's premier mega-cap conglomerate."
    },
    "HDFCBANK": {
        "ticker": "HDFCBANK.NS",
        "name": "HDFC Bank Limited",
        "sector": "Banking & Financial Services",
        "price": "₹1,645.80",
        "raw_price": 1645.80,
        "market_cap": "₹12.54 Lakh Cr",
        "pe_ratio": "18.5",
        "pb_ratio": "2.8",
        "dividend_yield": "1.18%",
        "revenue_growth": "+16.5% YoY",
        "profit_growth": "+18.1% YoY",
        "operating_margin": "42.0%",
        "52_week_high": "₹1,794.00",
        "52_week_low": "₹1,363.55",
        "risk_level": "Low to Moderate",
        "strengths": [
            "India's largest private sector bank with pristine asset quality (Low GNPA < 1.3%)",
            "Unrivaled branch network (>8,000 branches) driving CASA deposit gathering",
            "Post-merger scale synergy with parent HDFC Limited",
            "Strong risk management culture across retail and corporate lending"
        ],
        "risks": [
            "Short-term Net Interest Margin (NIM) compression post-merger",
            "Tightening system credit-to-deposit ratios across Indian banking",
            "Intense competition for low-cost retail CASA deposits",
            "Regulatory oversight on unsecured credit expansion"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 1490},
            {"month": "Nov 25", "price": 1530},
            {"month": "Jan 26", "price": 1580},
            {"month": "Mar 26", "price": 1610},
            {"month": "May 26", "price": 1670},
            {"month": "Jul 26", "price": 1720},
            {"month": "Sep 26", "price": 1645},
        ],
        "summary": "HDFC Bank remains the gold standard in private banking with top-tier underwriting standards, navigating deposit digestion post landmark merger."
    },
    "ICICIBANK": {
        "ticker": "ICICIBANK.NS",
        "name": "ICICI Bank Limited",
        "sector": "Banking & Financial Services",
        "price": "₹1,210.40",
        "raw_price": 1210.40,
        "market_cap": "₹8.51 Lakh Cr",
        "pe_ratio": "17.2",
        "pb_ratio": "3.1",
        "dividend_yield": "0.91%",
        "revenue_growth": "+19.2% YoY",
        "profit_growth": "+21.4% YoY",
        "operating_margin": "44.5%",
        "52_week_high": "₹1,257.80",
        "52_week_low": "₹930.00",
        "risk_level": "Low to Moderate",
        "strengths": [
            "Industry-leading Return on Equity (~18.5%) and expanding NIMs",
            "Rapid digital banking adoption via iMobile Pay ecosystem",
            "Broad-based credit growth across retail, SME, and corporate sectors",
            "Proactive provisioning and clean balance sheet (Net NPA ~0.4%)"
        ],
        "risks": [
            "Macroeconomic credit growth deceleration",
            "Unsecured retail loan portfolio stress under higher interest rates",
            "Deposit cost pressures in a tight liquidity environment"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 960},
            {"month": "Nov 25", "price": 1020},
            {"month": "Jan 26", "price": 1090},
            {"month": "Mar 26", "price": 1140},
            {"month": "May 26", "price": 1190},
            {"month": "Jul 26", "price": 1240},
            {"month": "Sep 26", "price": 1210},
        ],
        "summary": "ICICI Bank delivers exceptional risk-adjusted profitability and operating performance, outstripping sector peers in ROE expansion."
    },
    "ITC": {
        "ticker": "ITC.NS",
        "name": "ITC Limited",
        "sector": "FMCG / Diversified",
        "price": "₹495.60",
        "raw_price": 495.60,
        "market_cap": "₹6.18 Lakh Cr",
        "pe_ratio": "28.9",
        "pb_ratio": "8.1",
        "dividend_yield": "2.82%",
        "revenue_growth": "+7.5% YoY",
        "profit_growth": "+8.9% YoY",
        "operating_margin": "36.2%",
        "52_week_high": "₹528.50",
        "52_week_low": "₹399.30",
        "risk_level": "Low",
        "strengths": [
            "Unmatched cash flow generation from core cigarette business",
            "Rapidly growing non-cigarette FMCG arm (Aashirvaad, Sunfeast, Bingo)",
            "High dividend yield and shareholder return policy",
            "Demerger of Hotels business unlocking capital allocation efficiency"
        ],
        "risks": [
            "Taxation risk (GST/Excise duties) on tobacco products",
            "Input cost inflation in agricultural commodities",
            "Intense competition from regional FMCG players in packaged foods"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 415},
            {"month": "Nov 25", "price": 435},
            {"month": "Jan 26", "price": 455},
            {"month": "Mar 26", "price": 470},
            {"month": "May 26", "price": 490},
            {"month": "Jul 26", "price": 515},
            {"month": "Sep 26", "price": 495},
        ],
        "summary": "ITC provides defensive portfolio characteristics with high cash flow visibility, attractive dividend yield, and expanding FMCG distribution."
    },
    "WIPRO": {
        "ticker": "WIPRO.NS",
        "name": "Wipro Limited",
        "sector": "Information Technology",
        "price": "₹512.30",
        "raw_price": 512.30,
        "market_cap": "₹2.68 Lakh Cr",
        "pe_ratio": "22.4",
        "pb_ratio": "3.5",
        "dividend_yield": "0.20%",
        "revenue_growth": "+3.1% YoY",
        "profit_growth": "+4.5% YoY",
        "operating_margin": "16.5%",
        "52_week_high": "₹564.00",
        "52_week_low": "₹380.00",
        "risk_level": "Moderate",
        "strengths": [
            "Established footprint in consulting and cloud migration (Capco integration)",
            "Active share buyback track record returning capital to shareholders",
            "Strong presence in healthcare and utility verticals"
        ],
        "risks": [
            "Revenue growth lagging Tier-1 IT peers (TCS, Infosys)",
            "Frequent organizational restructuring and leadership changes",
            "Sub-17% operating margins creating profitability drag"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 410},
            {"month": "Nov 25", "price": 430},
            {"month": "Jan 26", "price": 460},
            {"month": "Mar 26", "price": 485},
            {"month": "May 26", "price": 520},
            {"month": "Jul 26", "price": 540},
            {"month": "Sep 26", "price": 512},
        ],
        "summary": "Wipro is undergoing strategic repositioning to reignite revenue growth, presenting turnaround optionality amidst valuation discount to top peers."
    },
    "HCLTECH": {
        "ticker": "HCLTECH.NS",
        "name": "HCL Technologies Ltd",
        "sector": "Information Technology",
        "price": "₹1,740.00",
        "raw_price": 1740.00,
        "market_cap": "₹4.72 Lakh Cr",
        "pe_ratio": "27.5",
        "pb_ratio": "7.1",
        "dividend_yield": "3.10%",
        "revenue_growth": "+9.4% YoY",
        "profit_growth": "+11.2% YoY",
        "operating_margin": "18.6%",
        "52_week_high": "₹1,868.00",
        "52_week_low": "₹1,210.00",
        "risk_level": "Low to Moderate",
        "strengths": [
            "Market leadership in Engineering R&D (ERS) services",
            "Industry-highest dividend yield (~3.1%) among Tier-1 Indian IT",
            "Solid mega-deal execution in infrastructure management services (IMS)"
        ],
        "risks": [
            "Seasonality in Software Products & Platforms segment",
            "Dependence on legacy IT infrastructure contracts subject to cloud erosion"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 1280},
            {"month": "Nov 25", "price": 1360},
            {"month": "Jan 26", "price": 1490},
            {"month": "Mar 26", "price": 1580},
            {"month": "May 26", "price": 1690},
            {"month": "Jul 26", "price": 1790},
            {"month": "Sep 26", "price": 1740},
        ],
        "summary": "HCLTech combines high dividend yield with strong ER&D market positioning, making it one of the top performers in recent IT industry cycles."
    },
    "LT": {
        "ticker": "LT.NS",
        "name": "Larsen & Toubro Ltd",
        "sector": "Engineering & Construction",
        "price": "₹3,620.00",
        "raw_price": 3620.00,
        "market_cap": "₹4.97 Lakh Cr",
        "pe_ratio": "35.2",
        "pb_ratio": "5.6",
        "dividend_yield": "0.83%",
        "revenue_growth": "+18.8% YoY",
        "profit_growth": "+20.5% YoY",
        "operating_margin": "11.4%",
        "52_week_high": "₹3,919.90",
        "52_week_low": "₹2,845.00",
        "risk_level": "Moderate",
        "strengths": [
            "Direct proxy for India's national infrastructure and Capex supercycle",
            "Record order book exceeding ₹4.7 Lakh Cr providing 3+ years revenue visibility",
            "Diversified global execution across Middle East, infrastructure, and green hydrogen"
        ],
        "risks": [
            "Working capital intensity in long-gestation EPC infrastructure projects",
            "Raw material price inflation (steel, cement, copper) squeezing contract margins"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 2920},
            {"month": "Nov 25", "price": 3100},
            {"month": "Jan 26", "price": 3320},
            {"month": "Mar 26", "price": 3480},
            {"month": "May 26", "price": 3690},
            {"month": "Jul 26", "price": 3840},
            {"month": "Sep 26", "price": 3620},
        ],
        "summary": "Larsen & Toubro stands out as India's premier engineering conglomerate, backed by record order inflows and strong government infrastructure spending."
    },
    "BHARTIARTL": {
        "ticker": "BHARTIARTL.NS",
        "name": "Bharti Airtel Limited",
        "sector": "Telecommunications",
        "price": "₹1,530.50",
        "raw_price": 1530.50,
        "market_cap": "₹8.95 Lakh Cr",
        "pe_ratio": "52.1",
        "pb_ratio": "9.2",
        "dividend_yield": "0.52%",
        "revenue_growth": "+13.2% YoY",
        "profit_growth": "+28.4% YoY",
        "operating_margin": "51.8%",
        "52_week_high": "₹1,625.00",
        "52_week_low": "₹885.00",
        "risk_level": "Moderate",
        "strengths": [
            "Consistent Average Revenue Per User (ARPU) expansion above ₹210+",
            "Industry-leading 5G subscriber migration and premiumization",
            "Strong African telecom operations providing geographical cash flow hedge"
        ],
        "risks": [
            "High ongoing 5G network rollout Capex and debt servicing obligations",
            "Regulatory spectrum auction payouts"
        ],
        "price_trend": [
            {"month": "Sep 25", "price": 930},
            {"month": "Nov 25", "price": 1050},
            {"month": "Jan 26", "price": 1210},
            {"month": "Mar 26", "price": 1340},
            {"month": "May 26", "price": 1470},
            {"month": "Jul 26", "price": 1590},
            {"month": "Sep 26", "price": 1530},
        ],
        "summary": "Bharti Airtel is capitalizing on tariff hikes and 5G upgrades to drive structural ARPU and free cash flow expansion."
    }
}

# Alias Map
ALIAS_MAP: Dict[str, str] = {
    "tcs": "TCS",
    "tata consultancy": "TCS",
    "tata consultancy services": "TCS",
    "infosys": "INFY",
    "infy": "INFY",
    "reliance": "RELIANCE",
    "ril": "RELIANCE",
    "reliance industries": "RELIANCE",
    "jio": "RELIANCE",
    "hdfc": "HDFCBANK",
    "hdfc bank": "HDFCBANK",
    "hdfcbank": "HDFCBANK",
    "icici": "ICICIBANK",
    "icici bank": "ICICIBANK",
    "icicibank": "ICICIBANK",
    "itc": "ITC",
    "wipro": "WIPRO",
    "hcl": "HCLTECH",
    "hcl tech": "HCLTECH",
    "hcltech": "HCLTECH",
    "l&t": "LT",
    "larsen": "LT",
    "larsen & toubro": "LT",
    "larsen and toubro": "LT",
    "airtel": "BHARTIARTL",
    "bharti airtel": "BHARTIARTL",
    "bhartiartl": "BHARTIARTL",
}

# Financial Knowledge Base for Metric Explanations
METRICS_DB: List[Dict[str, Any]] = [
    {
        "key": "pe",
        "title": "Price-to-Earnings (P/E) Ratio",
        "patterns": [r'\bp/?e\b', r'\bprice[\s\-]?to[\s\-]?earnings\b', r'\bpe[\s\-]?ratio\b'],
        "definition": "P/E (Price-to-Earnings) ratio compares a company's current stock price with its earnings per share (EPS). It measures how much investors are willing to pay for every ₹1 of net profit.",
        "formula": "P/E Ratio = Market Price per Share / Earnings per Share (EPS)",
        "interpretation": "A higher P/E ratio can indicate that investors expect stronger future earnings growth or that the stock is priced at a premium. A lower P/E ratio can suggest lower growth expectations or that the stock may be undervalued relative to earnings. P/E is most effective when compared against industry peers and historical averages.",
        "example": "If a company trades at ₹200 per share and earns ₹10 per share in net profit, its P/E ratio is 20x (₹200 / ₹10)."
    },
    {
        "key": "roe",
        "title": "Return on Equity (ROE)",
        "patterns": [r'\broe\b', r'\breturn[\s\-]?on[\s\-]?equity\b'],
        "definition": "Return on Equity (ROE) measures how efficiently a company's management uses shareholders' equity to generate net profit.",
        "formula": "ROE (%) = (Net Income / Shareholders' Equity) * 100",
        "interpretation": "An ROE above 15-20% is generally considered strong for non-financial companies, demonstrating capital efficiency, pricing power, and disciplined capital allocation.",
        "example": "If a company has ₹100 Crore in shareholders' equity and generates ₹20 Crore in annual net profit, its ROE is 20%."
    },
    {
        "key": "roa",
        "title": "Return on Assets (ROA)",
        "patterns": [r'\broa\b', r'\breturn[\s\-]?on[\s\-]?assets\b'],
        "definition": "Return on Assets (ROA) measures how effectively a company utilizes its total assets to generate net earnings.",
        "formula": "ROA (%) = (Net Income / Total Assets) * 100",
        "interpretation": "Higher ROA indicates greater asset productivity. It shows how much profit a company extracts from every rupee of capital asset it owns.",
        "example": "If a business owns ₹1,000 Crore in total assets and earns ₹100 Crore in net profit, its ROA is 10%."
    },
    {
        "key": "ebitda",
        "title": "EBITDA (Earnings Before Interest, Taxes, Depreciation & Amortization)",
        "patterns": [r'\bebitda\b', r'\bearnings[\s\-]?before[\s\-]?interest\b'],
        "definition": "EBITDA measures a company's core operational cash profitability before accounting decisions, tax structures, and debt financing costs.",
        "what_it_measures": "Pure operating profitability stripped of non-cash depreciation, tax regimes, and capital structure leverage.",
        "why_analysts_use_it": "It allows direct operational comparisons between companies operating in different tax jurisdictions or carrying different debt burdens.",
        "example": "If a company generates ₹500 Cr in revenue and incurs ₹350 Cr in operational expenses, its EBITDA is ₹150 Cr."
    },
    {
        "key": "eps",
        "title": "Earnings Per Share (EPS)",
        "patterns": [r'\beps\b', r'\bearnings[\s\-]?per[\s\-]?share\b'],
        "definition": "Earnings Per Share (EPS) represents the portion of a company's net profit allocated to each outstanding share of common stock.",
        "formula": "EPS = (Net Profit - Preferred Dividends) / Total Outstanding Shares",
        "interpretation": "Consistently increasing EPS indicates expanding business profitability per share and is a primary fundamental driver of long-term stock price appreciation.",
        "example": "If a company earns ₹100 Crore net profit and has 10 Crore outstanding shares, its EPS is ₹10 per share."
    },
    {
        "key": "profit_margin",
        "title": "Net Profit Margin",
        "patterns": [r'\bprofit[\s\-]?margin\b', r'\bnet[\s\-]?margin\b', r'\bnet[\s\-]?profit[\s\-]?margin\b', r'\bprofitability\b'],
        "definition": "Net Profit Margin measures the percentage of total sales revenue that converts into net profit after deducting all operational expenses, interest, and taxes.",
        "formula": "Net Profit Margin (%) = (Net Profit / Total Revenue) * 100",
        "interpretation": "Higher profit margins indicate strong pricing power, superior cost control, and resilience against raw material inflation.",
        "example": "If a company earns ₹15 Crore net profit on total sales of ₹100 Crore, its net profit margin is 15%."
    },
    {
        "key": "operating_margin",
        "title": "Operating Margin (OPM)",
        "patterns": [r'\boperating[\s\-]?margin\b', r'\boperating[\s\-]?profit[\s\-]?margin\b', r'\bopm\b'],
        "definition": "Operating Margin measures the percentage of revenue remaining after paying variable operational expenses (raw materials, employee wages) before interest and taxes.",
        "formula": "Operating Margin (%) = (Operating Profit / Total Revenue) * 100",
        "interpretation": "Strong operating margins reflect core business operational health independent of capital structure or tax strategy.",
        "example": "If total revenue is ₹100 Cr and core operating costs are ₹75 Cr, the operating margin is 25%."
    },
    {
        "key": "revenue_growth",
        "title": "Revenue Growth Rate (YoY)",
        "patterns": [r'\brevenue[\s\-]?growth\b', r'\bsales[\s\-]?growth\b', r'\btopline[\s\-]?growth\b', r'\btop[\s\-]?line[\s\-]?growth\b', r'\bprofit[\s\-]?growth\b'],
        "definition": "Revenue Growth tracks the percentage increase in total sales over a specific period (typically Year-over-Year).",
        "formula": "Revenue Growth (%) = ((Current Period Revenue - Prior Period Revenue) / Prior Period Revenue) * 100",
        "interpretation": "Sustained revenue growth demonstrates expanding customer demand, market share acquisition, and business scaling capacity.",
        "example": "Sales growing from ₹1,000 Cr last year to ₹1,150 Cr this year represents a +15% YoY revenue growth rate."
    },
    {
        "key": "market_cap",
        "title": "Market Capitalization (Market Cap)",
        "patterns": [r'\bmarket[\s\-]?cap\b', r'\bmarket[\s\-]?capitalization\b'],
        "definition": "Market Capitalization represents the total equity market value of a publicly traded company.",
        "formula": "Market Cap = Current Share Price * Total Outstanding Shares",
        "interpretation": "Classifies companies into Large-cap (>₹20,000 Cr, steady), Mid-cap (₹5,000–20,000 Cr, growing), and Small-cap (<₹5,000 Cr, high risk/reward).",
        "example": "A company with 100 Crore shares trading at ₹500 per share has a Market Cap of ₹50,000 Crore."
    },
    {
        "key": "fifty_two_week",
        "title": "52-Week High & Low Range",
        "patterns": [r'\b52[\s\-]?week\b', r'\bfifty[\s\-]?two[\s\-]?week\b'],
        "definition": "The 52-Week High and Low represent the highest and lowest trading prices of a stock over the past 52 weeks (1 year).",
        "how_investors_use_it": "Investors use this range to gauge market sentiment, price volatility, and whether a stock is trading near technical support levels or historical highs.",
        "example": "If a stock's 52-week range is ₹1,000 to ₹1,500 and it trades at ₹1,450, it is trading near its 52-week high."
    },
    {
        "key": "fcf",
        "title": "Free Cash Flow (FCF)",
        "patterns": [r'\bfcf\b', r'\bfree[\s\-]?cash[\s\-]?flow\b'],
        "definition": "Free Cash Flow represents the actual cash a company generates after accounting for operating expenses and capital expenditures (Capex).",
        "formula": "FCF = Operating Cash Flow - Capital Expenditures (Capex)",
        "interpretation": "Positive FCF allows companies to pay dividends, reduce debt, or fund organic growth without relying on external bank borrowing.",
        "example": "If operating cash flow is ₹500 Cr and Capex is ₹200 Cr, the Free Cash Flow is ₹300 Cr."
    }
]


# General Financial Knowledge Base
GENERAL_FINANCE_DB: List[Dict[str, Any]] = [
    {
        "patterns": [
            r'\bmetrics\b.*\b(look|check|analyze|evaluate)\b',
            r'\bbefore\s+analyzing\s+a\s+stock\b',
            r'\bwhat\s+financial\s+metrics\s+should\s+i\s+look\s+at\b',
            r'\bcheck\s+before\s+evaluating\s+a\s+stock\b',
            r'\bhow\s+should\s+i\s+analyze\s+a\s+company\b',
            r'\bwhat\s+makes\s+a\s+company\s+financially\s+strong\b',
            r'\bhow\s+to\s+(analyze|evaluate)\s+(a\s+stock|stocks|company)\b',
            r'\bstock\s+evaluation\s+(checklist|guide|metrics|framework)\b'
        ],
        "answer": (
            "Before analyzing a stock, look at a combination of growth, profitability, valuation, financial health, and cash flow metrics:\n\n"
            "### 1. Revenue Growth Rate\n"
            "- **What it tells you:** Measures Year-over-Year percentage increase in total sales revenue.\n"
            "- **Why it matters:** Sustained topline revenue growth signals expanding market demand and business scaling capacity.\n\n"
            "### 2. Profit Growth & Net Profit Margin\n"
            "- **What it tells you:** Net Profit Margin represents the percentage of total sales converting into net earnings after expenses.\n"
            "- **Why it matters:** Expanding profit margins reflect pricing power and cost discipline.\n\n"
            "### 3. Operating Margin (OPM)\n"
            "- **What it tells you:** Percentage of revenue remaining after paying variable operational costs before interest and taxes.\n"
            "- **Why it matters:** Evaluates core operational efficiency independent of tax regimes or debt structure.\n\n"
            "### 4. Earnings Per Share (EPS)\n"
            "- **What it tells you:** Portion of company profit allocated to each outstanding common share.\n"
            "- **Why it matters:** Consistently growing EPS is the primary fundamental driver of long-term stock price appreciation.\n\n"
            "### 5. Price-to-Earnings (P/E) Ratio\n"
            "- **What it tells you:** Compares current share price with earnings per share.\n"
            "- **Why it matters:** Helps evaluate whether a stock is valued reasonably relative to its earnings and industry peers.\n\n"
            "### 6. Return on Equity (ROE) & Return on Assets (ROA)\n"
            "- **What it tells you:** ROE measures how efficiently management generates profit from shareholders' equity (target >15-20%). ROA measures total asset productivity.\n\n"
            "### 7. Debt / Financial Health\n"
            "- **What it tells you:** Evaluates corporate debt load and financial leverage.\n"
            "- **Why it matters:** Low leverage buffers companies during economic downturns and high-interest rate environments.\n\n"
            "### 8. Market Capitalization\n"
            "- **What it tells you:** Total equity market value, categorizing companies into Large-cap (>₹20,000 Cr), Mid-cap, or Small-cap.\n\n"
            "### 9. Free Cash Flow (FCF)\n"
            "- **What it tells you:** Actual cash generated after operating costs and capital expenditure (Capex).\n"
            "- **Why it matters:** FCF funds dividends, share buybacks, and debt reduction without relying on bank borrowing.\n\n"
            "These metrics should be considered together rather than using a single metric in isolation."
        )
    },
    {
        "patterns": [
            r'\bhow\s+to\s+(evaluate|check)\s+stock\s+valuation\b',
            r'\bvaluation\s+(framework|guide|metrics)\b'
        ],
        "answer": (
            "Evaluating stock valuation requires comparing multiples against historical averages and peer competitors:\n\n"
            "- **P/E Ratio:** Compares share price to earnings per share. Lower P/E relative to peers may suggest undervaluation.\n"
            "- **Price-to-Book (P/B) Ratio:** Compares market price to net asset book value (especially useful for banks and asset-heavy sectors).\n"
            "- **EV/EBITDA:** Measures Enterprise Value relative to operating EBITDA, accounting for debt levels.\n"
            "- **Dividend Yield:** Percentage of share price returned to investors as annual cash dividends.\n\n"
            "Always evaluate valuation in context with earnings growth rates (PEG ratio)."
        )
    }
]


def detect_general_finance_answer(query: str) -> Optional[str]:
    """Match query string against general finance educational topics."""
    q = query.lower().strip()
    for item in GENERAL_FINANCE_DB:
        for pat in item["patterns"]:
            if re.search(pat, q):
                return item["answer"]
    return None


def detect_metric_explanation(query: str) -> Optional[Dict[str, Any]]:
    """Match query string against regex metric patterns."""
    q = query.lower().strip()
    for item in METRICS_DB:
        for pat in item["patterns"]:
            if re.search(pat, q):
                return item
    return None


def format_metric_answer(kb: Dict[str, Any]) -> str:
    """Format metric explanation into clean Markdown."""
    parts = [f"### {kb['title']}\n"]
    if "definition" in kb:
        parts.append(f"**What it means:** {kb['definition']}\n")
    if "formula" in kb:
        parts.append(f"**Formula:**\n`{kb['formula']}`\n")
    if "what_it_measures" in kb:
        parts.append(f"**What it measures:** {kb['what_it_measures']}\n")
    if "why_analysts_use_it" in kb:
        parts.append(f"**Why analysts use it:** {kb['why_analysts_use_it']}\n")
    if "how_investors_use_it" in kb:
        parts.append(f"**How investors use it:** {kb['how_investors_use_it']}\n")
    if "interpretation" in kb:
        parts.append(f"**How to interpret:** {kb['interpretation']}\n")
    if "example" in kb:
        parts.append(f"**Example:** {kb['example']}")
    
    return "\n".join(parts)


def normalize_company(query: str) -> Optional[str]:
    """Find matching stock key from raw string query."""
    q = query.lower().strip()
    for alias, key in ALIAS_MAP.items():
        if alias in q:
            return key
    for key in STOCKS_DB:
        if key.lower() in q:
            return key
    return None


def extract_two_companies(query: str) -> List[str]:
    """Extract up to 2 companies for comparison."""
    found = []
    words = re.split(r'\s+vs\s+|\s+and\s+|\s+compare\s+|,', query.lower())
    for chunk in words:
        key = normalize_company(chunk)
        if key and key not in found:
            found.append(key)
        if len(found) == 2:
            break
    if len(found) < 2:
        # Fallback search across full query string
        for alias, key in ALIAS_MAP.items():
            if alias in query.lower() and key not in found:
                found.append(key)
            if len(found) == 2:
                break
    return found


def analyze_financial_message(message: str) -> Dict[str, Any]:
    """
    Main Financial Intelligence router.
    Detects intent and generates structured educational analysis.
    """
    msg_lower = message.lower().strip()
    disclaimer = "Educational analysis only. This is not personalized investment advice. Demo market data shown."

    comp_key = normalize_company(msg_lower)
    extracted_companies = extract_two_companies(msg_lower)

    # 1. COMPANY COMPARISON INTENT (2 companies OR explicit comparison words)
    if any(w in msg_lower for w in ["compare", "vs", "versus", "difference"]) or len(extracted_companies) == 2:
        if len(extracted_companies) >= 2:
            c1 = STOCKS_DB[extracted_companies[0]]
            c2 = STOCKS_DB[extracted_companies[1]]
            answer = (
                f"### Company Comparison: {c1['name']} vs {c2['name']}\n\n"
                f"Here is a side-by-side financial metric breakdown for **{extracted_companies[0]}** and **{extracted_companies[1]}** based on current demo market figures.\n\n"
                f"**Key Takeaways:**\n"
                f"- **Valuation (P/E):** {extracted_companies[0]} trades at **{c1['pe_ratio']}x** P/E vs {extracted_companies[1]} at **{c2['pe_ratio']}x** P/E.\n"
                f"- **Growth Profile:** {extracted_companies[0]} recorded revenue growth of **{c1['revenue_growth']}** compared to **{c2['revenue_growth']}** for {extracted_companies[1]}.\n"
                f"- **Operating Margins:** {extracted_companies[0]} operates at **{c1['operating_margin']}** margin vs **{c2['operating_margin']}** for {extracted_companies[1]}.\n\n"
                f"*Factors to research further include capital allocation strategies, sectoral tailwinds, and earnings momentum.*"
            )
            return {
                "intent": "COMPANY_COMPARISON",
                "answer": answer,
                "comparison_table": [
                    {"metric": "Stock Ticker", "c1": c1["ticker"], "c2": c2["ticker"]},
                    {"metric": "Current Price", "c1": c1["price"], "c2": c2["price"]},
                    {"metric": "Market Cap", "c1": c1["market_cap"], "c2": c2["market_cap"]},
                    {"metric": "P/E Ratio", "c1": c1["pe_ratio"], "c2": c2["pe_ratio"]},
                    {"metric": "Revenue Growth", "c1": c1["revenue_growth"], "c2": c2["revenue_growth"]},
                    {"metric": "Profit Growth", "c1": c1["profit_growth"], "c2": c2["profit_growth"]},
                    {"metric": "Operating Margin", "c1": c1["operating_margin"], "c2": c2["operating_margin"]},
                    {"metric": "Dividend Yield", "c1": c1["dividend_yield"], "c2": c2["dividend_yield"]},
                    {"metric": "52-Week Range", "c1": f"{c1['52_week_low']} – {c1['52_week_high']}", "c2": f"{c2['52_week_low']} – {c2['52_week_high']}"},
                    {"metric": "Risk Profile", "c1": c1["risk_level"], "c2": c2["risk_level"]},
                ],
                "company_1": c1,
                "company_2": c2,
                "disclaimer": disclaimer,
            }

    # 2. STOCK TREND INTENT (Company matched + trend/chart/graph/history/movement)
    if comp_key and any(w in msg_lower for w in ["trend", "chart", "graph", "history", "movement"]):
        stock = STOCKS_DB[comp_key]
        answer = (
            f"### Price Trend Analysis: {stock['name']} ({stock['ticker']})\n\n"
            f"Here is the recent price movement and historical performance trend for **{stock['name']}** based on demo market data.\n\n"
            f"- **Current Trading Price:** {stock['price']}\n"
            f"- **52-Week Range:** {stock['52_week_low']} – {stock['52_week_high']}\n"
            f"- **Financial Momentum:** Revenue growth of **{stock['revenue_growth']}** with operating margins of **{stock['operating_margin']}**."
        )
        return {
            "intent": "STOCK_TREND",
            "answer": answer,
            "company": stock["name"],
            "ticker": stock["ticker"],
            "analysis": {
                "price": stock["price"],
                "market_cap": stock["market_cap"],
                "pe_ratio": stock["pe_ratio"],
                "revenue_growth": stock["revenue_growth"],
                "profit_growth": stock["profit_growth"],
                "operating_margin": stock["operating_margin"],
                "52_week_high": stock["52_week_high"],
                "52_week_low": stock["52_week_low"],
            },
            "price_trend": stock["price_trend"],
            "disclaimer": disclaimer,
        }

    # 3. RISK ANALYSIS INTENT (Company matched + risk/danger/downside/threat)
    if comp_key and any(w in msg_lower for w in ["risk", "danger", "threat", "downside"]):
        stock = STOCKS_DB[comp_key]
        answer = (
            f"### Risk Analysis: {stock['name']} ({stock['ticker']})\n\n"
            f"The key risk factors and vulnerabilities to monitor for **{stock['name']}** include:\n\n"
            + "\n".join([f"⚠️ **{r}**" for r in stock["risks"]]) + "\n\n"
            f"**Risk Rating:** {stock['risk_level']}"
        )
        return {
            "intent": "RISK_ANALYSIS",
            "answer": answer,
            "company": stock["name"],
            "ticker": stock["ticker"],
            "analysis": {
                "price": stock["price"],
                "market_cap": stock["market_cap"],
                "pe_ratio": stock["pe_ratio"],
                "revenue_growth": stock["revenue_growth"],
                "profit_growth": stock["profit_growth"],
                "operating_margin": stock["operating_margin"],
                "52_week_high": stock["52_week_high"],
                "52_week_low": stock["52_week_low"],
            },
            "risks": stock["risks"],
            "risk_level": stock["risk_level"],
            "price_trend": stock["price_trend"],
            "disclaimer": disclaimer,
        }

    # 4. SPECIFIC STOCK ANALYSIS INTENT
    if comp_key and comp_key in STOCKS_DB:
        stock = STOCKS_DB[comp_key]
        answer = (
            f"### {stock['name']} ({stock['ticker']}) — Financial Analysis\n\n"
            f"**Sector:** {stock['sector']} | **Risk Rating:** {stock['risk_level']}\n\n"
            f"#### 📊 Performance Overview\n"
            f"{stock['summary']}\n\n"
            f"#### 💪 Core Strengths\n"
            + "\n".join([f"- {s}" for s in stock["strengths"]]) + "\n\n"
            f"#### ⚠️ Key Risks to Monitor\n"
            + "\n".join([f"- {r}" for r in stock["risks"]]) + "\n\n"
            f"#### 📌 Neutral Assessment\n"
            f"Based on available metrics, **{comp_key}** shows revenue growth of **{stock['revenue_growth']}** with operating margins of **{stock['operating_margin']}**. "
            f"Investors should evaluate these figures alongside broader sector trends."
        )
        return {
            "intent": "STOCK_ANALYSIS",
            "answer": answer,
            "company": stock["name"],
            "ticker": stock["ticker"],
            "analysis": {
                "price": stock["price"],
                "market_cap": stock["market_cap"],
                "pe_ratio": stock["pe_ratio"],
                "revenue_growth": stock["revenue_growth"],
                "profit_growth": stock["profit_growth"],
                "operating_margin": stock["operating_margin"],
                "52_week_high": stock["52_week_high"],
                "52_week_low": stock["52_week_low"],
            },
            "strengths": stock["strengths"],
            "risks": stock["risks"],
            "risk_level": stock["risk_level"],
            "price_trend": stock["price_trend"],
            "disclaimer": disclaimer,
        }

    # 5. FINANCIAL METRIC INTENT
    metric_kb = detect_metric_explanation(msg_lower)
    if metric_kb:
        answer = format_metric_answer(metric_kb)
        return {
            "intent": "FINANCIAL_METRIC",
            "answer": answer,
            "metric_title": metric_kb["title"],
            "disclaimer": disclaimer,
        }

    # 6. GENERAL FINANCE EDUCATIONAL INTENT
    gen_answer = detect_general_finance_answer(msg_lower)
    if gen_answer:
        return {
            "intent": "GENERAL_FINANCE",
            "answer": gen_answer,
            "disclaimer": disclaimer,
        }

    # 7. UNSUPPORTED / UNRELATED QUERY FALLBACK
    supported_list = ", ".join(STOCKS_DB.keys())
    return {
        "intent": "UNSUPPORTED",
        "answer": (
            f"I am your AI Financial Analyst. I can analyze supported Indian stocks, compare companies, explain financial metrics, or provide stock evaluation frameworks.\n\n"
            f"**Try asking:**\n"
            f"- *'What financial metrics should I look at before analyzing a stock?'*\n"
            f"- *'Analyze TCS'* or *'Analyze Infosys stock'*\n"
            f"- *'Compare TCS and Infosys'*\n"
            f"- *'What are the key risks for Reliance?'*\n"
            f"- *'Show me the recent trend of TCS'*\n"
            f"- *'Explain P/E ratio'* or *'What is ROE?'*\n\n"
            f"**Supported Companies:** {supported_list}"
        ),
        "disclaimer": disclaimer,
    }


