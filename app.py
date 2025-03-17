import streamlit as st
from data_ingestion import process_assets_and_labels
from tabs.performance_tab import show_performance_tab
from tabs.throughput_tab import show_throughput_tab
from tabs.utils import add_points_column, format_points_explanation

# Project configuration
project_id = 'cm7dgibsd0fy801bgdiqs7xjc'

# Set page configuration
st.set_page_config(
    page_title="Lean 4 Contribution Leaderboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def main():
    # Load and process data
    assets_df, assets_df_finished = process_assets_and_labels(project_id)
    assets_df = add_points_column(assets_df)
    

    # Display title and points explanation
    st.title("🏆 Lean 4 Contribution Leaderboard")
    st.write("Track performance and compete with your fellow contributors!")
    st.info(format_points_explanation())

    # Create tabs
    tab1, tab2 = st.tabs(["🥇 Performance & Activity", "📈 Throughput & Trends"])

    # Show content in each tab
    with tab1:
        show_performance_tab(assets_df)
    
    with tab2:
        show_throughput_tab(assets_df)

    # Add refresh button
    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

if __name__ == "__main__":
    main() 