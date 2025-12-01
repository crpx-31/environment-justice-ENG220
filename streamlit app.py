import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Configuration ---
st.set_page_config(
    page_title="CalEnviroScreen Action Toolkit",
    page_icon="📢",
    layout="wide"
)

# --- Load Data ---
@st.cache_data
def load_data():
    excel_file = "calenviroscreen40resultsdatadictionary_F_2021.xlsx"
    
    try:
        df_results = pd.read_excel(excel_file, sheet_name="CES4.0FINAL_results", engine='openpyxl')
        
        # Clean text columns to remove hidden spaces
        if 'California County' in df_results.columns:
            df_results['California County'] = df_results['California County'].astype(str).str.strip()
        if 'Approximate Location' in df_results.columns:
            df_results['Approximate Location'] = df_results['Approximate Location'].astype(str).str.strip()
            
        df_demo = pd.read_excel(excel_file, sheet_name="Demographic Profile", engine='openpyxl', header=1)
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()
    
    df_results['Census Tract'] = df_results['Census Tract'].astype(str)
    df_demo['Census Tract'] = df_demo['Census Tract'].astype(str)
    
    demo_cols = [
        'Census Tract', 'Children < 10 years (%)', 'Elderly > 64 years (%)',
        'Hispanic (%)', 'White (%)', 'African American (%)', 
        'Native American (%)', 'Asian American (%)'
    ]
    available_cols = [c for c in demo_cols if c in df_demo.columns]
    merged_df = pd.merge(df_results, df_demo[available_cols], on="Census Tract", how="left")
    
    return merged_df

try:
    df = load_data()
except FileNotFoundError:
    st.error("**File not found.** Ensure 'calenviroscreen40resultsdatadictionary_F_2021.xlsx' is present.")
    st.stop()

# --- Helper: Action Logic ---
def get_action_recommendations(row):
    """Returns a list of specific actions based on high indicators."""
    actions = []
    high_threshold = 75.0
    
    # Pollution Burden Actions
    if row.get('Diesel PM Pctl', 0) > high_threshold:
        actions.append(("🚚 High Diesel Pollution", "Advocate for truck re-routing, 'No Idling' signs near schools, and electrification of local delivery fleets."))
    if row.get('PM2.5 Pctl', 0) > high_threshold:
        actions.append(("🌫️ High Particle Pollution (PM2.5)", "Push for stricter permits on local industry, ban agricultural burning on bad air days, and increase vegetative buffers."))
    if row.get('Drinking Water Pctl', 0) > high_threshold:
        actions.append(("💧 Drinking Water Contaminants", "Demand a transparent water quality report from the local water board and apply for state infrastructure grants."))
    if row.get('Lead Pctl', 0) > high_threshold:
        actions.append(("🏠 Lead Paint Risk", "Request county-funded blood lead testing events and housing remediation grants for pre-1978 homes."))
    if row.get('Pesticides Pctl', 0) > high_threshold:
        actions.append(("🚜 Pesticide Exposure", "Advocate for notification systems before spraying and larger buffer zones (setbacks) near residential areas."))
    if row.get('Traffic Pctl', 0) > high_threshold:
        actions.append(("🚗 High Traffic Density", "Lobby for 'Complete Streets' (bike lanes, wider sidewalks), traffic calming bumps, and sound walls."))
    
    # Sensitive Population Actions
    if row.get('Asthma Pctl', 0) > high_threshold:
        actions.append(("🫁 High Asthma Rates", "Partner with local clinics for asthma management workshops and free indoor air filtration distribution."))
    
    return actions

# --- Sidebar Filters ---
st.sidebar.image("https://oehha.ca.gov/media/downloads/calenviroscreen/report/calenviroscreen40_logo.png", use_container_width=True)
st.sidebar.header("Step 1: Filter Region")

# County Filter
all_counties = sorted(df['California County'].unique().astype(str))
selected_counties = st.sidebar.multiselect("Select County", all_counties, default=["Fresno"])

# Percentile Slider
percentile_range = st.sidebar.slider(
    "Vulnerability Score Range", 
    0, 100, (75, 100),
    help="75-100% represents the most disadvantaged communities."
)

# Apply Sidebar Filters
if selected_counties:
    region_df = df[df['California County'].isin(selected_counties)]
else:
    region_df = df

region_df = region_df[
    (region_df['CES 4.0 Percentile'] >= percentile_range[0]) & 
    (region_df['CES 4.0 Percentile'] <= percentile_range[1])
]

# --- Main App Layout ---
st.title("📢 CalEnviroScreen Action Toolkit")
st.markdown("Use this tool to **Identify**, **Diagnose**, and **Act** on environmental injustice in your community.")

# Create Tabs for cleaner interface
tab1, tab2 = st.tabs(["🗺️ Explore Map", "🔍 Diagnose & Act"])

# --- TAB 1: EXPLORE ---
with tab1:
    st.subheader(f"Identifying Priority Areas in {', '.join(selected_counties) if selected_counties else 'California'}")
    st.markdown(f"Found **{len(region_df)}** census tracts matching your criteria.")

    if not region_df.empty:
        # Map
        fig_map = px.scatter_mapbox(
            region_df, 
            lat="Latitude", 
            lon="Longitude", 
            color="CES 4.0 Percentile", 
            size="Total Population",
            hover_name="Approximate Location", 
            hover_data=["Census Tract", "California County"],
            color_continuous_scale="RdYlGn_r", 
            range_color=[0, 100], 
            zoom=8, 
            height=500,
            title="Size = Population | Color = Vulnerability Score (Red is Worse)"
        )
        fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
        with st.expander("View Data List"):
            st.dataframe(
                region_df[['Census Tract', 'Approximate Location', 'CES 4.0 Percentile', 'Total Population']].sort_values('CES 4.0 Percentile', ascending=False),
                use_container_width=True
            )
    else:
        st.info("No areas match your filters. Try widening the Score Range or selecting more counties.")

# --- TAB 2: DIAGNOSE & ACT ---
with tab2:
    st.header("Community Deep Dive")
    st.markdown("Select a specific neighborhood to see exactly *why* it is scoring high and generate an advocacy plan.")
    
    col_filter1, col_filter2 = st.columns(2)
    
    # Smart Filters for Selection
    with col_filter1:
        # Filter by City to make finding Tracts easier
        cities = sorted(region_df['Approximate Location'].unique())
        selected_city = st.selectbox("1. Filter by City / Location", ["All"] + cities)
    
    with col_filter2:
        # Filter Tract dropdown based on City Selection
        if selected_city != "All":
            tract_options_df = region_df[region_df['Approximate Location'] == selected_city]
        else:
            tract_options_df = region_df
            
        tract_list = tract_options_df['Census Tract'].unique()
        selected_tract = st.selectbox("2. Select Census Tract ID", tract_list)

    # Get Data for Selected Tract
    if len(tract_options_df) > 0:
        row = region_df[region_df['Census Tract'] == selected_tract].iloc[0]
        
        st.divider()
        
        # --- DIAGNOSIS SECTION ---
        st.subheader(f"📍 Diagnosis: {row['Approximate Location']} (Tract {selected_tract})")
        
        # Top Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Overall Score", f"{row['CES 4.0 Percentile']:.1f}%", help="Percentile ranking in California (100 is worst)")
        m2.metric("Population", f"{row['Total Population']:,}")
        m3.metric("Poverty Rate", f"{row.get('Poverty Pctl', 0):.0f}%", help="Percentile relative to rest of state")
        m4.metric("Asthma Rate", f"{row.get('Asthma Pctl', 0):.0f}%", help="Percentile relative to rest of state")

        # Root Cause Analysis
        indicators = {
            'Diesel PM': row.get('Diesel PM Pctl', 0),
            'Drinking Water': row.get('Drinking Water Pctl', 0),
            'Pesticides': row.get('Pesticides Pctl', 0),
            'Lead Risk': row.get('Lead Pctl', 0),
            'Traffic Density': row.get('Traffic Pctl', 0),
            'PM2.5': row.get('PM2.5 Pctl', 0),
            'Cleanup Sites': row.get('Cleanup Sites Pctl', 0),
            'Groundwater Threats': row.get('Groundwater Threats Pctl', 0),
            'Hazardous Waste': row.get('Haz. Waste Pctl', 0)
        }
        # Get top 3
        top_causes = sorted(indicators.items(), key=lambda x: x[1], reverse=True)[:3]
        
        st.info("##### 🚨 Top 3 Pollution Drivers")
        c1, c2, c3 = st.columns(3)
        cols = [c1, c2, c3]
        for i, (cause, score) in enumerate(top_causes):
            with cols[i]:
                if score > 75:
                    st.error(f"**{cause}**\n\n{score:.1f}th Percentile")
                else:
                    st.warning(f"**{cause}**\n\n{score:.1f}th Percentile")

        # --- ACTION SECTION ---
        st.divider()
        st.subheader("🛠️ Take Action")
        
        col_actions, col_letter = st.columns([1, 1])
        
        with col_actions:
            st.markdown("**Recommended Steps**")
            recommendations = get_action_recommendations(row)
            if recommendations:
                for title, desc in recommendations:
                    with st.expander(title, expanded=False):
                        st.write(desc)
            else:
                st.success("No specific pollution indicators exceed the critical 75th percentile, though the overall score is high due to other combined factors.")

        with col_letter:
            st.markdown("**📝 Automated Advocacy Letter**")
            st.markdown("Copy this script to email your representatives.")
            
            high_issues = [f"{cause} ({score:.0f}th percentile)" for cause, score in top_causes if score > 70]
            issues_str = ", ".join(high_issues)
            
            letter_content = f"""Subject: Urgent Action Needed for {row['Approximate Location']} (Tract {selected_tract})

Dear Representative,

I am writing to urge immediate action for the community located in Census Tract {row['Census Tract']} in {row['Approximate Location']}.

According to the CalEnviroScreen 4.0 data, this neighborhood is in the {row['CES 4.0 Percentile']:.1f}th percentile for cumulative environmental burden, ranking it among the most disadvantaged in the state.

Specifically, the data identifies these critical drivers:
- {issues_str}

We request that you prioritize this neighborhood for:
1. Enhanced regulatory enforcement on local pollution sources.
2. Allocation of 'California Climate Investments' funding.
3. A community meeting to discuss mitigation strategies.

Sincerely,
[Your Name]"""
            
            st.text_area("Email Draft", letter_content, height=350)
            
    else:
        st.warning("No data available for the selected filters.")