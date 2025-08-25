# S&P Investment Calculator

An interactive web application built with Streamlit to visualize long-term investment growth.

You can find a public deployment of this application [here](https://spcalc.ibalampanis.gr).

## Features

- Calculate investment growth over time based on various parameters
- Visualize your investment journey with interactive charts
- Analyze contributions vs investment gains
- View yearly breakdown of investment performance
- Track return on investment (ROI) over time
- Export data to CSV for further analysis

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

Or, using Docker Compose:

```bash
docker-compose up
```

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

The application will open in your default web browser at http://localhost:8501.

## Investment Parameters

- **Initial Investment**: The lump sum amount you start with
- **Monthly Contribution**: The amount you contribute every month
- **Investment Period**: Number of years to project
- **Expected Annual Return**: The average annual return on your investment
- **Annual Increase in Contributions**: Yearly percentage increase in your monthly contributions
- **Annual Inflation Rate**: Optional adjustment for inflation
- **Lump Sum Investments**: Additional one-time investments at specific years

## Data and Calculations

The application calculates:

- Total contributions over time
- Investment gains from compound interest
- Total value of your investment
- Return on investment (ROI)
- Compound annual growth rate (CAGR)

## Disclaimer

This is a simulation tool and does not constitute financial advice. Past performance does not guarantee future results. The actual returns may vary.

## License

[MIT](LICENSE)
