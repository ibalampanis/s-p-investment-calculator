import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="S&P Investment Calculator", page_icon="📈", layout="wide"
)

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

annual_return = (
    st.sidebar.slider(
        "Expected Annual Return (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.1
    )
    / 100
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
def calculate_investment(
    initial_investment,
    monthly_contribution,
    years,
    annual_return,
    annual_increase_rate,
    annual_inflation_rate,
    lump_sums,
):
    results = []

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

    for year in range(1, years + 1):
        for month in range(1, 13):
            # Add this month's contribution
            total_value = total_value * (1 + monthly_rate) + monthly_contrib
            total_contributions += monthly_contrib

        # Apply lump sums at year end if any
        lumps = [amount for (y, amount) in lump_sums if y == year]
        for lump in lumps:
            total_value += lump
            total_contributions += lump

        # Apply annual increase to monthly contributions
        monthly_contrib *= 1 + annual_increase_rate

        # Record year-end results
        investment_gain = total_value - total_contributions
        results.append(
            {
                "Year": year,
                "Total Contributions (€)": round(total_contributions, 2),
                "Investment Gain (€)": round(investment_gain, 2),
                "Total Value (€)": round(total_value, 2),
            }
        )

    return pd.DataFrame(results)


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
df = calculate_investment(
    initial_investment,
    monthly_contribution,
    years,
    annual_return,
    annual_increase_rate,
    annual_inflation_rate,
    lump_sums,
)

# Clear the progress message
progress_container.empty()

# Calculate ROI for later use
df["ROI (%)"] = (df["Investment Gain (€)"] / df["Total Contributions (€)"]) * 100

# Create tabs for different visualizations
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Summary", "Growth Chart", "Composition", "Yearly Analysis", "ROI", "Data Table"]
)

with tab1:
    # Create a summary of the investment
    final_value = df["Total Value (€)"].iloc[-1]
    total_contributions = df["Total Contributions (€)"].iloc[-1]
    investment_gain = df["Investment Gain (€)"].iloc[-1]
    roi_percent = df["ROI (%)"].iloc[-1]
    years_invested = years

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