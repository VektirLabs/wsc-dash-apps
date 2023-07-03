import cpyai as cp
import pandas as pd

# AKDW -----------------------------------------------------
# def query_akdw(query):
#     """
#     Updated By: Tyler Hunt
#     Updated Date: 2/21/23
#     :param query: This is a SQL String that queries the AKDW server
#                   Note: must fully qualify the db.tablename
#     :return: pandas dataframe with the requested data from AKDW
#     """
#     df = pd.DataFrame()
#     try:
#         akdw = cp.AKDW()
#         return "Success, Here is your data!\n", akdw.query(f"{query}")
#     except:
#         return "Error, Please try again!\n", df

def get_wv_well_names():
    """
          Updated By: Tyler Hunt
          Updated Date: 3/15/23
          :param: None
          :return: SQL string
          """
    return """ 
    SELECT DISTINCT
        "Common Well Name" as WELL_NAME
    FROM GWDW_BI_GLOBAL.GW_WELLHEADER
    WHERE 
        "Business Unit" in ('ALASKA')	
        AND "Common Well Name" NOT like '0-Test%'
    ORDER BY "Common Well Name" ASC
    """

def get_akdw_wv_wh():
    """
       Updated By: Tyler Hunt
       Updated Date: 2/21/23
       :param: None
       :return: SQL string
       """
    return f"""
    SELECT 
        "Business Unit", 
        "Common Well Name", 
        "Wellbore API - UWI",
        "API - UWI"||'-'|| "API - UWI Sidetrack" as WB_ST_UWI, 
        Operator, 
        Country, 
        "State - Province", 
        Region,
        "Surface Latitude", 
        "Surface Longitude", 
         Program, 
        "Drill Site" as PAD, 
        "Well Type", 
        "Well Sub Type", 
        "Well Config Type", 
        "Well Status", 
        "KB-Ground Distance", 
        "Original Spud Date", 
        "On Production Date", 
        "First Sales Date", 
        "Abandonment Date", 
        "Operated Flag", 
        "Wellbore Start Date", 
        "Wellbore End Date", 
        "Wellbore Start Depth", 
        "Wellbore Total Depth", 
        "Wellbore Total Depth TVD", 
        "Well ID", "Wellbore ID", 
        "Wellbore Seq"
    FROM GWDW_BI_GLOBAL.GW_WELLHEADER
    WHERE 
        "Business Unit" in ('ALASKA')	
         AND "Common Well Name" NOT like '0-Test%'
    ORDER BY "Common Well Name" ASC
    """

def get_akdw_wv_wh_by_api(api):
    """
   Updated By: Tyler Hunt
   Updated Date: 2/21/23
   :param api: pass the single api # that you want
   :return: SQL string
   """
    return f"""
    SELECT 
        "Business Unit", 
        "Common Well Name", 
        "Wellbore API - UWI",
        "API - UWI"||'-'|| "API - UWI Sidetrack" as WB_ST_UWI, 
        Operator, 
        Country, 
        "State - Province", 
        Region,
        "Surface Latitude", 
        "Surface Longitude", 
         Program, 
        "Drill Site" as PAD, 
        "Well Type", 
        "Well Sub Type", 
        "Well Config Type", 
        "Well Status", 
        "KB-Ground Distance", 
        "Original Spud Date", 
        "On Production Date", 
        "First Sales Date", 
        "Abandonment Date", 
        "Operated Flag", 
        "Wellbore Start Date", 
        "Wellbore End Date", 
        "Wellbore Start Depth", 
        "Wellbore Total Depth", 
        "Wellbore Total Depth TVD", 
        "Well ID", "Wellbore ID", 
        "Wellbore Seq"
    FROM GWDW_BI_GLOBAL.GW_WELLHEADER
    WHERE 
        "Business Unit" in ('ALASKA')	
       	AND "Wellbore API - UWI" in ('{api}')
    """

def get_akdw_wv_wh_by_name(well_name):
    """
    Updated By: Tyler Hunt
    Updated Date: 2/21/23
    :param well_name: pass the single well name that you want
    :return: SQL string
    """
    return f"""
    SELECT 
        "Business Unit", 
        "Common Well Name", 
        "Wellbore API - UWI",
        "API - UWI"||'-'|| "API - UWI Sidetrack" as WB_ST_UWI, 
        Operator, 
        Country, 
        "State - Province", 
        Region,
        "Surface Latitude", 
        "Surface Longitude", 
         Program, 
        "Drill Site" as PAD, 
        "Well Type", 
        "Well Sub Type", 
        "Well Config Type", 
        "Well Status", 
        "KB-Ground Distance", 
        "Original Spud Date", 
        "On Production Date", 
        "First Sales Date", 
        "Abandonment Date", 
        "Operated Flag", 
        "Wellbore Start Date", 
        "Wellbore End Date", 
        "Wellbore Start Depth", 
        "Wellbore Total Depth", 
        "Wellbore Total Depth TVD", 
        "Well ID", "Wellbore ID", 
        "Wellbore Seq"
    FROM GWDW_BI_GLOBAL.GW_WELLHEADER
    WHERE 
        "Business Unit" in ('ALASKA')	
        AND "Common Well Name" in ('{well_name}')
    ORDER BY "Common Well Name" ASC
    """

def get_akdw_wv_phase_by_api(api):
    """
    Updated By: Tyler Hunt
    Updated Date: 2/21/23
    :param api: pass in a single API number to get the well
    :return: SQL string
    """
    return f"""
    Select 
        "API - UWI"||'-'|| "API - UWI Sidetrack" AS WB_ST_UWI, 
        "Well Name",
        "Wellbore Name",
        "Rig Contractor" || ' - ' || "Rig Name" as RIG,
        "Rig Type",
        "Network Number",
        "Region",
        "Program",
        "Like Kind Group" AS "DESIGN_TYPE",
        "Well Status"
        "Job Category",
        "Primary Job Type",
        "Secondary Job Type",
        "Planned Formation",
        "Job Start Date",
        "Job End Date",
        "Job Phase",
        "Job Op Code",
        "Job Phase Seq",
        "Phase Seq AFE Start Date",
        "Phase Seq AFE End Date",
        "Phase Seq AFE Start Depth",
        "Phase Seq AFE End Depth",
        "Phase Seq Actual Start Date",
        "Phase Seq Actual End Date",
        "Phase Seq Actual Start Depth",
        "Phase Seq Actual End Depth"
    FROM GWDW_BI_GLOBAL.GW_JOB_PHASE gjp 
    WHERE "Wellbore API - UWI" in ('{api}')
    ORDER BY "Job Phase Seq" ASC
    """


## Test Stub
# msg, df = query_akdw(get_wv_well_names())
# print(get_akdw_wv_wh())
# print(msg, df)
