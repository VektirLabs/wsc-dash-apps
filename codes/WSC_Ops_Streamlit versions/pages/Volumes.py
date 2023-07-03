import datetime
import plotly.graph_objects as go
import plotly_express as px
import streamlit as st
import pandas as pd
import numpy as np
from util import grid

# Set app config
st.set_page_config(
    page_title="Volumes",
    page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# pd.options.display.float_format = '{:, .4f}'.format
# pd.options.display.precision = 4

# Referecnes ------------------------------------------------------------------
 # https://streamlit-aggrid.readthedocs.io/en/docs/Usage.html#making-cells-editable
 # https://www.ag-grid.com/archive/22.0.0/javascript-grid-row-models/

# Helper functions ------------------------------------------------------------
def get_dummy():
        """"
        Function to get the forecast data
            - currently produces dummy data
            - returns dataFrame
        """
        df1 = pd.DataFrame({
            'Name': ["5'' DP", "8.75'' BHA", None],
            'Type': ["Drill Pipe", "BHA", None],
            'OD': [5.000, 8.75, None],
            'ID': [4.276, 3.978, None],
            'Top Depth (Md)': [0, 100, None],
            'Bottom Depth (Md)': [100, 200, None],
            })

        df2 = pd.DataFrame({
            'Name': ["13.625'' Surface Casing", "Open Hole"],
            'Type': ["Casing", "Open Hole"],
            'OD': [13.625, 9.625],
            'ID': [12.415, 9.625],
            'Top Depth (Md)': [0., 200.],
            'Bottom Depth (Md)': [200., 350.],
        })

        return [df1, df2]

def get_geo_dummy():
    return pd.DataFrame({
            'Formation Name': ["Albien", "Hrz"],
            'Top Depth (Md)': [0, 110],
            'Bottom Depth (Md)': [100, 145],
            'Top Depth (Tvd)': [0, 107],
            'Bottom Depth (Tvd)': [97, 135]
            })

def get_dfs():
    tdf = pd.DataFrame({
        'Name': [None, None, None, None, None, None, None, None],
        'Type': [None, None, None, None, None, None, None, None],
        'OD': [None, None, None, None, None, None, None, None],
        'ID': [None, None, None, None, None, None, None, None],
        'Top Depth (Md)': [None, None, None, None, None, None, None, None],
        'Bottom Depth (Md)': [None, None, None, None, None, None, None, None],
    })

    adf = pd.DataFrame({
        'Name': [None, None, None, None, None, None, None, None],
        'Type': [None, None, None, None, None, None, None, None],
        'OD': [None, None, None, None, None, None, None, None],
        'ID': [None, None, None, None, None, None, None, None],
        'Top Depth (Md)': [None, None, None, None, None, None, None, None],
        'Bottom Depth (Md)': [None, None, None, None, None, None, None, None],
    })

    return [tdf,adf]

def calculate_df(df):
    DF_OUT = df.copy()
    H_CONV = 1029.4

    DF_OUT['Capacity'] = np.divide(np.square(DF_OUT['ID']), H_CONV)
    DF_OUT["Displacement"] = np.divide((np.subtract(np.square(DF_OUT['OD']), np.square(DF_OUT['ID']))), H_CONV)
    # Todo: add error check if ID == None then ID = OD in the Open Hole case

    return DF_OUT

def expand_details(df):
    final_cols = ['Name', 'Type', 'OD', 'ID', 'Top Depth (Md)', 'Bottom Depth (Md)']
    df_out = pd.DataFrame()
    for index, row in df.iterrows():
        rx = np.subtract(df['Bottom Depth (Md)'][index], df['Top Depth (Md)'][index])
        if rx is not None and rx >= 0:
            temp_df = pd.DataFrame(np.repeat(df.iloc[[index]].values, rx, axis=0), columns=final_cols)
            df_out = pd.concat([df_out, temp_df]).reset_index(drop=True)
            df_out['Measured Depth'] = df_out.index + 1
    # Calc extra cols
    df_main = calculate_df(df_out)
    return df_main

def prepare(df):
    DF = df.copy()
    DF["MD"] = df.index + 1
    cols = ['MD', 'Name_Anl', 'Type_Anl', 'OD_Anl', 'ID_Anl', 'Capacity_Anl', 'Displacement_Anl',
            'Name_Tbl', 'Type_Tbl', 'OD_Tbl', 'ID_Tbl', 'Capacity_Tbl', 'Displacement_Tbl']
    DF = DF[cols].copy()
    DF['Ann x Tbl Name'] = DF['Name_Anl'].str.cat(DF['Name_Tbl'], sep="_x_")
    DF['Annulus Capacity'] = DF['Capacity_Anl'] - DF['Capacity_Tbl']
    DF['Total Volume'] = DF['Capacity_Anl'] + DF['Capacity_Tbl']
    DF = DF.apply(pd.to_numeric, errors='ignore')
    return DF

def build_report(df):
    DF_OUT = df.copy()

    t_rpt = pd.DataFrame()
    t_rpt.infer_objects()
    print(t_rpt.info())
    t_rpt['Type'] = DF_OUT.copy().groupby('Name_Tbl')['Type_Tbl'].first()
    t_rpt['Capacity (bbl/ft)'] = DF_OUT.copy().groupby('Name_Tbl')['Capacity_Tbl'].first()
    t_rpt['Length'] = DF_OUT.copy().groupby('Name_Tbl')['Capacity_Tbl'].count()
    t_rpt['Volume'] = DF_OUT.copy().groupby('Name_Tbl')['Capacity_Tbl'].sum()
    t_rpt.reset_index(drop=True)

    a_rpt = pd.DataFrame()
    a_rpt['Type'] = DF_OUT.copy().groupby('Name_Anl')['Type_Anl'].first()
    a_rpt['Capacity (bbl/ft)'] = DF_OUT.copy().groupby('Name_Anl')['Capacity_Anl'].first()
    a_rpt['Length'] = DF_OUT.copy().groupby('Name_Anl')['Capacity_Anl'].count()
    a_rpt['Volume'] = DF_OUT.copy().groupby('Name_Anl')['Capacity_Anl'].sum()
    a_rpt.reset_index(drop=True)

    at_rpt = pd.DataFrame()
    at_rpt['Type'] = DF_OUT.copy().groupby('Ann x Tbl Name')['Ann x Tbl Name'].first()
    # at_rpt['Capacity (bbl/ft)'] = DF_OUT.copy().groupby('Ann x Tbl Name')['Annulus Capacity'].first()
    at_rpt['Length'] = DF_OUT.copy().groupby('Ann x Tbl Name')['Annulus Capacity'].count()
    at_rpt['Volume'] = DF_OUT.copy().groupby('Ann x Tbl Name')['Total Volume'].sum()
    at_rpt.reset_index(drop=True)

    return t_rpt, a_rpt, at_rpt

# Get app tubular def and annulus df
TDF, ADF    = get_dfs()    # df empty
TDF1, ADF1  = get_dummy()  # df with dummy data
GDF = get_geo_dummy()
 
# Create Header Container -----------------------------------------------------
c1 = st.container()
with c1:
    c1.header("Volumes App")
    c1.markdown("""This app is designed to dynamically build a wellbore profile and 
    automatically calculate all volumes, strokes and times """)

    tab1, tab2, tab3  = st.tabs(["Instructions", "Input Info","Analysis & Report"])

    # Instructions Tab --------------------------------------------------------
    with tab1:
        c1, c2 = tab1.columns(2)
        with c1:
            st.markdown("#### **Instructions**")
            st.markdown("**Step 1** - Add each Tubular section starting from 0 to the end Measured depth in Ascending order - See example")
            st.markdown("**Step 2** - Add each Annulus section starting from 0 to the end Measured depth")
            st.markdown("**Step 3** - (Optional) Upload the directional survey data in the **Surveys** tab")
            st.markdown("**Step 4** - Preview Volume Analysis and Volume Reports")
            st.markdown("**Step 5** - QAQC and save your Analysis")
            st.markdown("**Step 6** - Share the Analysis and/or send in an email")

    # Input Data Tab ----------------------------------------------------------
    with tab2:
        c1, c2 = tab2.columns(2)
        with c1:
            # Tubular input section -------------------------------------------
            st.markdown("#### Tubular Info")
            st.markdown("""Please enter the current tubular string configuration 
                        information below. (i.e. Current drill string, tubing string, etc.)""")
            tubular_grid = grid.create_grid("T", TDF1) # todo: swap to original
        
            # Annulus input section -------------------------------------------            
            st.markdown("#### Annular Info")
            st.markdown("""Please enter the current annulus configuration 
                        information below (i.e. Last set Casing, Liner string, etc.)""")
            annular_grid = grid.create_grid("A", ADF1) # todo: swap to original
            
            # Optional input section -------------------------------------------
            with st.expander("Optional Input Information"):
                with st.form("Input Form"):
                    rig = st.selectbox("Select your Rig",("--","Doyon 19","Doyon 25", "Doyon 26","Doyon 142"))
                    well = st.text_input("Well Name")
                    
                    submitted = st.form_submit_button("Submit")
                if submitted:
                    st.write(f"Rig: {rig} on {well}")
                    
                st.markdown("#### Geology Info")
                st.markdown("Please enter the any Geologic formation information that is relevant to your operation")
                geo_grid = grid.create_geo_grid(GDF) # todo: swap to original
            
                st.markdown("#### Component Info")
                st.markdown("Please enter the information for any component that you would like to add")
                GDF #geo_grid = grid.create_geo_grid(GDF) # todo: swap to original
        
        # Well Schematic Section ----------------------------------------------  
        with c2:
            # https://github.com/CharlyWargnier/width-customizer-for-streamlit-apps/blob/main/streamlit_app.py
            st.markdown("#### Schematic Area")
            schematic = go.Figure()
            
            # schematic.add_trace(go.Scatter(
            #                         x=DF_MAIN['OD_Anl']*-1,
            #                         y='MD'
            #                         ) 
            #                     )
            
            st.plotly_chart(schematic,
                            use_container_width=True,
                            theme='streamlit'
                        )
           
    # Analysis & Report Tab ---------------------------------------------------
    with tab3:
        df_all = pd.merge(
            expand_details(annular_grid['data']),
            expand_details(tubular_grid['data']),
            how='outer',
            on='Measured Depth',
            suffixes=("_Anl", "_Tbl")
        )
        DF_MAIN = prepare(df_all)
        t_rpt, a_rpt, at_rpt = build_report(DF_MAIN)

        c1, c2, c3 = tab3.columns(3)
        with c1:
            st.markdown("#### Tubular Sections")
            t_rpt
            totals = f"""
            Totals: Length: {np.round(t_rpt['Length'].sum(),0)}  |-|  Volume: {np.round(t_rpt['Volume'].sum(),4)}
            """
            st.caption(totals)
        with c2:
            st.markdown("#### Annulus Sections")
            a_rpt
        with c3:
            st.markdown("#### Annulus x Tubular Sections")
            at_rpt

        st.markdown("---")
        st.markdown("#### Drillers Breakdown")
        c11, c22, c33 = tab3.columns(3)
        with c11:
            st.markdown("#### Tubular Breakdown")

        with c22:
            st.markdown("#### Annulus Breakdown")

        with c33:
            st.markdown("#### Total Breakdown")


        st.write(DF_MAIN)

