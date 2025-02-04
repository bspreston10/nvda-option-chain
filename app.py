import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

df = pd.read_csv('/Users/bennett/Desktop/NVDIA Black Scholes/final_nvda_2023.csv')
unique_dates = df['Date'].unique()

# Streamlit Dashboard
st.set_page_config(page_title="NVIDIA Options Analytics Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("NVIDIA Options Analytics Dashboard")
option = st.sidebar.radio(
    "Select Analysis:",
    ('Implied Volatility Surface', 'Skew Analysis')
)

# --------------------------- Implied Volatility Surface --------------------------------
if option == "Implied Volatility Surface":
    st.title("Implied Volatility Surface")

    call_option = st.selectbox("Select Option Type:", ["Call", "Put"])
    date = st.selectbox("Select Date:", sorted(unique_dates))
    call_option ='C' if call_option.startswith('Call') else 'P'

    df_date = df[df['Date']==str(date)]
    if df_date.empty:
        st.warning("No data available for the selected date.")
    else:
        if call_option == 'C':
            df_option = df_date[['[DTE]', '[STRIKE]', '[C_IV]', '[C_VOLUME]']]
            pivot = df_option.pivot(index='[STRIKE]', columns='[DTE]', values='[C_IV]')
        else:
            df_option = df_date[['[DTE]', '[STRIKE]', '[P_IV]', '[P_VOLUME]']]
            pivot = df_option.pivot(index='[STRIKE]', columns='[DTE]', values='[P_IV]')

        pivot = pivot.fillna(method='ffill', axis=1).fillna(method='bfill', axis=1)
        X = np.tile(pivot.columns.values, (len(pivot), 1))
        Y = np.tile(pivot.index.values.reshape(-1, 1), (1, len(pivot.columns)))
        Z = pivot.values

        fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis', hovertemplate= 'Strike: %{y}<br>Days to Expiration: %{x}<br>IV: %{z}<extra></extra>')])
        fig.update_layout(
            title=f'Implied Volatility Surface for {date} ({call_option})',
            scene=dict(
                xaxis_title='Days to Expiration',
                yaxis_title='Strike Price',
                zaxis_title='Implied Volatility',
                aspectratio=dict(x=1.5, y=1.5, z=0.8),  # Adjust proportions
                camera=dict(eye=dict(x=1.8, y=1.8, z=1.2))  # Better viewing angle
            ),
            width=1000,  # Wider plot
            height=700,  # Taller plot
            margin=dict(l=0, r=0, b=0, t=50)  # Reduce margins for more space
        )

        st.plotly_chart(fig, use_container_width=True)

# -------------------- Skew Analysis --------------------
elif option == 'Skew Analysis':
    st.title("📊 Volatility Skew Analysis")

        # Get unique observation and expiration dates
    unique_observation_dates = sorted(df['Date'].unique())
    unique_expiration_dates = sorted(df['[EXPIRE_DATE]'].unique())

    # Use selectbox to ensure only available dates are selectable
    observation_date = st.selectbox('Observation Date:', unique_observation_dates)
    expiration_date = st.selectbox('Expiration Date:', unique_expiration_dates)

    subset = df[(df['Date'] == str(observation_date)) & (df['[EXPIRE_DATE]'] == str(expiration_date))]

    if subset.empty:
        st.warning('No data available for the selected dates.')
    else:
        underlying_last = subset['[UNDERLYING_LAST]'].values[0]
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=subset['[STRIKE]'], y=subset['[C_IV]'], mode='lines+markers', name='Call IV', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=subset['[STRIKE]'], y=subset['[P_IV]'], mode='lines+markers', name='Put IV', line=dict(color='red')))

        fig.add_vline(x=underlying_last, line_dash='dash', line_color='grey', line_width=1)

        fig.update_layout(
            title=f'Volatility Skew on {observation_date} (Expiring {expiration_date})',
            xaxis_title='Strike Price',
            yaxis_title='Implied Volatility',
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
