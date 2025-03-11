import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

def show_performance_tab(assets_df):
    # Create three columns for different time periods
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=False):
            # Get today's data
            today_df = assets_df[assets_df['createdAt'].dt.date == datetime.now().date()]
            today_leaders_html = ""
            if len(today_df) > 0:
                today_points = today_df.groupby('author')['points'].sum()
                today_leaders = today_points.sort_values(ascending=False).head(3)
                for i, (author, points) in enumerate(today_leaders.items()):
                    medal = ["🥇", "🥈", "🥉"][i]
                    today_leaders_html += f"""<div style='background-color: rgba(135, 206, 250, 0.2); padding: 10px; border-radius: 5px; margin: 5px;'>
                        <p style='text-align: center; margin: 0;'>{medal} <b>{author}</b>: {points:.1f} points</p>
                        </div>"""
            else:
                today_leaders_html = "<div style='text-align: center; padding: 10px;'>No contributions yet today!</div>"

            st.markdown(f"""
                <div style='background-color: rgba(135, 206, 250, 0.2); padding: 20px; border-radius: 10px;'>
                    <h3 style='text-align: center;'>Today's Champions 📅</h3>
                    {today_leaders_html}
                </div>""", unsafe_allow_html=True)

    with col2:
        with st.container(border=False):
            # Get weekly data
            week_df = assets_df[assets_df['createdAt'].dt.tz_localize(None) >= (pd.Timestamp.now() - timedelta(weeks=1))]
            week_leaders_html = ""
            if len(week_df) > 0:
                week_points = week_df.groupby('author')['points'].sum()
                week_leaders = week_points.sort_values(ascending=False).head(3)
                for i, (author, points) in enumerate(week_leaders.items()):
                    medal = ["🥇", "🥈", "🥉"][i]
                    week_leaders_html += f"""<div style='background-color: rgba(255, 223, 186, 0.2); padding: 10px; border-radius: 5px; margin: 5px;'>
                        <p style='text-align: center; margin: 0;'>{medal} <b>{author}</b>: {points:.1f} points</p>
                        </div>"""
            else:
                week_leaders_html = "<div style='text-align: center; padding: 10px;'>No contributions this week!</div>"

            st.markdown(f"""
                <div style='background-color: rgba(255, 223, 186, 0.2); padding: 20px; border-radius: 10px;'>
                    <h3 style='text-align: center;'>Weekly Stars 🌟</h3>
                    {week_leaders_html}
                </div>""", unsafe_allow_html=True)

    with col3:
        with st.container(border=False):
            # Get all-time data
            all_time_points = assets_df.groupby('author')['points'].sum()
            all_time_leaders = all_time_points.sort_values(ascending=False).head(3)
            all_time_leaders_html = ""
            for i, (author, points) in enumerate(all_time_leaders.items()):
                medal = ["🥇", "🥈", "🥉"][i]
                all_time_leaders_html += f"""<div style='background-color: rgba(152, 251, 152, 0.2); padding: 10px; border-radius: 5px; margin: 5px;'>
                    <p style='text-align: center; margin: 0;'>{medal} <b>{author}</b>: {points:.1f} points</p>
                    </div>"""

            st.markdown(f"""
                <div style='background-color: rgba(152, 251, 152, 0.2); padding: 20px; border-radius: 10px;'>
                    <h3 style='text-align: center;'>All-Time Heroes 👑</h3>
                    {all_time_leaders_html}
                </div>""", unsafe_allow_html=True)
            
    # Rising Stars and Most Regular Contributors
    st.write(" ")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Rising Stars")
            
            # Calculate growth rates
            last_week = assets_df[assets_df['createdAt'].dt.tz_localize(None) >= (pd.Timestamp.now() - timedelta(weeks=1))]
            prev_week = assets_df[(assets_df['createdAt'].dt.tz_localize(None) >= (pd.Timestamp.now() - timedelta(weeks=2))) & 
                                (assets_df['createdAt'].dt.tz_localize(None) < (pd.Timestamp.now() - timedelta(weeks=1)))]
            
            this_week_points = last_week.groupby('author')['points'].sum()
            prev_week_points = prev_week.groupby('author')['points'].sum()
            
            growth_rates = pd.DataFrame({
                'Current': this_week_points,
                'Previous': prev_week_points
            }).fillna(0)
            
            growth_rates['Growth'] = ((growth_rates['Current'] - growth_rates['Previous']) / (growth_rates['Previous'] + 1)) * 100
            growth_rates = growth_rates.sort_values('Growth', ascending=False).head(5)
            
            st.dataframe(
                growth_rates.round(1),
                column_config={
                    "Current": st.column_config.NumberColumn("This Week Points"),
                    "Previous": st.column_config.NumberColumn("Last Week Points"),
                    "Growth": st.column_config.ProgressColumn(
                        "Growth Rate",
                        format="%.1f%%",
                        min_value=0,
                        max_value=growth_rates['Growth'].max() * 1.1
                    )
                }
            )

        with col2:
            st.subheader("Most Regular Contributors")
            
            # Calculate consistency score based on weekly contributions
            four_weeks_ago = pd.Timestamp.now() - timedelta(weeks=4)
            weekly_df = assets_df[assets_df['createdAt'].dt.tz_localize(None) >= four_weeks_ago]
            
            # Group by author and week to get weekly contribution counts and points
            weekly_df['week'] = weekly_df['createdAt'].dt.isocalendar().week
            weekly_points = weekly_df.groupby(['author', 'week'])['points'].sum().unstack(fill_value=0)
            
            # Calculate consistency metrics
            consistency_scores = pd.DataFrame({
                'Active Weeks': (weekly_points > 0).sum(axis=1),
                'Avg Weekly Points': weekly_points.mean(axis=1).round(1),
                'Total Points': weekly_points.sum(axis=1).round(1)
            })
            
            # Sort by active weeks first, then by average points
            consistency_scores = consistency_scores.sort_values(
                ['Active Weeks', 'Avg Weekly Points'], 
                ascending=[False, False]
            ).head(5)
            
            st.dataframe(
                consistency_scores,
                column_config={
                    "Active Weeks": st.column_config.NumberColumn("Active Weeks (of 4)"),
                    "Avg Weekly Points": st.column_config.NumberColumn("Avg Weekly", format="%.1f"),
                    "Total Points": st.column_config.NumberColumn("Total")
                }
            )

    # Source Champions
    st.header("🎯 Source Champions")
    sources = assets_df['source'].unique()
    selected_source = st.selectbox("Select Source:", sources)
    
    source_df = assets_df[assets_df['source'] == selected_source]
    source_points = source_df.groupby('author')['points'].sum().sort_values(ascending=False).head(5)
    
    fig = px.bar(
        x=source_points.values,
        y=source_points.index,
        orientation='h',
        title=f"Top Contributors for {selected_source}",
        labels={'x': 'Points', 'y': 'Contributor'}
    )
    fig.update_traces(marker_color='skyblue')
    st.plotly_chart(fig, use_container_width=True) 