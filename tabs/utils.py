import pandas as pd

def add_points_column(df):
    """Add points column to the dataframe based on source."""
    df['points'] = df['source'].map({
        'AIME': 1.5,
        'AMC': 1.0
    })
    return df

def format_points_explanation():
    """Return formatted points system explanation."""
    return ("📊 Points System:\n"
            "• AIME Problem = 1.5 points\n"
            "• AMC Problem = 1.0 points") 