import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def show_throughput_tab(assets_df):
    st.header("📈 Throughput Analysis")
    
    # Date range selector
    date_range = st.slider(
        "Select Date Range:",
        min_value=assets_df['createdAt'].min().date(),
        max_value=assets_df['createdAt'].max().date(),
        value=(assets_df['createdAt'].min().date(), assets_df['createdAt'].max().date())
    )
    
    start_date, end_date = date_range
    filtered_df = assets_df[
        (assets_df['createdAt'].dt.date >= start_date) & 
        (assets_df['createdAt'].dt.date <= end_date)
    ]
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_points = filtered_df['points'].sum()
        st.metric("Total Points", f"{total_points:,.1f}")
    with col2:
        active_contributors = filtered_df['author'].nunique()
        st.metric("Active Contributors", active_contributors)
    with col3:
        avg_daily_points = total_points / max(1, (end_date - start_date).days)
        st.metric("Average Daily Points", f"{avg_daily_points:.1f}")
    
    # Daily trend chart
    daily_counts = filtered_df.groupby(filtered_df['createdAt'].dt.date).agg({
        'points': 'sum',
        'author': 'nunique'
    }).reset_index()
    daily_counts.columns = ['Date', 'Points', 'Contributors']
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=daily_counts['Date'],
        y=daily_counts['Points'],
        name='Points',
        marker_color='skyblue'
    ))
    fig.add_trace(go.Scatter(
        x=daily_counts['Date'],
        y=daily_counts['Contributors'],
        name='Active Contributors',
        yaxis='y2',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title='Daily Points and Active Contributors',
        yaxis=dict(title='Points'),
        yaxis2=dict(title='Number of Contributors', overlaying='y', side='right'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Source distribution
    st.subheader("Distribution by Source")
    source_points = filtered_df.groupby('source')['points'].sum().reset_index()
    source_points.columns = ['Source', 'Points']
    
    fig = px.pie(
        source_points,
        values='Points',
        names='Source',
        title='Points Distribution by Source'
    )
    st.plotly_chart(fig, use_container_width=True) 