import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="CalEnviroScreen 4.0 Explorer",
    page_icon="🌍",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    # Define the name of your Excel file
    # Make sure this matches your actual filename exactly
    excel_file = "calenviroscreen40resultsdatadictionary_F_2021.xlsx"
    
    try:
        # Load the "CES 4.0 Results" sheet
        # Note: We use engine='openpyxl' to read xlsx files
        df_results = pd.read_excel(excel_file, sheet_name="CES4.0FINAL_results", engine='openpyxl')
        
        # Load the "Demographic Profile" sheet
        df_demo = pd.read_excel(excel_file, sheet_name="Demographic Profile", engine='openpyxl')
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()
    
    # Clean and Merge
    # Ensure Census Tract is the key (converting to string to match correctly)
    df_results['Census Tract'] = df_results['Census Tract'].astype(str)
    df_demo['Census Tract'] = df_demo['Census Tract'].astype(str)
    
    # Merge demographic columns into results
    # We select specific columns from demographic file to avoid duplicates
    demo_cols = [
        'Census Tract', 'Children < 10 years (%)', 'Elderly > 64 years (%)',
        'Hispanic (%)', 'White (%)', 'African American (%)', 
        'Native American (%)', 'Asian American (%)'
    ]
    
    # Check if columns exist before merging (handling potential variations in file versions)
    available_cols = [c for c in demo_cols if c in df_demo.columns]
    
    merged_df = pd.merge(df_results, df_demo[available_cols], on="Census Tract", how="left")
    
    return merged_df

try:
    df = load_data()
except FileNotFoundError:
    st.error("""
    **File not found.** Please make sure the file `calenviroscreen40resultsdatadictionary_F_2021.xlsx` is in the same folder as this app.
    """)
    st.stop()

# --- Sidebar ---
st.sidebar.header("Filter Options")

# 1. County Filter
counties = sorted(df['California County'].unique().astype(str))
selected_counties = st.sidebar.multiselect("Select County", counties, default=["Fresno", "Los Angeles"])

# 2. Percentile Slider
st.sidebar.subheader("Vulnerability Threshold")
percentile_range = st.sidebar.slider(
    "CES 4.0 Percentile Range (Higher = More Burdened)",
    min_value=0, max_value=100, value=(75, 100),
    help="Select the range of CalEnviroScreen scores. The top 25% (75-100) are typically designated as Disadvantaged Communities."
)

# --- Filtering Data ---
if selected_counties:
    filtered_df = df[df['California County'].isin(selected_counties)]
else:
    filtered_df = df # If nothing selected, show all

filtered_df = filtered_df[
    (filtered_df['CES 4.0 Percentile'] >= percentile_range[0]) & 
    (filtered_df['CES 4.0 Percentile'] <= percentile_range[1])
]

# --- Main Dashboard ---
st.title("🌍 CalEnviroScreen 4.0 Community Explorer")
st.markdown("""
This tool visualizes **cumulative pollution burdens** and **population vulnerabilities** using the official OEHHA 4.0 dataset.
Use the filters on the left to identify priority areas for advocacy and grant funding.
""")

# Top Level Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Census Tracts Selected", len(filtered_df))
col2.metric("Avg CES Percentile", f"{filtered_df['CES 4.0 Percentile'].mean():.1f}")
col3.metric("Total Population Impacted", f"{filtered_df['Total Population'].sum():,.0f}")

st.markdown("---")

# Row 1: Map and Pollution/Pop Char Scatter
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.subheader("📍 Interactive Map")
    if not filtered_df.empty:
        fig_map = px.scatter_mapbox(
            filtered_df,
            lat="Latitude",
            lon="Longitude",
            color="CES 4.0 Percentile",
            size="Total Population",
            hover_name="Approximate Location",
            hover_data=["Census Tract", "California County", "PM2.5 Pctl", "Asthma Pctl"],
            color_continuous_scale="RdYlGn_r", # Red is high score (bad), Green is low (good)
            range_color=[0, 100],
            zoom=8,
            height=500
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No data matches your filters.")

with row1_col2:
    st.subheader("📊 Key Indicators")
    st.markdown("**Top Pollution Drivers (Avg Percentile)**")
    
    # Calculate averages for key indicators in the filtered selection
    indicators = ['PM2.5 Pctl', 'Diesel PM Pctl', 'Drinking Water Pctl', 'Pesticides Pctl', 'Lead Pctl']
    # Filter only columns that exist (just in case)
    valid_indicators = [i for i in indicators if i in filtered_df.columns]
    
    if valid_indicators:
        avg_scores = filtered_df[valid_indicators].mean().sort_values(ascending=True)
        fig_bar = px.bar(
            x=avg_scores.values,
            y=avg_scores.index,
            orientation='h',
            labels={'x': 'Avg Percentile', 'y': 'Indicator'},
            color=avg_scores.values,
            color_continuous_scale="Reds"
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# Row 2: Demographics
st.subheader("👥 Community Demographics")
st.markdown("Who lives in these highly burdened areas?")

if not filtered_df.empty:
    # Prepare data for demographic pie chart (average of percentages)
    race_cols = ['Hispanic (%)', 'White (%)', 'African American (%)', 'Native American (%)', 'Asian American (%)']
    valid_race_cols = [c for c in race_cols if c in filtered_df.columns]
    
    if valid_race_cols:
        avg_demo = filtered_df[valid_race_cols].mean().reset_index()
        avg_demo.columns = ['Demographic', 'Percentage']
        
        fig_pie = px.pie(
            avg_demo, 
            values='Percentage', 
            names='Demographic',
            title='Average Racial/Ethnic Composition of Selected Tracts',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Sensitive Populations
    st.markdown("**Sensitive Populations (Average %)**")
    c1, c2 = st.columns(2)
    if 'Children < 10 years (%)' in filtered_df.columns:
        c1.info(f"Children (<10 yrs): **{filtered_df['Children < 10 years (%)'].mean():.1f}%**")
    if 'Elderly > 64 years (%)' in filtered_df.columns:
        c2.info(f"Elderly (>64 yrs): **{filtered_df['Elderly > 64 years (%)'].mean():.1f}%**")

# Row 3: Data Table
st.subheader("📋 Detailed Data View")
with st.expander("View Raw Data"):
    display_cols = ['Census Tract', 'California County', 'Approximate Location', 'CES 4.0 Score', 'CES 4.0 Percentile', 'Total Population']
    st.dataframe(filtered_df[display_cols].sort_values(by='CES 4.0 Percentile', ascending=False))

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_df)
    st.download_button(
        "Download Filtered Data as CSV",
        csv,
        "filtered_calenviroscreen_data.csv",
        "text/csv",
        key='download-csv'
    )