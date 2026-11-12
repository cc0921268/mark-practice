# 🎧 eBay Headphones Market Intelligence Dataset

<p align="center">
  <strong>A comprehensive dataset of 13,000+ eBay headphone listings for market analysis and data science projects</strong>
</p>

<p align="center">
  <img src="pic.jpg" alt="eBay - Data Source" width="80%" />
</p>

<p align="center">
  <em>Data sourced from publicly available eBay listings</em>
</p>

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement](#-problem-statement)
3. [Solution Approach](#-solution-approach)
4. [Dataset Overview](#-dataset-overview)
5. [Data Fields](#-data-fields)
6. [Data Source](#-data-source)
7. [Web Scraping Methodology](#%EF%B8%8F-web-scraping-methodology)
8. [Exploratory Data Analysis](#-exploratory-data-analysis)
9. [Repository Structure](#-repository-structure)
10. [Tools & Technologies](#%EF%B8%8F-tools--technologies)
11. [How to Use](#-how-to-use)
12. [Analysis Use Cases](#-analysis-use-cases)
13. [Challenges Faced](#-challenges-faced)
14. [Limitations](#%EF%B8%8F-limitations)
15. [Portfolio Value](#-portfolio-value)
16. [Data Source Disclaimer](#%EF%B8%8F-data-source-disclaimer)
17. [Author](#-author)

---

## 📌 Project Overview

This project presents a **real-world market intelligence dataset** collected from **publicly available eBay headphone listings** using ethical web scraping techniques. The goal is to demonstrate an **end-to-end data analytics workflow** — from data collection to cleaning, exploration, and insight generation — suitable for **portfolio, research, and educational purposes**.

The dataset captures detailed information about headphone products, pricing strategies, seller reputation, and customer engagement, enabling meaningful analysis of trends in the online electronics resale market.

---

## 🎯 Problem Statement

Online marketplaces like eBay contain valuable market intelligence data, but accessing this information at scale presents several challenges:

**Key Issues Identified:**
- Publicly available listing data is scattered across thousands of pages
- No structured dataset exists for headphone market analysis
- Manual data collection is time-consuming and error-prone
- Need for ethical data collection practices that respect platform policies

**Objective:** Build an ethical web scraping pipeline to collect, structure, and prepare eBay headphone listing data for market analysis and data science applications.

---

## 💡 Solution Approach

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  eBay Public    │────▶│  Ethical Web    │────▶│  Structured     │
│  Listings       │     │  Scraping       │     │  CSV Dataset    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Data Cleaning  │
                        │  & Validation   │
                        └─────────────────┘
```

**Workflow:**
1. **URL Collection** — Gather product URLs from 20+ eBay category/brand pages
2. **Data Extraction** — Scrape detailed product information from each listing
3. **Rate Limiting** — Implement ethical delays between requests
4. **Duplicate Handling** — Update incomplete records, avoid duplicates
5. **Data Storage** — Export clean, structured CSV dataset
6. **Validation** — Verify data quality and completeness

---

## 📦 Dataset Overview

| Metric | Value |
|--------|-------|
| **Dataset Name** | `ebay_headphones_listings.csv` |
| **Total Listings** | 13,142 |
| **Total Columns** | 28 structured fields |
| **Data Source** | eBay (public listings) |
| **Format** | CSV |
| **Update Type** | Snapshot (single scrape) |
| **Scrape Date** | January 2026 |

Each row represents a **single public eBay headphone listing**, enriched with product, pricing, seller, and engagement attributes.

---

## 🧾 Data Fields

### 🔑 Identification (3 fields)

| Field | Description |
|-------|-------------|
| `listing_id` | Unique eBay listing identifier |
| `listing_url` | Direct URL to the listing page |
| `scrape_timestamp` | Date and time of data collection |

### 🎧 Product Information (8 fields)

| Field | Description |
|-------|-------------|
| `title` | Product listing title |
| `brand` | Manufacturer brand name |
| `model` | Product model name/number |
| `category` | Product category |
| `headphone_type` | Form factor (Over-Ear / On-Ear / In-Ear) |
| `wireless` | Wireless connectivity (True/False) |
| `noise_cancelling` | Active noise cancellation feature |
| `color` | Product color |

### 💰 Pricing & Sales (5 fields)

| Field | Description |
|-------|-------------|
| `price` | Listed price value |
| `currency` | Price currency (USD, EUR, etc.) |
| `shipping_price` | Shipping cost |
| `listing_type` | Sale format (Auction / Buy It Now / Best Offer) |
| `bids_count` | Number of bids (for auctions) |

### 📦 Condition & Inventory (3 fields)

| Field | Description |
|-------|-------------|
| `condition` | Item condition (New, Used, Refurbished, etc.) |
| `quantity_available` | Available stock quantity |
| `sold_count` | Number of units sold |

### 🧑 Seller Information (4 fields)

| Field | Description |
|-------|-------------|
| `seller_username` | Seller's eBay username |
| `seller_feedback_score` | Seller's feedback rating score |
| `seller_positive_percent` | Percentage of positive feedback |
| `seller_location` | Seller's geographic location |

### ⭐ Engagement & Shipping (5 fields)

| Field | Description |
|-------|-------------|
| `rating` | Product rating (if available) |
| `reviews_count` | Number of product reviews |
| `watchers_count` | Number of users watching the listing |
| `shipping_type` | Shipping method (Free, Paid, etc.) |
| `returns_accepted` | Whether returns are accepted |

---

## 📊 Data Source

| Attribute | Details |
|-----------|---------|
| **Source** | eBay Public Listings |
| **Categories Scraped** | 20+ headphone categories and brands |
| **Brands Covered** | Sony, Bose, Beats, Apple, JBL, Sennheiser, Skullcandy, and more |
| **Data Access** | Public listings only (no login required) |
| **Collection Method** | Ethical web scraping with rate limiting |

### Categories Included
- All Headphones
- Brand-specific: Bose, Beats, Sony, JBL, Apple, Sennheiser, Skullcandy, Audio-Technica, Jabra, and more
- Type-specific: In-Ear, Over-Ear, Wireless
- Listing types: Auction, Buy It Now, Best Offer

---

## ⚙️ Web Scraping Methodology

### Ethical Scraping Practices

| Practice | Implementation |
|----------|----------------|
| **Rate Limiting** | Random delays (0.5-1.5 seconds) between requests |
| **Public Data Only** | No login, cookies, or private data accessed |
| **Robots.txt Respect** | Only publicly accessible pages scraped |
| **Error Handling** | Graceful handling of timeouts and failures |
| **Duplicate Prevention** | Intelligent deduplication with updates |

### Technical Implementation

- **URL Extraction:** Automated pagination through category pages
- **Data Parsing:** BeautifulSoup for HTML parsing with multiple fallback selectors
- **Browser Automation:** Selenium WebDriver for dynamic content loading
- **Stealth Mode:** Realistic browser headers and user agent rotation
- **Test Mode:** Quick validation with limited scraping for development

> ⚠️ **Note:** Parallel execution capabilities exist in the code but were **disabled during data collection** to respect ethical scraping practices.

---

## 📁 Repository Structure

```
ebay-headphones-market-dataset/
│
├── 📄 README.md                        # Project documentation
├── 📄 LICENSE                          # License information
├── 📄 requirements.txt                 # Python dependencies
├── 📄 pic.jpg                          # Project header image
│
├── 📁 dataset/
│   └── 📄 ebay_headphones_listings.csv # Main dataset (13,142 listings)
│
├── 📁 notebooks/
│   ├── 📓 01_data_inspection_local.ipynb  # Data exploration notebook (local)
│
├── 📁 outputs/
│   ├── 📄 dataset_summary.json         # Summary statistics
│   ├── 📊 brand_analysis.png           # Brand distribution visualization
│   ├── 📊 condition_analysis.png       # Condition analysis visualization
│   ├── 📊 data_quality_summary.png     # Data quality overview
│   ├── 📊 feature_analysis.png         # Wireless & ANC features
│   ├── 📊 headphone_type_analysis.png  # Headphone type distribution
│   ├── 📊 missing_values_analysis.png  # Missing data patterns
│   ├── 📊 price_analysis.png           # Price distribution charts
│   └── 📊 seller_analysis.png          # Seller metrics visualization
│
└── 📁 scripts/
    └── 📄 01_web_scraping.py           # Web scraping script
```

---

## 📊 Exploratory Data Analysis

The dataset has been thoroughly analyzed with comprehensive visualizations. Below are key insights from the exploratory data analysis:

### 📈 Data Quality Overview

<p align="center">
  <img src="outputs/data_quality_summary.png" alt="Data Quality Summary" width="90%" />
</p>

The dataset shows **74.52% overall completeness** with most critical fields having high fill rates. The visualization above shows completeness by column and overall data health.

---

### 🔍 Missing Values Analysis

<p align="center">
  <img src="outputs/missing_values_analysis.png" alt="Missing Values Analysis" width="90%" />
</p>

Missing value patterns reveal which fields are consistently available across listings and which require handling during analysis.

---

### 💰 Price Analysis

<p align="center">
  <img src="outputs/price_analysis.png" alt="Price Analysis" width="90%" />
</p>

**Key Price Insights:**
| Metric | Value |
|--------|-------|
| **Minimum Price** | $0.99 |
| **Maximum Price** | $9,999.00 |
| **Mean Price** | $70.76 |
| **Median Price** | $34.99 |

The price distribution shows a right-skewed pattern typical of e-commerce marketplaces, with most listings in the $25-100 range.

---

### 🎧 Brand Analysis

<p align="center">
  <img src="outputs/brand_analysis.png" alt="Brand Analysis" width="90%" />
</p>

**Dataset includes 1,179 unique brands** with major players like Sony, Bose, Beats, Apple, JBL, and Sennheiser dominating the market share.

---

### 📦 Condition Analysis

<p align="center">
  <img src="outputs/condition_analysis.png" alt="Condition Analysis" width="90%" />
</p>

Analysis of item conditions (New, Used, Refurbished, etc.) and their impact on pricing strategies.

---

### 🎯 Headphone Type Distribution

<p align="center">
  <img src="outputs/headphone_type_analysis.png" alt="Headphone Type Analysis" width="90%" />
</p>

Distribution across In-Ear, Over-Ear, and On-Ear form factors with corresponding price ranges.

---

### ⭐ Seller Analysis

<p align="center">
  <img src="outputs/seller_analysis.png" alt="Seller Analysis" width="90%" />
</p>

**3,690 unique sellers** in the dataset with feedback scores and positive rating percentages analyzed.

---

### 📡 Feature Analysis (Wireless & ANC)

<p align="center">
  <img src="outputs/feature_analysis.png" alt="Feature Analysis" width="90%" />
</p>

Distribution of wireless connectivity and Active Noise Cancellation (ANC) features across listings.

---

## 🛠️ Tools & Technologies

| Tool | Purpose | Version |
|------|---------|---------|
| **Python** | Primary programming language | 3.10+ |
| **Selenium** | Browser automation for dynamic content | 4.x |
| **BeautifulSoup** | HTML parsing and data extraction | 4.x |
| **Pandas** | Data manipulation and analysis | 2.x |
| **NumPy** | Numerical operations | 1.x |
| **Matplotlib** | Static visualizations | 3.x |
| **Seaborn** | Statistical data visualization | 0.13+ |
| **lxml** | Fast XML/HTML parsing | 4.x |
| **Jupyter Notebook** | Interactive data analysis | 7.x |

---

## 🚀 How to Use

### 1. Clone the Repository
```bash
git clone https://github.com/Haseeb-U/ebay-headphones-market-dataset.git
cd ebay-headphones-market-dataset
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Load the Dataset
```python
import pandas as pd

# Load the dataset
df = pd.read_csv('dataset/ebay_headphones_listings.csv')

# Quick overview
print(f"Total listings: {len(df):,}")
print(f"Columns: {df.shape[1]}")
df.head()
```

### 4. Explore the Data
```python
# Price statistics by brand
df.groupby('brand')['price'].describe()

# Listing type distribution
df['listing_type'].value_counts()

# Top sellers by feedback score
df.nlargest(10, 'seller_feedback_score')[['seller_username', 'seller_feedback_score']]
```

### 5. View Analysis Outputs
All visualizations from the data inspection notebook are saved in the `outputs/` folder:
- `brand_analysis.png` - Brand distribution charts
- `price_analysis.png` - Price distribution and statistics
- `condition_analysis.png` - Condition vs price analysis
- `seller_analysis.png` - Seller metrics visualization
- `feature_analysis.png` - Wireless & ANC features
- `data_quality_summary.png` - Overall data quality
- `dataset_summary.json` - Summary statistics in JSON format

---

## 📈 Analysis Use Cases

This dataset enables various market intelligence analyses:

| Use Case | Description |
|----------|-------------|
| 📊 **Price Analysis** | Price distribution across brands and conditions |
| 🎯 **Listing Comparison** | Auction vs Buy It Now performance analysis |
| ⭐ **Seller Analysis** | Reputation vs pricing power correlation |
| 🔥 **Demand Estimation** | Using watchers and bids as demand proxies |
| 🎧 **Feature Pricing** | Premium analysis for wireless, ANC features |
| 🌍 **Geographic Insights** | Seller location distribution and pricing |
| 📦 **Condition Impact** | Price differences by item condition |
| 📈 **Market Trends** | Brand popularity and market share analysis |

---

## 🚧 Challenges Faced

| Challenge | Description | Solution |
|-----------|-------------|----------|
| **Dynamic Content** | eBay pages load content via JavaScript | Selenium WebDriver for browser automation |
| **Rate Limiting** | Risk of being blocked for excessive requests | Random delays and respectful scraping pace |
| **Data Inconsistency** | Varying page structures across listings | Multiple fallback CSS selectors |
| **Missing Data** | Some fields not available on all listings | Graceful handling with null values |
| **Duplicate Listings** | Same products appearing in multiple categories | Deduplication by listing ID |
| **Pagination** | Navigating through thousands of pages | Automated pagination with page tracking |

---

## ⚠️ Limitations

| Limitation | Description |
|------------|-------------|
| **Snapshot Data** | Single point-in-time capture; prices and availability change |
| **Geographic Bias** | Primarily US-based listings due to eBay's default location |
| **Missing Fields** | Some listings lack complete information |
| **Category Coverage** | Focused on headphones; not representative of all eBay electronics |
| **Temporal Scope** | Data reflects market conditions at scrape time only |

### Recommendations for Improvement
- Implement periodic scraping for time-series analysis
- Expand to international eBay domains
- Add image URLs and product specifications
- Include historical price tracking

---

## 💼 Portfolio Value

This project demonstrates key data analytics competencies:

| Skill | Demonstration |
|-------|---------------|
| **Web Scraping** | Ethical data collection from dynamic websites |
| **Data Engineering** | Pipeline design for large-scale data extraction |
| **Data Cleaning** | Handling messy, real-world data |
| **Exploratory Data Analysis** | Comprehensive EDA with visualizations |
| **Data Visualization** | Professional charts using Matplotlib & Seaborn |
| **Python Programming** | Advanced use of Selenium, BeautifulSoup, Pandas |
| **Market Intelligence** | Understanding e-commerce data structures |
| **Documentation** | Clear, professional project documentation |

**Suitable For:**
- 💼 Data Analyst portfolios
- 📊 Kaggle datasets and competitions
- 🎓 Educational and research projects
- 🔬 Market research demonstrations
- 💻 Technical interview showcases

---

## ⚖️ Data Source Disclaimer

> **Disclaimer:**
>
> This dataset was collected from **publicly available eBay listings** for **educational and research purposes only**.
>
> No personal or private user data was collected.
>
> The dataset is **not intended for commercial use** and respects eBay's public data access policies.
>
> This project is **not affiliated with, endorsed by, or connected to eBay Inc.**

**Usage Terms:**
- ✅ Educational use
- ✅ Research purposes
- ✅ Portfolio demonstrations
- ✅ Non-commercial analysis
- ⚠️ Commercial use — Not recommended; verify platform terms

---

## 👤 Author

**Haseeb Uddin**  
*Data Analyst*

| Platform | Link |
|----------|------|
| 🐙 GitHub | [github.com/Haseeb-U](https://github.com/Haseeb-U) |
| 💼 LinkedIn | [linkedin.com/in/haseeb-uddin-q](https://www.linkedin.com/in/haseeb-uddin-q/) |
| 📊 Kaggle | [kaggle.com/haseebhsb](https://www.kaggle.com/haseebhsb) |

---

## 🌟 Acknowledgements

- **[eBay](https://www.ebay.com/)** — Data source (public listings)
- **[Selenium](https://www.selenium.dev/)** — Browser automation framework
- **[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)** — HTML parsing library
- **[Pandas](https://pandas.pydata.org/)** — Data manipulation library

---

## 📜 Licensing

### Code License
All source code and scripts in this repository are licensed under the **MIT License**  
(see the `LICENSE` file).

### Dataset License
The dataset file (`ebay_headphones_listings.csv`) is provided for **educational and research purposes only**.

**Dataset License:**  
Creative Commons Attribution–NonCommercial 4.0 International (CC BY-NC 4.0)

The dataset:
- Is derived from publicly available eBay listings
- Contains no private or personal data
- Must not be used for commercial resale or redistribution

This project is not affiliated with or endorsed by eBay Inc.



---

<p align="center">
  ⭐ If you find this dataset useful, please consider giving it a star! ⭐
</p>
