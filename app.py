import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import calendar

# Set page config
st.set_page_config(
    page_title="S&P Investment Calculator", page_icon="📈", layout="wide"
)

# Historical S&P 500 annual returns data
@st.cache_data
def get_historical_sp500_data():
    """Returns historical S&P 500 annual returns (1957-2023)"""
    return {
        'period_name': {
            '1957-2023': 'Long-term Average (1957-2023)',
            '2000-2023': 'Recent Period (2000-2023)', 
            '2010-2023': 'Last Decade (2010-2023)',
            '1990-2023': 'Last 30+ Years (1990-2023)'
        },
        'returns': {
            '1957-2023': 10.5,  # Long-term average including dividends
            '2000-2023': 8.2,   # Including dot-com crash and 2008 crisis
            '2010-2023': 12.9,  # Bull market period
            '1990-2023': 10.1   # Last 30+ years
        }
    }

# Apply custom CSS
st.markdown(
    """
<style>
    .main {
        padding: 2rem;
    }
    .title {
        font-size: 3rem !important;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .subtitle {
        font-size: 1.5rem !important;
        margin-bottom: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Header
st.markdown('<p class="title">S&P Investment Calculator</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">Visualize your long-term investment growth</p>',
    unsafe_allow_html=True,
)

# Sidebar - Input Parameters
st.sidebar.header("Investment Parameters")

# Investment start date
st.sidebar.subheader("📅 Investment Start Date")
current_date = datetime.now()
start_month = st.sidebar.selectbox(
    "Start Month",
    options=list(range(1, 13)),
    format_func=lambda x: calendar.month_name[x],
    index=current_date.month - 1
)

start_year = st.sidebar.number_input(
    "Start Year",
    min_value=2020,
    max_value=2030,
    value=current_date.year,
    step=1
)

# Historical S&P 500 returns option
st.sidebar.subheader("📊 Return Rate Settings")
use_historical_returns = st.sidebar.checkbox(
    "Use Historical S&P 500 Returns",
    value=False,
    help="Check this to use actual historical S&P 500 return rates instead of a fixed rate"
)

if use_historical_returns:
    sp500_data = get_historical_sp500_data()
    selected_period = st.sidebar.selectbox(
        "Historical Period",
        options=list(sp500_data['returns'].keys()),
        format_func=lambda x: sp500_data['period_name'][x],
        index=0
    )
    annual_return = sp500_data['returns'][selected_period] / 100
    st.sidebar.info(f"Using {sp500_data['returns'][selected_period]:.1f}% annual return based on {sp500_data['period_name'][selected_period]}")
else:
    annual_return = (
        st.sidebar.slider(
            "Expected Annual Return (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.1
        )
        / 100
    )

# Starting amounts
initial_investment = st.sidebar.number_input(
    "Initial Investment (€)", min_value=0, max_value=1000000, value=50, step=50
)

monthly_contribution = st.sidebar.number_input(
    "Monthly Contribution (€)", min_value=0, max_value=10000, value=50, step=10
)

# Projection settings
years = st.sidebar.slider(
    "Investment Period (Years)", min_value=1, max_value=50, value=30, step=1
)

annual_increase_rate = (
    st.sidebar.slider(
        "Annual Increase in Contributions (%)",
        min_value=0.0,
        max_value=10.0,
        value=3.0,
        step=0.1,
    )
    / 100
)

annual_inflation_rate = (
    st.sidebar.slider(
        "Annual Inflation Rate (%)", min_value=0.0, max_value=10.0, value=0.0, step=0.1
    )
    / 100
)

# Lump Sum Investments
st.sidebar.header("Lump Sum Investments")
st.sidebar.markdown("Add one-time investments in specific years")

# Container to hold all lump sum inputs
lump_sums = []

# Allow up to 5 lump sum investments
lump_sum_count = st.sidebar.number_input(
    "Number of lump sums", min_value=0, max_value=5, value=0
)

for i in range(lump_sum_count):
    col1, col2 = st.sidebar.columns(2)
    with col1:
        year = st.number_input(
            f"Year #{i + 1}", min_value=1, max_value=years, value=min(5 * i + 5, years)
        )
    with col2:
        amount = st.number_input(
            f"Amount #{i + 1} (€)", min_value=0, max_value=1000000, value=1000
        )

    lump_sums.append((year, amount))

# Calculate results
monthly_rate = annual_return / 12
n_months = years * 12


# Calculate results (without progress bar for caching)
@st.cache_data
def calculate_investment_detailed(
    initial_investment,
    monthly_contribution,
    years,
    annual_return,
    annual_increase_rate,
    annual_inflation_rate,
    lump_sums,
    start_month,
    start_year,
):
    """Enhanced calculation function that tracks monthly details"""
    results_yearly = []
    results_monthly = []

    total_contributions = initial_investment
    total_value = initial_investment
    monthly_contrib = monthly_contribution
    monthly_rate = annual_return / 12

    # For inflation adjustment
    real_annual_return = (
        ((1 + annual_return) / (1 + annual_inflation_rate)) - 1
        if annual_inflation_rate
        else annual_return
    )
    real_monthly_rate = real_annual_return / 12

    current_month = start_month
    current_year = start_year

    for year in range(1, years + 1):
        year_start_value = total_value
        year_start_contributions = total_contributions
        
        for month in range(1, 13):
            # Add this month's contribution
            total_value = total_value * (1 + monthly_rate) + monthly_contrib
            total_contributions += monthly_contrib
            
            # Calculate current date
            display_month = ((current_month + month - 2) % 12) + 1
            display_year = current_year + ((current_month + month - 2) // 12)
            
            # Store monthly data
            investment_gain = total_value - total_contributions
            results_monthly.append({
                "Year": year,
                "Month": month,
                "Calendar_Month": display_month,
                "Calendar_Year": display_year,
                "Month_Name": calendar.month_name[display_month],
                "Monthly Contribution (€)": round(monthly_contrib, 2),
                "Total Contributions (€)": round(total_contributions, 2),
                "Investment Gain (€)": round(investment_gain, 2),
                "Total Value (€)": round(total_value, 2),
            })

        # Apply lump sums at year end if any
        lumps = [amount for (y, amount) in lump_sums if y == year]
        for lump in lumps:
            total_value += lump
            total_contributions += lump

        # Apply annual increase to monthly contributions
        monthly_contrib *= 1 + annual_increase_rate
        
        # Increment year for calendar tracking
        current_year += 1

        # Record year-end results for yearly analysis
        investment_gain = total_value - total_contributions
        results_yearly.append(
            {
                "Year": year,
                "Total Contributions (€)": round(total_contributions, 2),
                "Investment Gain (€)": round(investment_gain, 2),
                "Total Value (€)": round(total_value, 2),
            }
        )

    return pd.DataFrame(results_yearly), pd.DataFrame(results_monthly)


# Create a container for the progress message
progress_container = st.empty()

# Check if we need to recalculate (by checking if inputs have changed)
cache_key = (
    initial_investment,
    monthly_contribution,
    years,
    annual_return,
    annual_increase_rate,
    annual_inflation_rate,
    tuple(lump_sums),
    start_month,
    start_year,
)

# Show calculating message only if cache miss
if (
    "last_cache_key" not in st.session_state
    or st.session_state.last_cache_key != cache_key
):
    with progress_container:
        st.info("Calculating investment projection...")
    st.session_state.last_cache_key = cache_key

# Calculate the investment
df, df_monthly = calculate_investment_detailed(
    initial_investment,
    monthly_contribution,
    years,
    annual_return,
    annual_increase_rate,
    annual_inflation_rate,
    lump_sums,
    start_month,
    start_year,
)

# Clear the progress message
progress_container.empty()

# Calculate ROI for later use
df["ROI (%)"] = (df["Investment Gain (€)"] / df["Total Contributions (€)"]) * 100

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    ["Summary", "Growth Chart", "Composition", "Yearly Analysis", "ROI", "Monthly Breakdown", "Data Table"]
)

with tab1:
    # Create a summary of the investment
    final_value = df["Total Value (€)"].iloc[-1]
    total_contributions = df["Total Contributions (€)"].iloc[-1]
    investment_gain = df["Investment Gain (€)"].iloc[-1]
    roi_percent = df["ROI (%)"].iloc[-1]
    years_invested = years

    # Calculate start and end dates
    start_date = datetime(start_year, start_month, 1)
    end_date = start_date + timedelta(days=365 * years_invested)
    
    # Display investment timeline
    st.subheader("📅 Investment Timeline")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Start Date:** {start_date.strftime('%B %Y')}")
    with col2:
        st.info(f"**End Date:** {end_date.strftime('%B %Y')}")
    with col3:
        if use_historical_returns:
            st.info(f"**Return Rate:** {annual_return*100:.1f}% (Historical)")
        else:
            st.info(f"**Return Rate:** {annual_return*100:.1f}% (Custom)")

    st.subheader("💰 Financial Summary")
    
    # Calculate average annual return achieved
    cagr = (((final_value / initial_investment) ** (1 / years_invested)) - 1) * 100

    # Calculate how much of the final value is from contributions vs gains
    contribution_percent = (total_contributions / final_value) * 100
    gain_percent = (investment_gain / final_value) * 100

    # Display in three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Initial Investment", f"€{initial_investment:,.2f}")
        st.metric("Total Contributions", f"€{total_contributions:,.2f}")
        st.metric("Years Invested", f"{years_invested}")

    with col2:
        st.metric("Final Value", f"€{final_value:,.2f}")
        st.metric("Investment Gain", f"€{investment_gain:,.2f}")
        st.metric("Return on Investment", f"{roi_percent:.2f}%")

    with col3:
        st.metric("CAGR", f"{cagr:.2f}%")
        st.metric("Contributions %", f"{contribution_percent:.2f}%")
        st.metric("Investment Gains %", f"{gain_percent:.2f}%")

    # Create a pie chart to show the final breakdown
    final_contribs = df["Total Contributions (€)"].iloc[-1]
    final_gain = df["Investment Gain (€)"].iloc[-1]

    # Calculate percentages
    total = final_contribs + final_gain
    contrib_pct = (final_contribs / total) * 100
    gain_pct = (final_gain / total) * 100

    # Create the pie chart using Plotly
    labels = ["Contributions", "Investment Gain"]
    values = [final_contribs, final_gain]
    colors = ["#1f77b4", "#2ca02c"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.3,
                marker=dict(colors=colors, line=dict(color="#000000", width=2)),
                textposition="auto",
                textinfo="label+percent+value",
                texttemplate="%{label}<br>€%{value:,.0f}<br>(%{percent})",
                hovertemplate="%{label}<br>€%{value:,.0f}<br>%{percent}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title={
            "text": "Final Investment Breakdown",
            "font": {"size": 20},
            "x": 0.5,
            "xanchor": "center",
        },
        height=500,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05),
    )

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Investment Growth Over Time")

    # Create a line chart using Plotly
    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Total Value (€)"],
            mode="lines+markers",
            name="Total Value",
            line=dict(color="#2ca02c", width=3),
            marker=dict(size=8),
            hovertemplate="Year: %{x}<br>Total Value: €%{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Total Contributions (€)"],
            mode="lines+markers",
            name="Total Contributions",
            line=dict(color="#1f77b4", width=3),
            marker=dict(size=8, symbol="square"),
            hovertemplate="Year: %{x}<br>Total Contributions: €%{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Investment Gain (€)"],
            mode="lines+markers",
            name="Investment Gain",
            line=dict(color="#d62728", width=3),
            marker=dict(size=8, symbol="triangle-up"),
            hovertemplate="Year: %{x}<br>Investment Gain: €%{y:,.0f}<extra></extra>",
        )
    )

    # Add a horizontal line at y=0
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

    # Update layout
    fig.update_layout(
        title={
            "text": "Investment Growth Over Time",
            "font": {"size": 20},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Year",
        yaxis_title="Amount (€)",
        height=600,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Format y-axis
    fig.update_yaxes(tickformat=",.")

    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Composition of Investment Value Over Time")

    # Create a stacked area chart using Plotly
    fig = go.Figure()

    # Add traces
    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Total Contributions (€)"],
            mode="lines",
            name="Total Contributions",
            fill="tonexty",
            fillcolor="rgba(31, 119, 180, 0.7)",
            line=dict(color="#1f77b4", width=0),
            hovertemplate="Year: %{x}<br>Total Contributions: €%{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["Total Value (€)"],
            mode="lines",
            name="Investment Gain",
            fill="tonexty",
            fillcolor="rgba(44, 160, 44, 0.7)",
            line=dict(color="#2ca02c", width=2),
            hovertemplate="Year: %{x}<br>Total Value: €%{y:,.0f}<extra></extra>",
        )
    )

    # Add annotations
    final_year = df["Year"].iloc[-1]
    final_contribs = df["Total Contributions (€)"].iloc[-1]
    final_value = df["Total Value (€)"].iloc[-1]
    final_gain = df["Investment Gain (€)"].iloc[-1]

    fig.add_annotation(
        x=final_year,
        y=final_value,
        text=f"Final Total: €{final_value:,.0f}",
        showarrow=True,
        arrowhead=2,
        ax=-50,
        ay=-50,
    )

    # Update layout
    fig.update_layout(
        title={
            "text": "Composition of Investment Value Over Time",
            "font": {"size": 20},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Year",
        yaxis_title="Amount (€)",
        height=600,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Format y-axis
    fig.update_yaxes(tickformat=",.")

    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Yearly Contributions vs Investment Gains")

    # Create a new dataframe with yearly data (not cumulative)
    yearly_df = df.copy()
    yearly_df["Yearly Contribution"] = (
        yearly_df["Total Contributions (€)"]
        .diff()
        .fillna(yearly_df["Total Contributions (€)"].iloc[0])
    )
    yearly_df["Yearly Gain"] = (
        yearly_df["Investment Gain (€)"]
        .diff()
        .fillna(yearly_df["Investment Gain (€)"].iloc[0])
    )

    # Adjust the first year to account for initial investment
    yearly_df.loc[0, "Yearly Contribution"] = (
        initial_investment + monthly_contribution * 12
    )

    # Create grouped bar chart using Plotly
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=yearly_df["Year"],
            y=yearly_df["Yearly Contribution"],
            name="Yearly Contribution",
            marker_color="rgba(31, 119, 180, 0.7)",
            hovertemplate="Year: %{x}<br>Yearly Contribution: €%{y:,.0f}<extra></extra>",
        )
    )

    fig.add_trace(
        go.Bar(
            x=yearly_df["Year"],
            y=yearly_df["Yearly Gain"],
            name="Yearly Investment Gain",
            marker_color="rgba(44, 160, 44, 0.7)",
            hovertemplate="Year: %{x}<br>Yearly Gain: €%{y:,.0f}<extra></extra>",
        )
    )

    # Add annotations for lump sums
    for lump_year, lump_amount in lump_sums:
        if lump_year in yearly_df["Year"].values:
            idx = yearly_df[yearly_df["Year"] == lump_year].index[0]
            fig.add_annotation(
                x=lump_year,
                y=yearly_df["Yearly Contribution"].iloc[idx],
                text=f"Lump sum: €{lump_amount:,.0f}",
                showarrow=True,
                arrowhead=2,
                ax=0,
                ay=-40,
            )

    # Update layout
    fig.update_layout(
        title={
            "text": "Yearly Contributions vs Investment Gains",
            "font": {"size": 20},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Year",
        yaxis_title="Amount (€)",
        barmode="group",
        height=600,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Format y-axis
    fig.update_yaxes(tickformat=",.")

    # Adjust x-axis for many years
    if len(yearly_df) > 15:
        fig.update_xaxes(dtick=2)

    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Return on Investment (ROI) Over Time")

    # Create a line chart using Plotly
    fig = go.Figure()

    # Add ROI line
    fig.add_trace(
        go.Scatter(
            x=df["Year"],
            y=df["ROI (%)"],
            mode="lines+markers",
            name="ROI",
            line=dict(color="#9467bd", width=3),
            marker=dict(size=8),
            hovertemplate="Year: %{x}<br>ROI: %{y:.1f}%<extra></extra>",
        )
    )

    # Add horizontal line for annual return rate
    fig.add_hline(
        y=annual_return * 100,
        line_dash="dash",
        line_color="red",
        opacity=0.7,
        annotation_text=f"Annual Return Rate ({annual_return * 100:.1f}%)",
        annotation_position="right",
    )

    # Add annotation for final ROI
    final_roi = df["ROI (%)"].iloc[-1]
    fig.add_annotation(
        x=df["Year"].iloc[-1],
        y=final_roi,
        text=f"Final ROI: {final_roi:.1f}%",
        showarrow=True,
        arrowhead=2,
        ax=-50,
        ay=-50,
        font=dict(size=14, color="black"),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
    )

    # Update layout
    fig.update_layout(
        title={
            "text": "Return on Investment (ROI) Over Time",
            "font": {"size": 20},
            "x": 0.5,
            "xanchor": "center",
        },
        xaxis_title="Year",
        yaxis_title="ROI (%)",
        height=600,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    # Format y-axis
    fig.update_yaxes(tickformat=".1f", ticksuffix="%")

    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Monthly Breakdown")
    
    # Allow user to select specific years to view
    available_years = sorted(df_monthly['Calendar_Year'].unique())
    selected_years = st.multiselect(
        "Select years to display (leave empty for all years)",
        options=available_years,
        default=[],
        help="Choose specific years to view monthly details, or leave empty to see all years"
    )
    
    # Filter monthly data based on selection
    if selected_years:
        monthly_filtered = df_monthly[df_monthly['Calendar_Year'].isin(selected_years)]
    else:
        monthly_filtered = df_monthly
    
    if len(monthly_filtered) > 0:
        # Create tabs for different monthly views
        monthly_tab1, monthly_tab2, monthly_tab3 = st.tabs(["Monthly Table", "Monthly Chart", "Year Summary"])
        
        with monthly_tab1:
            st.subheader("Monthly Investment Schedule")
            
            # Format the monthly dataframe for display
            monthly_display = monthly_filtered.copy()
            monthly_display['Date'] = monthly_display['Month_Name'] + ' ' + monthly_display['Calendar_Year'].astype(str)
            
            # Select and reorder columns for better display
            display_columns = [
                'Date', 'Monthly Contribution (€)', 'Total Contributions (€)', 
                'Investment Gain (€)', 'Total Value (€)'
            ]
            monthly_display = monthly_display[display_columns]
            
            # Format currency columns
            for col in ['Monthly Contribution (€)', 'Total Contributions (€)', 'Investment Gain (€)', 'Total Value (€)']:
                monthly_display[col] = monthly_display[col].apply(lambda x: f"€{x:,.2f}")
            
            st.dataframe(monthly_display, use_container_width=True, height=400)
            
            # Download button for monthly data
            monthly_csv = monthly_filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download monthly data as CSV",
                monthly_csv,
                f"monthly_investment_data_{start_year}_{start_month}.csv",
                "text/csv",
                key="download-monthly-csv",
            )
            
            # Summary statistics for selected period
            total_months = len(monthly_filtered)
            total_contributions = monthly_filtered['Total Contributions (€)'].iloc[-1]
            total_value = monthly_filtered['Total Value (€)'].iloc[-1]
            total_gain = monthly_filtered['Investment Gain (€)'].iloc[-1]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Months", total_months)
            with col2:
                st.metric("Total Contributions", f"€{total_contributions:,.2f}")
            with col3:
                st.metric("Investment Gain", f"€{total_gain:,.2f}")
            with col4:
                st.metric("Total Value", f"€{total_value:,.2f}")
        
        with monthly_tab2:
            st.subheader("Monthly Growth Visualization")
            
            # Create monthly growth chart
            fig = go.Figure()
            
            fig.add_trace(
                go.Scatter(
                    x=monthly_filtered.index,
                    y=monthly_filtered["Total Value (€)"],
                    mode="lines+markers",
                    name="Total Value",
                    line=dict(color="#2ca02c", width=2),
                    marker=dict(size=4),
                    hovertemplate="%{text}<br>Total Value: €%{y:,.0f}<extra></extra>",
                    text=[f"{row['Month_Name']} {row['Calendar_Year']}" for _, row in monthly_filtered.iterrows()]
                )
            )
            
            fig.add_trace(
                go.Scatter(
                    x=monthly_filtered.index,
                    y=monthly_filtered["Total Contributions (€)"],
                    mode="lines+markers",
                    name="Total Contributions",
                    line=dict(color="#1f77b4", width=2),
                    marker=dict(size=4),
                    hovertemplate="%{text}<br>Total Contributions: €%{y:,.0f}<extra></extra>",
                    text=[f"{row['Month_Name']} {row['Calendar_Year']}" for _, row in monthly_filtered.iterrows()]
                )
            )
            
            fig.update_layout(
                title="Monthly Investment Growth",
                xaxis_title="Timeline",
                yaxis_title="Amount (€)",
                height=500,
                hovermode="x unified"
            )
            
            # Format y-axis
            fig.update_yaxes(tickformat=",.")
            
            st.plotly_chart(fig, use_container_width=True)
        
        with monthly_tab3:
            st.subheader("Year-by-Year Summary")
            
            # Group by calendar year for summary
            yearly_summary = monthly_filtered.groupby('Calendar_Year').agg({
                'Monthly Contribution (€)': 'sum',
                'Total Contributions (€)': 'last',
                'Investment Gain (€)': 'last',
                'Total Value (€)': 'last'
            }).reset_index()
            
            yearly_summary.columns = ['Year', 'Annual Contributions (€)', 'Total Contributions (€)', 'Investment Gain (€)', 'Total Value (€)']
            
            # Format for display
            yearly_display = yearly_summary.copy()
            for col in ['Annual Contributions (€)', 'Total Contributions (€)', 'Investment Gain (€)', 'Total Value (€)']:
                yearly_display[col] = yearly_display[col].apply(lambda x: f"€{x:,.2f}")
            
            st.dataframe(yearly_display, use_container_width=True)
    else:
        st.info("No data available for the selected years.")

with tab7:
    st.subheader("Investment Data Table")

    # Show filters
    show_options = st.multiselect(
        "Select columns to display", options=df.columns, default=list(df.columns)
    )

    # Format the dataframe for display
    @st.cache_data
    def format_df(df, show_options):
        # Create a copy to avoid modifying the original
        display_df = df[show_options].copy()

        # Format currency columns
        for col in display_df.columns:
            if "€" in col:
                display_df[col] = display_df[col].apply(lambda x: f"€{x:,.2f}")
            elif "%" in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%")

        return display_df

    display_df = format_df(df, show_options)
    st.dataframe(display_df, use_container_width=True)

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download data as CSV",
        csv,
        "investment_projection.csv",
        "text/csv",
        key="download-csv",
    )

# Footer
st.markdown("""
---
**Disclaimer**: This is a simulation tool and does not constitute financial advice. 
Past performance does not guarantee future results. The actual returns may vary.
""")