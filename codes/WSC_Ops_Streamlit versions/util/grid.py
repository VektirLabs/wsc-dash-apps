import pandas as pd
from st_aggrid import AgGrid
from st_aggrid import GridOptionsBuilder as gb

def create_grid(gType, DF):
    # DF["UID"] = DF.index + 1

    PARAMS = []
    if gType == "T":
        PARAMS = ["Drill Pipe", "Bit", "Hwdp", "Drill Collars", "BHA", "Tubing"]
    elif gType == "A":
        PARAMS = ["Casing", "Liner", 'Open Hole']
    elif gType is None:
        PARAMS = ["Drill Pipe",  "Bit", "Hwdp", "Drill Collars", "BHA", "Casing", "Liner", "Tubing", "Open Hole"]

    GO = gb.from_dataframe(DF)
    GO.configure_column("Name", editable=True, width=250, )
    GO.configure_column("Type", editable=True, cellEditor='agSelectCellEditor',
                        cellEditorParams={'values': PARAMS}, width=110, )
    GO.configure_column("OD", editable=True, width=85, )
    GO.configure_column("ID", editable=True, width=85, )
    GO.configure_column("Top Depth (Md)", editable=True, width=145, )
    GO.configure_column("Bottom Depth (Md)", editable=True, width=145, )

    go = GO.build()

    return AgGrid(data=DF,
            gridOptions=go,
            update_mode='VALUE_CHANGED',
            fit_columns_on_grid_load=True,
            data_return_mode='FILTERED',
            theme='streamlit',
            editable=True,
        )

def create_geo_grid(DF):
    GO = gb.from_dataframe(DF)
    GO.configure_column("Formation Name", editable=True, width=250, )
    GO.configure_column("Top Depth (Md)", editable=True, width=145, )
    GO.configure_column("Bottom Depth (Md)", editable=True, width=145, )
    GO.configure_column("Top Depth (Tvd)", editable=True, width=145, )
    GO.configure_column("Bottom Depth (Tvd)", editable=True, width=145, )
    go = GO.build()
    return AgGrid(data=DF,
            gridOptions=go,
            update_mode='VALUE_CHANGED',
            fit_columns_on_grid_load=True,
            data_return_mode='FILTERED',
            theme='streamlit',
            editable=True,
        )
