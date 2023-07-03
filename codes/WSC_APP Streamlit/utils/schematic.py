import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class SchematicBuilder():
    def __init__(self, df):
        self.df = df
        self.LIGHT_GREY = 'rgba(50,50,50,0.2)'
        self.CASING_COLOR = 'rgba(0,0,0,1)'
        self.SHOE_COLOR = 'rgba(0,0,0,0.6)'
        self.LINER_COLOR = 'rgba(150 150 150,1)'
        self.OPEN_HOLE_COLOR = 'rgba(98,52,18,1)'
        self.PACKER_COLOR = 'rgba(50,50,50,0.2)'
        self.DRILL_PIPE_COLOR = 'rgba(50,50,50,0.7)'
        self.BHA_COLOR = 'rgba(50,50,50,0.2)'
        self.BIT_COLOR = 'rgba(50,50,50,0.2)'
        self.COMP_LIST = []

        self.SHOE_WIDTH = 3
        self.SHOE_HEIGHT = 10
        self.OH_HEIGHT = 1
        self.ANNOTATE_OFFSET = 40
        self.F_HEIGHT = 650
        self.F_WIDTH = 50
        self.F_LAYOUT = go.Layout(
            height=self.F_HEIGHT,
            margin=dict(l=20, r=20, b=20, t=50, pad=20),
        )

        # Clean dn prep the data'
        self.df["Comp_Desc"] = self.df["Type"] + " " + self.df["Name"]
        self.COMP_LIST = self.df["Comp_Desc"].unique().tolist()

        # Calculates the deltas
        self.df['Delta_shift'] = self.df["OD"].shift(-1)
        self.df['Deltas'] = self.df["OD"] - df["Delta_shift"]
        self.df['Deltas'] = self.df['Deltas'].apply(lambda x: x if x > 0 else 0)
        self.df = self.df.sort_values(by='Deltas', ascending=False)

        # Pass layout to the schematic
        self.SCHEMATIC = go.Figure(layout=self.F_LAYOUT)
        self.SCHEMATIC.update_xaxes(range=[self.F_WIDTH * -1, self.F_WIDTH + 75])
        self.SCHEMATIC.update_layout(
            autosize=False,
            height=self.F_HEIGHT,
            margin=dict(l=20, r=20, b=20, t=20, pad=20),
        )

        for idx, cmp in enumerate(self.COMP_LIST):

            if "Casing" in self.COMP_LIST[idx]:
                # CREATE AND EXPAND DF -------------------------------------------------------------------------------------
                cols = ["OD", "MD"]
                MD = np.arange(df[df["Comp_Desc"] == self.COMP_LIST[idx]]["Top Depth (Md)"][idx],
                               df[df["Comp_Desc"] == self.COMP_LIST[idx]]["Bottom Depth (Md)"][idx], 1) + 1
                OD = np.repeat(df[df["Comp_Desc"] == self.COMP_LIST[idx]]["OD"][idx], len(MD))
                t_df = pd.DataFrame(zip(OD, MD * -1), columns=cols)
                t_df["Comp_Desc"] = df["Comp_Desc"][idx]
                name = t_df[t_df["Comp_Desc"] == self.COMP_LIST[idx]]["Comp_Desc"][0].split(" ", 1)[1]

                # SHOE LOCATION COORDS
                SHOE_TOP_LEFT = t_df[t_df["Comp_Desc"] == self.COMP_LIST[idx]]["OD"].max()
                SHOE_TOP_RIGHT = t_df[t_df["Comp_Desc"] == self.COMP_LIST[idx]]["MD"].min()
                SHOE_BTM_LEFT = t_df[t_df["Comp_Desc"] == self.COMP_LIST[idx]]["OD"].max() + self.SHOE_WIDTH
                SHOE_BTM_RIGHT = t_df[t_df["Comp_Desc"] == self.COMP_LIST[idx]]["MD"].min() + self.SHOE_HEIGHT
                # st.write(SHOE_TOP_LEFT,SHOE_TOP_RIGHT,SHOE_BTM_LEFT,SHOE_BTM_RIGHT)

                # Add right side casing ------------------------------------------------------------------------------------
                self.SCHEMATIC.add_scatter(
                    x=t_df["OD"],  # OD
                    y=t_df["MD"],  # MD
                    line=dict(color=self.CASING_COLOR),
                    name=f"{name}",
                    textposition='top right',
                    textfont=dict(color='black'),
                    mode='lines+text',
                )

                # Add right side square shoe
                self.SCHEMATIC.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=SHOE_TOP_LEFT,
                    y0=SHOE_TOP_RIGHT,
                    x1=SHOE_BTM_LEFT,
                    y1=SHOE_BTM_RIGHT,
                    line=dict(color='black', width=2, ),
                    fillcolor=self.SHOE_COLOR,
                    opacity=1,
                )


                # Add left side casing -------------------------------------------------------------------------------------
                t_df = pd.DataFrame(zip(OD * -1, MD * -1), columns=cols)
                self.SCHEMATIC.add_scatter(
                    x=t_df["OD"],  # OD
                    y=t_df["MD"],  # MD
                    line=dict(color=self.CASING_COLOR),
                    name=f"{name}",
                    textposition='top left',
                    textfont=dict(color='#E58606'),
                    mode='lines+text',
                    showlegend=False

                )

                # Add left side square shoe
                self.SCHEMATIC.add_shape(
                    type="rect",
                    xref="x", yref="y",
                    x0=SHOE_TOP_LEFT * -1,
                    y0=SHOE_TOP_RIGHT,
                    x1=SHOE_BTM_LEFT * -1,
                    y1=SHOE_BTM_RIGHT,
                    line=dict(color='black', width=2, ),
                    fillcolor=self.SHOE_COLOR,
                )

    def __str__(self):
        return f"""

        """
