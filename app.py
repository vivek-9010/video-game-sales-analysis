import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import os

# Set up the app
st.set_page_config(layout="wide", page_title="Video Game Sales Analysis")
st.title("🎮 Video Game Sales Analysis Dashboard")
st.markdown("""
This interactive dashboard explores video game sales data using Python's data science stack.
""")

# Load data from reliable source
@st.cache_data
def load_data():
    try:
        # Using local file path - make sure the file exists in the same directory as your script
        file_path = os.path.join(os.path.dirname(__file__), 'vgsales.csv')
        df = pd.read_csv(file_path)
        
        # Basic data cleaning
        # Handle missing values in Year
        df['Year'] = df['Year'].fillna(df['Year'].median()).astype('Int64')
        
        # Handle missing Publisher values
        df['Publisher'].fillna('Unknown', inplace=True)
        
        # Create decade column
        df['Decade'] = (df['Year'] // 10) * 10
        
        # Calculate total sales (sum of all regional sales)
        df['Total_Sales'] = df[['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']].sum(axis=1)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs

df = load_data()

if df.empty:
    st.warning("No data loaded. Please make sure 'vgsales.csv' exists in the same directory as this script.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(int(df['Year'].quantile(0.25)), int(df['Year'].quantile(0.75))))
    
selected_platforms = st.sidebar.multiselect(
    "Select Platforms",
    options=sorted(df['Platform'].unique()),
    default=['PS2', 'X360', 'Wii'])

selected_genres = st.sidebar.multiselect(
    "Select Genres",
    options=sorted(df['Genre'].unique()),
    default=['Action', 'Sports', 'Shooter'])

# Apply filters
filtered_df = df[
    (df['Year'] >= selected_years[0]) & 
    (df['Year'] <= selected_years[1]) &
    (df['Platform'].isin(selected_platforms)) &
    (df['Genre'].isin(selected_genres))
]

# Main content tabs
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Sales Analysis", "Genre Insights", "Data Export"])

with tab1:
    st.header("Dataset Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Games", len(filtered_df))
        st.metric("Total Global Sales (millions)", round(filtered_df['Global_Sales'].sum(), 2))
    with col2:
        st.metric("Average Sales per Game", round(filtered_df['Global_Sales'].mean(), 2))
        st.metric("Time Span", f"{int(filtered_df['Year'].min())} - {int(filtered_df['Year'].max())}")
    st.subheader("Sample Data")
    st.dataframe(filtered_df.head(10)[['Name', 'Platform', 'Year', 'Genre', 'Publisher', 'Global_Sales']])

with tab2:
    st.header("Sales Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales by platform
        st.subheader("Sales by Platform")
        platform_sales = filtered_df.groupby('Platform')['Global_Sales'].sum().sort_values(ascending=False)
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        platform_sales.plot(kind='bar', color='skyblue', ax=ax1)
        ax1.set_title('Total Sales by Platform (in millions)')
        ax1.set_ylabel('Sales')
        plt.xticks(rotation=45)
        st.pyplot(fig1)
    
    with col2:
        # Regional sales comparison
        st.subheader("Regional Sales Distribution")
        regions = ['NA_Sales', 'EU_Sales', 'JP_Sales', 'Other_Sales']
        region_sales = filtered_df[regions].sum()
        fig2, ax2 = plt.subplots(figsize=(8, 8))
        region_sales.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax2)
        ax2.set_title('Regional Sales Distribution')
        ax2.set_ylabel('')
        st.pyplot(fig2)
    
    # Yearly trend
    st.subheader("Yearly Sales Trend")
    yearly_sales = filtered_df.groupby('Year')['Global_Sales'].sum()
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    yearly_sales.plot(kind='line', color='green', marker='o', ax=ax3)
    ax3.set_title('Yearly Sales Trend (in millions)')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Global Sales')
    ax3.grid(True)
    st.pyplot(fig3)

with tab3:
    st.header("Genre Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sales by Genre")
        genre_sales = filtered_df.groupby('Genre')['Global_Sales'].sum().sort_values(ascending=False)
        fig4, ax4 = plt.subplots(figsize=(10, 6))
        genre_sales.plot(kind='bar', color='purple', ax=ax4)
        ax4.set_title('Total Sales by Genre (in millions)')
        ax4.set_ylabel('Sales')
        plt.xticks(rotation=45)
        st.pyplot(fig4)
    
    with col2:
        st.subheader("Top Performing Games")
        top_games = filtered_df.sort_values('Global_Sales', ascending=False).head(10)
        st.dataframe(top_games[['Name', 'Platform', 'Year', 'Genre', 'Global_Sales']])
        
        st.subheader("Top Publishers")
        top_publishers = filtered_df.groupby('Publisher')['Global_Sales'].sum().nlargest(5)
        st.dataframe(top_publishers)

with tab4:
    st.header("Data Export")
    
    st.subheader("Filtered Data")
    st.dataframe(filtered_df)
    
    st.subheader("Download Options")
    
    # CSV download
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="video_game_sales_filtered.csv",
        mime="text/csv"
    )
    
    # Excel download
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='VideoGameSales')
    excel_data = output.getvalue()
    st.download_button(
        label="Download as Excel",
        data=excel_data,
        file_name="video_game_sales_filtered.xlsx",
        mime="application/vnd.ms-excel"
    )

# Footer
st.markdown("---")
st.markdown("""
**Built with:** Python, pandas, matplotlib, Streamlit
""")