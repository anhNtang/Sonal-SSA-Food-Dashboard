import streamlit as st
import pandas as pd
import plotly.express as px
import json 


# Set up a layout suitable for dashboard
st.set_page_config(layout="wide")

# Create a title 
st.markdown("""
    <h1 style='text-align: center;
               color: white;
               background: linear-gradient(120deg, #1f4037, #99f2c8);
               padding: 20px;
               border-radius: 12px;'>
        Socioeconomic Spatial Analysis of US Food Access
    </h1>
""", unsafe_allow_html=True)

# Create five tabs 
st.markdown("###")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "State Breakdown", 
    "Drivers",
    "Map",
    "Insights"
])
    

# Robust data loading 

def load_data():
    data = pd.read_csv("master_dataset_only_common_counties.csv")
    # Ensure FIPS is string 
    data["CountyFIPS"] = data["CountyFIPS"].astype(str).str.zfill(5)
    return data
    

df = load_data()

# Load GeoJSON 
with open("geojson-counties-fips.json") as f:
    counties_geojson = json.load(f)


# Map state names to abbreviations
# Reason: locationmode="USA-states" only supports state abbreviations 
us_state_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

df["State_code"] = df["State"].map(us_state_abbrev)

# Modify the columns 
df['Food Insecurity Rate'] =(df['Overall Food Insecurity Rate']*100).round(2)
df['Population'] = df['Pop2010'].round(1)
df['Vulnerability Score'] = ((df['Vulnerability_Score_PCA']).round(2)).copy()
df['SNAP Participation Rate'] = (df['snap_participation_rate']*100).round(2)
df['Food_insecurity_risk_index'] = (df['food_insecurity_risk_index']*100).round(2)

# TAB 1: OVERVIEW 

with tab1: 
    if df is not None:
        # Select variables to be key metrics 
        metrics = ["MedianFamilyIncome", "PovertyRate", "unemployment_rate", 
                "Cost Per Meal", "SNAP Participation Rate", "# of Food Insecure Persons Overall", 
                "SNAP Threshold", "no_vehicle_rate", "Population, low access to store (%), 2019", 
                "Children, low access to store (%), 2019", "Seniors, low access to store (%), 2019", 
                "White, low access to store (%), 2019", "Black, low access to store (%), 2019", 
                "Hispanic ethnicity, low access to store (%), 2019", "Asian, low access to store (%), 2019",
                "American Indian or Alaska Native, low access to store (%), 2019", 
                "Hawaiian or Pacific Islander, low access to store (%), 2019", "obesity_pct", "diabetes_pct"]
        
        # Check if columns exist before grouping
        available_metrics = [m for m in metrics if m in df.columns]


    # Split the dashboard into two columns 
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        # Create a subheader for the map 
        st.subheader("Nationwide Spatial Distribution")

        # Create a selectbox for the key metrics 
        selected_metric = st.selectbox("Choose Metric", available_metrics, key="metric_select")
        
        # Aggregate data by state-level 
        df_state = df.groupby(["State", "State_code"], as_index=False)[selected_metric].mean() # State is a column in the dataframe, not the index 


        # Create a state-level US map that compares key metrics using a color scale 
        fig = px.choropleth(
            df_state,
            locations="State_code",
            locationmode="USA-states",
            color=selected_metric,
            scope="usa",
            color_continuous_scale="blues",
            labels = {"MedianFamilyIncome" : "Median Family Income", 
            "PovertyRate" : "Poverty Rate (%)", 
            "unemployment_rate" : "Unemployment Rate (%)", 
            "Cost Per Meal" : "Cost Per Meal ($)", 
            "obesity_pct" : "Obesity Percent", 
            "diabetes_pct" : "Diabetes Percent"},
            hover_data=['State', selected_metric]
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Statewide Metric Distribution")

        # Create a selectbox for states
        state_list = sorted(df["State"].unique().astype(str).tolist())
        options = ["All States"] + state_list # This includes the all state option  
        selected_state = st.selectbox("Select a state", options) 


        # Filter data based on state filter selection 
        if selected_state == "All States":
            df_filtered = df
            title_suffix = "Across all US Counties"
        else:
            df_filtered = df[df["State"] == selected_state]
            title_suffix = f"in {selected_state}"


        # Create the histogram 
        fig_hist = px.histogram(
        df_filtered, 
        x=selected_metric,
        nbins=30,
        title=f"Distribution of {selected_metric} {title_suffix}",
        color_discrete_sequence=["#eee600"], 
        labels={selected_metric: "Metric Value"}
        )

        fig_hist.update_layout(
            showlegend=False,
            margin=dict(l=20, r=20, t=50, b=20),
            height=400
        )

        st.plotly_chart(fig_hist, use_container_width=True)

    
    # Create the key metrics 
    st.subheader("Key Metrics", help="""
             Metric Definitions:
             - Food Insecurity: $%$ of population with limited food access.
             - Vulnerability Score: constructed metric using PCA results (see hypothesis 2 for more information).
             - SNAP Participation Rate: $%$ of food insecure population receiving benefits.
             """)


    # Create a function for styling key metric boxes 
    def kpi_card(title, value, color):
        return f"""
            <div style="
                background: {color};
                padding: 14px;
                border-radius: 10px;
                text-align: center;
                color: white;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
            ">
                <h5 style='margin-bottom:5px'>{title}</h5>
                <h2 style='margin:0;'>{value}</h2>
            </div>
        """
    
    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:
        pop_sum = int(df_filtered['Population'].sum())
        st.markdown(kpi_card("Population", f"{pop_sum:,}", "#6a4c93"), unsafe_allow_html=True)

    with col2:
        county_count = len(df_filtered)
        st.markdown(kpi_card("Number of Counties", f"{county_count}", "#4ecdc4"), unsafe_allow_html=True)

    with col3:
        st.markdown(kpi_card("SNAP Participation Rate", f"{df_filtered['SNAP Participation Rate'].mean():.2f}%", "#1a535c"), unsafe_allow_html=True)

    with col4:
        st.markdown(kpi_card("Vulnerability Score", f"{df_filtered['Vulnerability Score'].mean():.2f}", "#4ecdc4"), unsafe_allow_html=True)

    with col5:
        st.markdown(kpi_card("Food Insecurity Rate", f"{df_filtered['Food Insecurity Rate'].mean():.2f}%", "#ff6b6b"), unsafe_allow_html=True)
    



# TAB 2: STATE BREAKDOWN 
with tab2:

    # Part 1: Initialize the base dataframes for this tab 
    df_comparison = df.copy()

    state_level_count = pd.read_csv("county_level_count.csv")
    county_level_count = pd.read_csv("food_deserts_count.csv")

    # Part 2: Create navigation filters  
    level = st.radio('Select Level', ['County', 'State'], horizontal=True)

    if level == "County":
        selected_states = st.multiselect(
        "Filter Counties by State(s)",
        options=sorted(df["State"].dropna().unique()),
        default=None, 
        help="Select one or more states to compare their counties."
    )
        if selected_states:
            df_comparison = df_comparison[df_comparison["State"].isin(selected_states)]
        
        # Assign name labels for the counties
        df_comparison["Name"] = df_comparison["County"] + ", " + df_comparison["State"]
    
    else:
        # If the user selects "State", we use the entire dataset to aggregate 
        df_comparison = df_comparison.groupby("State").mean(numeric_only=True).round(2).reset_index()
        df_comparison["Name"] = df_comparison["State"]


    # Part 3: Create the comparison chart 
    st.markdown("---")
    st.subheader("Top Vulnerable Regions")

    metric = st.selectbox(
        "Select Metric to Rank",
        [
            "Vulnerability Score",
            "Food Insecurity Rate",
            "SNAP Participation Rate", 
            "Food Desert Count (0.5 & 10 miles)", 
            "Food Desert Count (1 & 10 miles)", 
            "Food Desert Count (1 & 20 miles)", 
            "Food Desert Count (Vehicle)"
        ],
        key="bar_metric"
    )

    # Define a dictionary for the Food Desert columns
    food_desert_map = {
        "Food Desert Count (0.5 & 10 miles)": {"County" : "LILATracts_halfAnd10", 
                                               "State" : "LILATracts_halfAnd10_flag"},
        "Food Desert Count (1 & 10 miles)": {"County" : "LILATracts_1And10", 
                                               "State" : "LILATracts_1And10_flag"},
        "Food Desert Count (1 & 20 miles)": {"County" : "LILATracts_1And20", 
                                               "State" : "LILATracts_1And20_flag"},
        "Food Desert Count (Vehicle)": {"County" : "LILATracts_Vehicle", 
                                               "State" : "LILATracts_Vehicle_flag"}
    }

    top_n = st.slider("Top N", 5, 20, 10)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top {top_n} {level} by {metric}")

        # Determine which dataframe and column to use
        if metric in food_desert_map:
            target_col = food_desert_map[metric][level]
            
            if level == "State":
                top_df = state_level_count.sort_values(target_col, ascending=False).head(top_n)
                top_df["Name"] = top_df["State"]
                hover_cols = [target_col] 
            else:
                # Create a temporary copy of the county counts
                temp_county_df = county_level_count.copy()
            
                # Filter the data 
                if selected_states:
                    temp_county_df = temp_county_df[temp_county_df["State"].isin(selected_states)]
            
                # Sort 
                top_df = temp_county_df.sort_values(target_col, ascending=False).head(top_n)
                top_df["Name"] = top_df["County"] + ", " + top_df["State"]
                hover_cols = ["State", target_col]
                
        else:
            # Use the standard aggregated dataframe
            target_col = metric 
            top_df = df_comparison.sort_values(target_col, ascending=False).round(2).head(top_n)
            # These columns exist in df_comparison because it's a copy of the main df
            hover_cols = ["Population", "PovertyRate", "MedianFamilyIncome", target_col]


        # This filter removes any column from hover_cols that isn't in top_df
        valid_hover_cols = [c for c in hover_cols if c in top_df.columns]

        fig_bar = px.bar(
            top_df,
            x=target_col,
            y='Name',
            orientation="h",
            hover_data=valid_hover_cols, 
            labels={
                "Population": "Population", 
                "PovertyRate": "Poverty Rate", 
                "MedianFamilyIncome": "Median Family Income", 
                target_col: metric
            }
        )
        # Make the chart shows the highest value at the top
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("Data Summary")
        st.dataframe(df_comparison, use_container_width=True, height=450)


# TAB 3: Drivers 
with tab3:

    st.subheader("What Drives Food Insecurity?")
    df['PovertyRate'] = df['PovertyRate'].round(2)
    df['MedianFamilyIncome'] = df['MedianFamilyIncome'].round(2)
    features = [
        "PovertyRate",
        "MedianFamilyIncome",
        "SNAP Participation Rate"
    ]

    target = "Food Insecurity Rate"

    col1, col2 = st.columns(2)

    # Scatter
    with col1:

        st.subheader("Scatter Analysis")
        c1, c2 = st.columns(2)
        with c1:
            x_var = st.selectbox(
                "X-axis",
                features,
            key="scatter_x"
            )

        with c2:
            y_var = st.selectbox(
            "Y-axis",
            ["Food Insecurity Rate"],
            key="scatter_y"
        )
            
        if "PovertyRate" in top_df.columns:
            fig_scatter = px.scatter(
                top_df,
                x=x_var,
                y=y_var,
                size="Population",
                color="food_insecurity_risk_index",
                hover_name="Name"
            )

            st.plotly_chart(fig_scatter, width='stretch')
        else:
            st.info("Scatter plot analysis is not available if you select a food desert count metric in State Breakdown.")

    # Heatmap
    
    with col2:
       
        st.subheader('Correlation heatmap')
        st.markdown("###")
        corr = df[[
            "PovertyRate",
            "Food Insecurity Rate",
            "MedianFamilyIncome",
            "SNAP Participation Rate",
            "Vulnerability Score"
        ]].corr().round(2)

        fig_heat = px.imshow(corr, text_auto=True, color_continuous_scale="Viridis")
        st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""
        **Insight:** Poverty and income are the strongest drivers of food insecurity.
        """)
    
# TAB 4: Map
with tab4:

    st.header("Geographic Distribution")

    st.subheader("Filters")


    selected_states = st.multiselect(
        "Select State(s)",
        options=sorted(df["State"].unique()),
        default=None
    )

    if selected_states:
        df = df[df["State"].isin(selected_states)]


    fig_map = px.choropleth(
        df,
        geojson=counties_geojson,
        locations="CountyFIPS",
        color="Food Insecurity Rate",
        color_continuous_scale=[
            [0, "#fff5eb"],
            [0.5, "#fd8d3c"],
            [1, "#bd0026"]
        ],
        scope="usa",
        hover_data=[
            "County",
            "State",
            "Population",
            "PovertyRate",
            "MedianFamilyIncome",
            "Food Insecurity Rate", 
            "Vulnerability Score"
            
        ]

    )

    if selected_states:
        fig_map.update_geos(fitbounds="locations", visible=False)
    else:
        fig_map.update_geos(visible=False)
    st.plotly_chart(fig_map, use_container_width=True, height=700)

# TAB 5: Insights
with tab5:
    col1, col2 = st.columns(2)

    with col1:
        df["Risk_Level"] = pd.qcut(
        df["Vulnerability Score"],
        q=3,
        labels=["Low", "Medium", "High"]
    )
        st.subheader("Food Insecurity Distribution by Risk Level")

        fig_box = px.box(
            df,
            x="Risk_Level",
            y="Food Insecurity Rate",
            color="Risk_Level",
            points="outliers", 
            color_discrete_map= {
                "Low" : "#8DD3C7", 
                "Medium" : "#E3E318", 
                "High" : "#FB8072"
            }
        )

        st.plotly_chart(fig_box, use_container_width=True)

    with col2:
        df["Income_Group"] = pd.qcut(df["MedianFamilyIncome"], q=3, labels=["Low", "Mid", "High"])

        st.subheader("Risk Level Comparison by Income Groups")

        fig_stack = px.histogram(
            df,
            x="Income_Group",
            color="Risk_Level",
            barmode="stack", 
            # Explicitly define the order for the x-axis
            category_orders={
                "Income_Group": ["Low", "Mid", "High"],
                "Risk_Level": ["Low Risk", "Medium Risk", "High Risk"] 
                }, 
            color_discrete_map= {
                "Low" : "#8DD3C7", 
                "Medium" : "#FFFFB3", 
                "High" : "#FB8072"
            }
            )

        st.plotly_chart(fig_stack, use_container_width=True)

    

    st.markdown("""
        ## Policy Insights 
    """)

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        st.markdown("""
             ### Key Findings:
            - High food insecurity strongly correlates with poverty levels
            - Vulnerability clusters in specific geographic regions
            - SNAP participation alone is insufficient
        """)

    with right_col:
        st.markdown("""
            ### Recommendations:
            1. Expand SNAP coverage in high-risk counties
            2. Improve food access infrastructure (transport, stores)
            3. Combine income support + food programs
        """)

    st.markdown("""
        ### Impact:
        Targeting top 10% vulnerable counties could significantly reduce national food insecurity rates.
        """)
    





    
   

   
