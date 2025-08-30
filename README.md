# S&P Investment Calculator

An interactive web application built with Streamlit to visualize long-term investment growth.

You can find a public deployment of this application [here](https://spcalc.ibalampanis.gr).

## Features

- **📅 Investment Start Date**: Define the exact month and year when you start investing
- **📊 Historical S&P 500 Returns**: Use actual historical S&P 500 return rates from different time periods (1957-2023, 2000-2023, 2010-2023, 1990-2023) or set custom rates
- **📈 Monthly Breakdown**: Detailed month-by-month analysis showing contribution amounts and estimated balance for each month of investment
- Calculate investment growth over time based on various parameters
- Visualize your investment journey with interactive charts
- Analyze contributions vs investment gains
- View yearly breakdown of investment performance
- Track return on investment (ROI) over time
- Export both yearly and monthly data to CSV for further analysis

## Installation

### Standard Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Using Docker

You can also run the application using Docker:

1. Clone this repository
2. Build and run the Docker container:

```bash
docker build -t sp-investment-calculator .
docker run -p 8501:8501 sp-investment-calculator
```

### Production Deployment

For production deployment, use the provided deployment script:

```bash
bash deploy.sh
```

The `deploy.sh` script provides automated deployment with the following features:
- Builds a Docker image for the application
- Runs the container with automatic restart policy
- Deploys on port 8585 for production use
- Includes `--upgrade` option to restart/update existing containers

Available options:
- `bash deploy.sh --upgrade`: Stops and removes existing container before deploying
- `bash deploy.sh --help`: Shows help information

## Usage

### Standard Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

### Docker Usage

If you're using Docker, access the application at:

```
http://localhost:8501
```

### Production Access

For the production deployment, the application is accessible at:

```
http://spcalc.ibalampanis.gr
```

The application will open in your default web browser.

## Investment Parameters

### Core Settings
- **Investment Start Date**: Choose the month and year to begin your investment journey
- **Initial Investment**: The lump sum amount you start with
- **Monthly Contribution**: The amount you contribute every month
- **Investment Period**: Number of years to project

### Return Rate Options
- **Historical S&P 500 Returns**: Select from actual historical periods:
  - Long-term Average (1957-2023): 10.5%
  - Recent Period (2000-2023): 8.2%
  - Last Decade (2010-2023): 12.9%
  - Last 30+ Years (1990-2023): 10.1%
- **Custom Expected Annual Return**: Set your own expected annual return percentage

### Advanced Options
- **Annual Increase in Contributions**: Yearly percentage increase in your monthly contributions
- **Annual Inflation Rate**: Optional adjustment for inflation
- **Lump Sum Investments**: Additional one-time investments at specific years (up to 5)

## Data and Calculations

### Investment Analysis
The application calculates:

- **Timeline Analysis**: Shows exact start and end dates based on your chosen start month/year
- **Monthly Projections**: Month-by-month breakdown showing:
  - Monthly contribution amounts
  - Running total of contributions
  - Investment gains each month
  - Total portfolio value
- **Yearly Summaries**: Annual analysis including total contributions and gains
- **Performance Metrics**: 
  - Total contributions over time
  - Investment gains from compound interest
  - Total value of your investment
  - Return on investment (ROI)
  - Compound annual growth rate (CAGR)

### Visualization Features
- **Summary Dashboard**: Overview with investment timeline and key metrics
- **Growth Charts**: Interactive line charts showing investment growth over time
- **Composition Analysis**: Stacked area charts showing contributions vs gains
- **Monthly Breakdown**: Detailed tables and charts for month-by-month analysis
- **ROI Tracking**: Performance visualization over the investment period
- **Data Export**: Download yearly or monthly data as CSV files

## Historical S&P 500 Data

The application includes historical S&P 500 return data for different periods:

| Period | Average Annual Return | Description |
|--------|----------------------|-------------|
| 1957-2023 | 10.5% | Long-term historical average including dividends |
| 2000-2023 | 8.2% | Recent period including dot-com crash and 2008 financial crisis |
| 2010-2023 | 12.9% | Bull market period following the 2008 crisis |
| 1990-2023 | 10.1% | Last 30+ years of market performance |

*Note: These returns include dividends and represent nominal (not inflation-adjusted) returns.*

## Disclaimer

This is a simulation tool and does not constitute financial advice. Past performance does not guarantee future results. The actual returns may vary significantly from projections. 

**Important Notes:**
- Historical returns are based on past performance and may not reflect future results
- The calculator assumes consistent monthly contributions and reinvestment of gains
- Real-world investing involves market volatility, fees, taxes, and other factors not accounted for in this simulation
- Always consult with a qualified financial advisor before making investment decisions

## License

[MIT](LICENSE)
