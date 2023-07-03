import streamlit as st
import pandas as pd
import cpyai as cp
# from utils import queries as q
from utils import schematic as sb
import numpy as np
from enum import Enum, auto
import plotly.graph_objects as go
#Teradata access
import cpyai as cp
from utils import queries as q
from dotenv import load_dotenv
import os
load_dotenv()

# App config --------------------------------------------------------
st.set_page_config(
    page_title="Schematic Apps",
    page_icon=":streamlit:",
    layout="wide",
    # initial_sidebar_state="collapsed"
)

# Globals - store the default value ---------------------------------
if 'show_setup' not in st.session_state:
    st.session_state['show_setup'] = True
if 'aut_well_name' not in st.session_state:
    st.session_state['aut_well_name'] = ''
if 'man_well_name' not in st.session_state:
    st.session_state['man_well_name'] = ''
if 'srvys_uploaded' not in st.session_state:
    st.session_state['srvys_uploaded'] = False
if 'visual_scale_factor' not in st.session_state:
    st.session_state['visual_scale_factor'] = 1
if 'inverse_scale_factor' not in st.session_state:
    st.session_state['inverse_scale_factor'] = -1

# Get default scale factor
VIZ_SF = st.session_state['visual_scale_factor']
INV_SF = st.session_state['inverse_scale_factor']

# Classes ---------------------------------------------------------------------
class SchematicType(Enum):
    MANUAL_ENTRY_CREATION = auto()
    MANUAL_UPLOAD_SURVEY_FILE = auto()
    AUTOMATIC_WELL_SCHEMATIC = auto()

class ColorScheme(Enum):
    LIGHT_GREY = 'rgba(50,50,50,0.2)'
    CASING_COLOR = 'rgba(0,0,0,1)'
    SHOE_COLOR = 'rgba(0,0,0,0.6)'
    LINER_COLOR = 'rgba(150,150,150,1)'
    OPENHOLE_COLOR = 'rgba(98,52,18,1)'
    PACKER_COLOR = 'rgba(50,50,50,0.2)'
    DRILLPIPE_COLOR = 'rgba(50,50,50,0.7)'
    BHA_COLOR = 'rgba(50,50,50,0.2)'
    BIT_COLOR = 'rgba(50,50,50,0.2)'

class WellSchematic:
    def __init__(self, df):
        self.df = df
        self.SHOE_WIDTH = 2
        self.SHOE_HEIGHT = 6
        self.OH_HEIGHT = 1
        self.ANNOTATE_OFFSET = 40

        self.CONV_MUD_GRADIENT = 1029.4

        # Color scheme
        self.LIGHT_GREY = 'rgba(50,50,50,0.2)'
        self.CASING_COLOR = 'rgba(0,0,0,1)'
        self.SHOE_COLOR = 'rgba(0,0,0,0.6)'
        self.LINER_COLOR = 'rgba(150,150,150,1)'
        self.OPENHOLE_COLOR = 'rgba(98,52,18,1)'
        self.PACKER_COLOR = 'rgba(50,50,50,0.2)'
        self.DRILLPIPE_COLOR = 'rgba(50,50,50,0.7)'
        self.BHA_COLOR = 'rgba(50,50,50,0.2)'
        self.BIT_COLOR = 'rgba(50,50,50,0.2)'

        # Figure Info
        self.F_HEIGHT = 650
        self.F_WIDTH = 50
        self.F_LAYOUT = go.Layout(
            height=self.F_HEIGHT,
            margin=dict(l=20, r=20, b=20, t=50, pad=20),
        )
        self.SCHEMATIC = go.Figure(layout=self.F_LAYOUT)
        self.get_figure = self.build_schematic()

    def build_schematic(self):
        # Get unique annular, tubular, geo, event component names -> list
        self.df["Comp_Desc"] = self.df["Type"] + " " + self.df["Name"]
        component_desc = self.df["Comp_Desc"].unique().tolist()

        # Get delta ranges
        self.df['Delta_shift'] = self.df["OD"].shift(-1)
        self.df['Deltas'] = self.df["OD"] - self.df["Delta_shift"]
        self.df['Deltas'] = self.df['Deltas'].apply(lambda x: x if x > 0 else 0)
        self.df['Deltas'] = self.df['Deltas'].shift(1)
        # st.table(self.df)

        # Expand df
        self.df = expand_dataframe(self.df)
        # Create a dictionary mapping each type to its corresponding color
        type_color_map = {
            'CSG': ColorScheme.CASING_COLOR.value,
            'TBG': ColorScheme.CASING_COLOR.value,
            'SH': ColorScheme.SHOE_COLOR.value,
            'LNR': ColorScheme.LINER_COLOR.value,
            'OH': ColorScheme.OPENHOLE_COLOR.value,
            'PKR': ColorScheme.PACKER_COLOR.value,
            'DP': ColorScheme.DRILLPIPE_COLOR.value,
            'HWDP': ColorScheme.CASING_COLOR.value,
            'DC': ColorScheme.CASING_COLOR.value,
            'BHA': ColorScheme.BHA_COLOR.value,
            'BIT': ColorScheme.BIT_COLOR.value,
        }

        # Calculate Left side schematic lines ()
        self.df['Y_axis_left_side'] = self.df['Bottom Depth (Md)'] * INV_SF
        self.df['X_axis_left_side'] = self.df['OD'] * (INV_SF * VIZ_SF)

        # Calculate Right side schematic lines
        self.df['Y_axis_right_side'] = self.df['Bottom Depth (Md)']
        self.df['X_axis_right_side'] = self.df['OD']

        # Set default colors into the df
        self.df['Color'] = self.df['Type'].apply(lambda x: type_color_map.get(x, ColorScheme.LIGHT_GREY.value))

        # Get well name from user input
        well_name = st.session_state['aut_well_name'] \
            if len(st.session_state['aut_well_name']) > 1 \
            else st.session_state['man_well_name']

        # Build and render the section lines
        for id, index_type in enumerate(self.df['Index Type'].unique()):
            # Filter the DataFrame for the current index type
            df_filtered = self.df[self.df['Index Type'] == index_type]
            df_filtered["default_Y"] = df_filtered['Bottom Depth (Md)'] * INV_SF
            name = self.df[self.df['Index Type'] == id]['Name'].unique()

            # Plot the left side
            self.SCHEMATIC.add_trace(
                go.Scatter(
                    x=df_filtered['X_axis_left_side'],
                    y=df_filtered["default_Y"],
                    mode='lines',
                    name=f"""{name[0]}""",
                    line=dict(
                        color=df_filtered['Color'].iloc[0],
                        dash='dot' if self.df[self.df['Index Type'] == id]['Type'].unique()[
                                           0] == "OH" else 'solid'
                    )
                )
            )

            # Plot the right side
            self.SCHEMATIC.add_trace(
                go.Scatter(
                    x=df_filtered['X_axis_right_side'],
                    y=df_filtered["default_Y"],
                    mode='lines',
                    name=f"""{name[0]}""",
                    showlegend=False,
                    line=dict(
                        color=df_filtered['Color'].iloc[0],
                        dash='dot' if self.df[self.df['Index Type'] == id]['Type'].unique()[
                                           0] == "OH" else 'solid'
                    )
                )
            )

            # Update the layout
            self.SCHEMATIC.update_layout(
                title=f'Well Name: {well_name}',
                xaxis_title='',
                yaxis_title='Measured Depth',
                legend_title='Section Name',
            )
            self.SCHEMATIC.update_xaxes(range=[-25, 75])

        # Add section components (shoe, liner top, completions, etc.)
        unique_components = self.df['Comp_Desc'].unique()
        for component in unique_components:
            if "CSG" in component:
                # Calculate shoe location coordinates
                SHOE_TOP_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min()
                SHOE_TOP_RIGHT = self.df[self.df["Comp_Desc"] == component]["Bottom Depth (Md)"].max() *-1
                SHOE_BTM_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min() + self.SHOE_WIDTH
                SHOE_BTM_RIGHT = self.df[self.df["Comp_Desc"] == component][
                                     "Bottom Depth (Md)"].min() + self.SHOE_HEIGHT

                # Create right triangle shoe path
                path = f'M {SHOE_TOP_LEFT}, {SHOE_TOP_RIGHT} L {SHOE_BTM_LEFT}, {SHOE_TOP_RIGHT} L {SHOE_TOP_LEFT}, {SHOE_TOP_RIGHT + self.SHOE_WIDTH}'

                # Add right triangle shoe to the Plotly figure
                self.SCHEMATIC.add_shape(
                    type='path',
                    path=path,
                    xref="x", yref="y",
                    line=dict(color='black', width=2),
                    fillcolor=ColorScheme.SHOE_COLOR.value,
                )

                # Create left triangle shoe path
                path = f'M {SHOE_TOP_LEFT*-1}, {SHOE_TOP_RIGHT} L {SHOE_BTM_LEFT*-1}, {SHOE_TOP_RIGHT} L {SHOE_TOP_LEFT*-1}, {SHOE_TOP_RIGHT + self.SHOE_WIDTH}'
                # Add left triangle shoe to the Plotly figure
                self.SCHEMATIC.add_shape(
                    type='path',
                    path=path,
                    xref="x", yref="y",
                    line=dict(color='black', width=2),
                    fillcolor=ColorScheme.SHOE_COLOR.value,
                )

            if "LNR" in component:
                # Calculate shoe location coordinates
                SHOE_TOP_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min()
                SHOE_TOP_RIGHT = self.df[self.df["Comp_Desc"] == component]["Bottom Depth (Md)"].max() * -1
                SHOE_BTM_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min() + self.SHOE_WIDTH
                SHOE_BTM_RIGHT = self.df[self.df["Comp_Desc"] == component]["Bottom Depth (Md)"].min() + self.SHOE_HEIGHT

                # Create right triangle shoe path
                path = f'M {SHOE_TOP_LEFT}, {SHOE_TOP_RIGHT} L {SHOE_BTM_LEFT}, {SHOE_TOP_RIGHT} L {SHOE_TOP_LEFT}, {SHOE_TOP_RIGHT + self.SHOE_WIDTH}'

                # Add right triangle shoe to the Plotly figure
                self.SCHEMATIC.add_shape(
                    type='path',
                    path=path,
                    xref="x", yref="y",
                    line=dict(color=self.SHOE_COLOR, width=1),
                    fillcolor=self.LINER_COLOR,
                )

                # Create left triangle shoe path
                path = f'M {SHOE_TOP_LEFT*-1}, {SHOE_TOP_RIGHT} L {SHOE_BTM_LEFT*-1}, {SHOE_TOP_RIGHT} L {SHOE_TOP_LEFT*-1}, {SHOE_TOP_RIGHT + self.SHOE_WIDTH}'
                # Add left triangle shoe to the Plotly figure
                self.SCHEMATIC.add_shape(
                    type='path',
                    path=path,
                    xref="x", yref="y",
                    line=dict(color=self.SHOE_COLOR, width=1),
                    fillcolor=self.LINER_COLOR,
                )

                # Calculate shoe location coordinates
                SHOE_TOP_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min()
                SHOE_TOP_RIGHT = self.df[self.df["Comp_Desc"] == component]["Bottom Depth (Md)"].min() * -1
                delta = self.df[self.df["Comp_Desc"] == component]["Deltas"].max()

                # Add right side square shoe
                self.SCHEMATIC.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=SHOE_TOP_LEFT,
                    y0=SHOE_TOP_RIGHT,
                    x1=SHOE_TOP_LEFT + delta ,
                    y1=SHOE_TOP_RIGHT + delta,
                    line=dict(color=self.SHOE_COLOR, width=1),
                    fillcolor=self.LINER_COLOR,
                )
                # Add left side square shoe
                self.SCHEMATIC.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=SHOE_TOP_LEFT*-1,
                    y0=SHOE_TOP_RIGHT,
                    x1=(SHOE_TOP_LEFT  + delta)*-1,
                    y1=SHOE_TOP_RIGHT + delta,
                    line=dict(color=self.SHOE_COLOR, width=1),
                    fillcolor=self.LINER_COLOR,
                )

            # if "DP" in component:
            #     SHOE_TOP_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min()
            #     # SHOE_TOP_RIGHT = self.df[self.df["Comp_Desc"] == component]["Bottom Depth (Md)"].max() * -1
            #     # SHOE_BTM_LEFT = self.df[self.df["Comp_Desc"] == component]["OD"].min() + self.SHOE_WIDTH
            #     # SHOE_BTM_RIGHT = self.df[self.df["Comp_Desc"] == component][
            #     #                      "Bottom Depth (Md)"].min() + self.SHOE_HEIGHT
            #
            #     # # Add right side square shoe
            #     # self.SCHEMATIC.add_shape(
            #     #     type="rect",
            #     #     xref="x", yref="y",
            #     #     x0=SHOE_TOP_LEFT,
            #     #     y0=SHOE_TOP_RIGHT,
            #     #     x1=SHOE_TOP_LEFT + delta,
            #     #     y1=SHOE_TOP_RIGHT + delta,
            #     #     line=dict(color=self.SHOE_COLOR, width=1),
            #     #     fillcolor=self.LINER_COLOR,
            #     # )
            #     # # Add left side square shoe
            #     # self.SCHEMATIC.add_shape(
            #     #     type="rect",
            #     #     xref="x", yref="y",
            #     #     x0=SHOE_TOP_LEFT * -1,
            #     #     y0=SHOE_TOP_RIGHT,
            #     #     x1=(SHOE_TOP_LEFT + delta) * -1,
            #     #     y1=SHOE_TOP_RIGHT + delta,
            #     #     line=dict(color=self.SHOE_COLOR, width=1),
            #     #     fillcolor=self.LINER_COLOR,
            #     # )
            #
            #     print(SHOE_TOP_LEFT, SHOE_TOP_RIGHT, SHOE_BTM_LEFT, SHOE_BTM_RIGHT, delta)

        return self.SCHEMATIC

    def get_schematic_df(self):
        self.df = self.df.sort_index()
        return self.df

    def calculate_schematic_vols(self):
        c_df = self.df.copy()
        tblr_df = c_df[c_df['Detail Type'] == 'Tubular Detail']
        anlr_df = c_df[c_df['Detail Type'] == 'Annular Detail']


# Sidebar ---------------------------------------------------------------------
sb = st.sidebar
with sb:
    show_setup = sb.checkbox('Show Setup', st.session_state['show_setup'])

# Data | Functions ------------------------------------------------------------

def get_dummies():
    """"
    Function to get the forecast data
        - currently produces dummy data
        - returns dataFrame
    """
    return  pd.DataFrame({
        'Name': ["13 3/8 Csg", "9 5/8 Csg", "Open Hole", "4.0 dp", "5.0 dp", "6.5 Bit"],
        'Type': ["CSG", "LNR", "OH", "DP", "BHA", "BIT"],
        'OD': [13.625, 9.625, 6.5, 4.000, 5.0, 6.5],
        'ID': [12.415, 8.853, 6.5, 3.276, 3.978, 6.5],
        'Top Depth (Md)': [0., 175., 350., 0, 450, 495],
        'Bottom Depth (Md)': [200., 350., 700., 450, 495, 500],
    })

def show_setup_cont():
    """
    Function call changes the value of the
    show_setup variable
    - This is used to hide the se objects
    :return: None
    """
    st.session_state['show_setup'] = False

def get_wh_info():
    df = pd.DataFrame()
    try:
        akdw = cp.AKDW()
        return "Success", akdw.query(f"{q.get_wv_well_names()}")
    except:
        return "Error", df

def detail_type(row):
    tubular_types = ["DP", "BIT", "HWDP", "DC", "BHA", "TBG"]
    if row['Type'] in tubular_types:
        return 'Tubular Detail'
    else:
        return 'Annular Detail'

def expand_dataframe(df):
    expanded_rows = []

    for index, row in df.iterrows():
        depths = np.arange(row['Top Depth (Md)'], row['Bottom Depth (Md)'], 1)
        for depth in depths:
            expanded_row = row.copy()
            expanded_row['Depth'] = depth
            expanded_row['Index Type'] = index
            expanded_rows.append(expanded_row)

    df = pd.DataFrame(expanded_rows).reset_index(drop=True)
    df = df.drop('Bottom Depth (Md)', axis=1)
    df = df.rename(columns={'Depth': 'Bottom Depth (Md)'})
    df['Detail Type'] = df.apply(detail_type, axis=1)


    return df

# Default header section ------------------------------------------------------
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.header("WSC - Schematic")
with c2:
    st.image('static/conoco_logo.png', width=225)
st.divider()

# Schematic containers
cont_setup = st.container()
cont_schematic = st.container()

# Show Setup
if show_setup:
    with cont_setup:
        c1, c2 = st.columns([0.45, 0.55])
        aut_well_name = st.session_state['aut_well_name']
        man_well_name = st.session_state['man_well_name']
        SURVEYS_UPLOADED = st.session_state['srvys_uploaded']
        rdo_create_type = c1.radio('Schematic Creation Type',
                                 ['Manual - Entry Creation',
                                  'Manual - Upload Survey File',
                                  'Automatic - Well Schematic'
                                  ])

        # If user select manual creation type
        if rdo_create_type == 'Manual - Entry Creation':
            if len(man_well_name) > 0:
                c1.markdown(f"""\t**Well Name**: {man_well_name}""")
            else:
                man_well_name = c1.text_input('Enter a Well Name')

            if len(man_well_name) > 0:
                btn_create = c1.button('Create Schematic', on_click=show_setup_cont())
                st.session_state['man_well_name'] = man_well_name
            else:
                btn_create = c1.button('Create Schematic', disabled=True)

        # If user select manual upload type
        elif rdo_create_type == 'Manual - Upload Survey File':
            if len(man_well_name) > 0:
                c1.markdown(f"""\t**Well Name**: {man_well_name}""")
            else:
                man_well_name = c1.text_input('Enter a Well Name')

            c1.markdown("#### **Upload your Survey Data**")

            # Create file uploader and check files type
            uploaded_file = c1.file_uploader("Choose file type ('.xlsx' or '.csv')", type=['xlsx', 'csv'])

            if uploaded_file is not None:
                try:
                    SURVEY_DATA = pd.read_excel(uploaded_file)
                except:
                    try:
                        SURVEY_DATA = pd.read_csv(uploaded_file)
                    except:
                        print("Error uploading Survey file")

                if SURVEY_DATA.columns is not None:
                    st.success('Survey file successfully uploaded!', icon="✅")
                    # st.markdown("##### Survey data preview")
                    # st.dataframe(SURVEY_DATA.head(5))
                    SURVEYS_UPLOADED = True

            if len(man_well_name) > 0 and SURVEYS_UPLOADED:
                btn_create = c1.button('Create Schematic', on_click=show_setup_cont())
            else:
                btn_create = c1.button('Create Schematic', disabled=True)

        # If user select Automatic creation type
        elif rdo_create_type == 'Automatic - Well Schematic':
            # Get well names from teradata
            msg = ""
            df = pd.DataFrame()
            @st.cache_data
            def get_wh_list():
                try:
                    akdw = cp.AKDW(
                        database_name=os.getenv("database_name"),
                        username=os.getenv("user_name"),
                        # password = os.getenv("password")
                        dotenv_path='.env')
                    return "Susscess", akdw.query(f"{q.get_wv_well_names()}")
                except Exception as e:
                    return 'Error: {e}', pd.DataFrame()

            # Create list of well names
            msg, df = get_wh_list()
            st.dataframe(df)
            wells_list = ['Select a Well']
            if msg == "Success":
                wv_wells = df.iloc[:, 0].to_list()
                wells_list.extend(wv_wells)
            else:
                wells_list = ['Select a Well']

            # Create st select box
            aut_well_name = c1.selectbox('Select Well Name', wells_list)

            if len(aut_well_name) > 0 and aut_well_name != 'Select a Well':
                btn_create = c1.button('Create Schematic', on_click=show_setup_cont())
            else:
                btn_create = c1.button('Create Schematic', disabled=True)

# Show Schematic
elif not show_setup:
    #todo: determine which type then build schematic to build
    with cont_schematic:
        tc1, tc2 = st.columns([0.4, 0.6], gap='medium')

        # Get temp data and filter
        df = get_dummies()
        tubular_df = df[df["Type"].isin(["DP", "BIT", "HWDP", "DC", "BHA", "TBG"])]
        annulus_df = df[df["Type"].isin(["CSG", "LNR", "OH"])]

        # Create each dynamic df
        tc1.markdown("#### Tubular Details")
        tc1.caption("""Please enter the current tubular string configuration information below. (i.e. Current drill
                          string, tubing string, etc.)""")
        edit_tubular_df = tc1.experimental_data_editor(
            tubular_df.reset_index(),
            num_rows='dynamic',
            use_container_width=True
        )

        tc1.markdown("#### Annulus Details")
        tc1.caption("""Please enter the current annulus configuration information below (i.e. Last set Casing, 
                       Liner string, etc.)""")
        edit_annulus_df = tc1.experimental_data_editor(
            annulus_df.reset_index(),
            num_rows='dynamic',
            use_container_width=True
        )

        # Combine edited df's
        out_df = pd.concat([edit_tubular_df, edit_annulus_df]).reset_index(drop=True).drop(columns='index')

        try:
            schematic_temp = WellSchematic(out_df)
            st.table(schematic_temp.get_schematic_df())  #rest
            df = schematic_temp.get_schematic_df()
            tc2.plotly_chart(
                schematic_temp.get_figure,
                use_container_width=True,
                theme='streamlit'
            )

            # Test build volumen calcs
            c_df = df.copy()
            c_df['Vol. Capacity (bbl/ft)'] = np.divide(np.square(c_df['ID']), 1029.4)
            tblr_df = c_df[c_df['Detail Type'] == 'Tubular Detail']
            anlr_df = c_df[c_df['Detail Type'] == 'Annular Detail']
            tblr_df = tblr_df.add_prefix('tblr_')
            anlr_df = anlr_df.add_prefix('anlr_')

            final_df = pd.merge(
                anlr_df,
                tblr_df,
                left_on='anlr_Bottom Depth (Md)',
                right_on='tblr_Bottom Depth (Md)',
                how='left'
            )

            # add annular capacities
            # other calcs

            st.table(final_df)

            # st.table(df)
        except:
            pass

    # st.table(exp_df)