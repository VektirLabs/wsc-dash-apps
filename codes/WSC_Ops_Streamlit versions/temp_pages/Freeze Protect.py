import datetime
import plotly.graph_objects as go
import plotly_express as px
import streamlit as st
import pandas as pd
import numpy as np

# Set app config
st.set_page_config(
    page_title="Freeze Protect Ops",
    page_icon=":streamlit",
    layout="wide",
    initial_sidebar_state="collapsed"
)
# Referecnes ------------------------------------------------------------------
 # https://streamlit-aggrid.readthedocs.io/en/docs/Usage.html#making-cells-editable

# Vars ------------------------------------------------------------------------
MW_GRADIENT = 0.052
AREA_FACTOR = 1029.4
FT_MD_LABEL = "' ft md"
FT_TVD_LABEL = "' ft tvd"
MW_LABEL = " ppg"
VOL_LABEL = " bls"
PSI_LABEL = " psi"
EMW_LABEL = " EMW PSI"
SURVEYS_UPLOADED = False
SURVEY_DATA = pd.DataFrame()

# Helper functions ------------------------------------------------------------

# Create header container
c1 = st.container()
with c1:
    c1.header("Freeze Protect Ops")
    c1.markdown("""This app is designed to calculate the Freeze Protect 
                pump schedule and other critical information pertaining to
                Freeze Protecting Operations.""")

# Create app container --------------------------------------------------------
c2 = st.container()
with c2:
    # Create tab layout for the Freeze Protect Ops app
    t1, t2, t3, t4, t5, t6 = st.tabs(["Instructions", "Well Data", "Surveys",
                                      "Analysis", "Pump Schedule(s)", "Finalize"
                                     ])

    # Instructions Tab --------------------------------------------------------
    with t1:
        st.markdown("#### **Freeze Protect Disclaimer**")
        st.caption("The use of the data and/or analysis should always be double checked")
        st.markdown("---")

        st.markdown("#### **Instructions**")
        st.markdown("**Step 1** - Enter the current wells data in the **Well Data** tab")
        st.markdown("**Step 2** - Upload the directional survey data in the **Surveys** tab")
        st.markdown("**Step 3** - Preview and QA/QC the **Analysis** tab for accuracy")
        st.markdown("**Step 4** - Preview and QA/QC the **Pump Schedule(s)** tab for accuracy")
        st.markdown("**Step 5** - Preview the **Finalize** tab and send communication email to the team")

    # Well Data Tab -----------------------------------------------------------
    with t2:
        st.markdown("### **Well Data**") # ------------------------------------
        st.write("Please enter you current wells data")
        # st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown("##### General Well Info")# -------------------------------
        c1.markdown("---")

        well_name = c1.text_input("Well Name") # ------------------------------
        mud_weight_oa = c1.number_input("Mud Weight in OA")

        c2.markdown("##### Casing Info") # ------------------------------------
        c2.markdown("---")
        surf_csg_shoe_md = c2.number_input("Surface Csg MD")
        surf_csg_shoe_tvd = c2.number_input("Surface Csg TVD")
        surf_csg_od = c2.number_input("Surface Csg OD")
        surf_csg_id = c2.number_input("Int. Csg ID")
        surf_csg_shoe_emw = c2.number_input("Surface Csg FIT/LOT EMW", step=0.1)

        c3.markdown("##### Freeze Protect Info") # ----------------------------
        c3.markdown("---")
        freeze_protect_md = c3.number_input("Freeze Protect MD")
        freeze_protect_tvd = c3.number_input("Freeze Protect TVD")
        freeze_protect_fluid_wt = c3.number_input("Freeze Protect Fluid Weight")

        c4.write(" ##### Input Parameters") # ---------------------------------

        # Dict to hold the input well data TODO: Fix Surf_OD and Int_ID cto Surf_ID and INt_OD
        well_data_dict = {"Well Name":              well_name,
                     "Mud Weight in OA":            mud_weight_oa,
                     "Surface Csg Shoe EMW":        surf_csg_shoe_emw,
                     "Surface Csg Shoe MD":         surf_csg_shoe_md,
                     "Surface Csg Shoe TVD":        surf_csg_shoe_tvd,
                     "Surface Csg OD":              surf_csg_od,
                     "Int Csg ID":                  surf_csg_id,
                     "Freeze Protect MD":           freeze_protect_md,
                     "Freeze Protect TVD":          freeze_protect_tvd,
                     "Freeze Protect Fluid Wt.":    freeze_protect_fluid_wt,
                     "Date Time":                   datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                          }

        c4.write(well_data_dict)

        #Input df
        # well_df = pd.DataFrame(data=well_data_dict, index=["Info"]) #.from_dict()

        # st.dataframe(well_df)
        # TODO: Need to build a qc for all input variables - do think its needed...

        # Calculated Outputs
        fit_lot_psi = (well_data_dict["Surface Csg Shoe TVD"] * well_data_dict["Surface Csg Shoe EMW"] * MW_GRADIENT)
        casing_cap = ((well_data_dict["Surface Csg OD"] * (well_data_dict["Surface Csg OD"]) -
                       (well_data_dict["Int Csg ID"] * well_data_dict["Int Csg ID"]))) / AREA_FACTOR
        annulus_vol = (well_data_dict["Surface Csg Shoe MD"]*casing_cap)
        freeze_protect_vol = (well_data_dict["Freeze Protect MD"] * casing_cap)

    # Surveys Tab ----------------------------------------------
    with t3:
        st.markdown("#### **Upload your Survey Data**")
        st.write("Please upload your most recent directional survey data")
        st.caption("""**Note:** When uploading the data the only columns that 
                    are needed are **MD', INC°, AZM°, TVD'**.  See example below.""")
        st.image('img/survey_example.png')
        st.markdown("---")

        # Create file uploader and check files type
        uploaded_file = st.file_uploader("Choose file type ('.xlsx' or '.csv')", type=['xlsx','csv'])

        if uploaded_file is not None:
            # print(uploaded_file.type)
            try:
                SURVEY_DATA = pd.read_excel(uploaded_file)
            except:
                try:
                    SURVEY_DATA = pd.read_csv(uploaded_file)
                except:
                    print("Error uploading Survey file")

            if SURVEY_DATA.columns is not None:
                st.success('Survey file successfully uploaded!', icon="✅")
                st.markdown("##### Survey data preview")
                st.dataframe(SURVEY_DATA)
                SURVEYS_UPLOADED = True

    # Analysis Tab ---------------------------------------------
    with t4:
        st.markdown("### **Analysis**")  # ------------------------------------
        st.write("Please enter you current wells data")
        # st.markdown("---")


    # Pump Schedules Tab ---------------------------------------

    # Finalize Tab ---------------------------------------------
