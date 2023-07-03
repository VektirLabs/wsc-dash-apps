import pandas as pd
import numpy as np

class well():
    def __init__(self, name, wellbores, tubulars):
        self.name = name
        self.wellbores = wellbores
        self.tubulars = tubulars

    def to_string(self):
        wb = []
        tb = []
        for w in self.wellbores:
            wb.append(self.w["name"])
        for t in self.tubulars:
            tb.append(self.name)
        return self.name, wb, tb

class wellbore:
    AREA_CONST = 1029.4
    def __init__(self, name, typ, top_md, btm_md, t_od):
        self.name = name
        self.typ = typ
        self.top_md = top_md
        self.btm_md = btm_md
        self.t_od = t_od

    def capacity(self):
        try:
            return ((self.t_od * self.t_od) / self.AREA_CONST)
        except ZeroDivisionError:
            return 0

    def details(self):
        STEP_SIZE = 1  # 1' increments
        Y_line = np.arange(self.top_md, self.btm_md, STEP_SIZE)

        df = pd.DataFrame()
        df[f"{self.name[0:4]}_{self.typ}_LX"] = np.full(len(Y_line), self.t_od*-1)
        df[f"{self.name[0:4]}_{self.typ}_RX"] = np.full(len(Y_line), self.t_od)
        df[f"{self.name[0:4]}_{self.typ}_Y"] = Y_line+1

        return df

    def section_length(self):
        return self.btm_md - self.top_md

    def to_string(self):
        return f"""Name: {self.name}, Type: {self.typ}, Top MD: {self.top_md}, Bottom MD: {self.btm_md}, Hole Size: {self.t_od}, Section Length: {self.section_length()}, Capacity: {self.capacity()}"""

class tubular:
    AREA_CONST = 1029.4
    def __init__(self, name, typ, top_md, btm_md, t_od, t_id):
        self.name = name
        self.typ = typ
        self.top_md = top_md
        self.btm_md = btm_md
        self.t_od = t_od
        self.t_id = t_id

    def capacity(self):
        try:
            return ((self.t_id * self.t_id) / self.AREA_CONST)
        except ZeroDivisionError:
            return 0

    def section_length(self):
        return self.btm_md-self.top_md

    def details(self):
        STEP_SIZE = 1  # 1' increments
        Y_line = np.arange(self.top_md, self.btm_md, STEP_SIZE)

        df = pd.DataFrame()
        df[f"{self.name[0:4]}_{self.typ}_LX"] = np.full(len(Y_line), self.t_od * -1)
        df[f"{self.name[0:4]}_{self.typ}_RX"] = np.full(len(Y_line), self.t_od)
        df[f"{self.name[0:4]}_{self.typ}_Y"] = Y_line + 1

        return df

    def to_string(self):
        return f"""Name: {self.name}, Type: {self.typ}, Top MD: {self.top_md}, Bottom MD: {self.btm_md}, OD: {self.t_od}, ID: {self.t_id}, Section Length: {self.section_length()}, Capacity: {self.capacity()}"""

conductor_wb = wellbore("Conductor", "Wellbore", 0, 120, 36)
conductor_csg = tubular("Conductor", "Casing", 0, 120, 30, 29.5)

surface_wb = wellbore("Surface", "Wellbore", 120, 3750, 18.625)
surface_csg = tubular("Surface", "Casing", 120, 3740, 13.875, 12.415)

print(conductor_wb.to_string())
print(conductor_csg.to_string())

print(surface_wb.to_string())
print(surface_csg.to_string())

df_wb = conductor_wb.details()
df_tb = conductor_csg.details()

df_wb1 = surface_wb.details()
df_tb1 = surface_csg.details()

print(df_wb.head())
print(df_tb.tail())

print(df_wb1.head())
print(df_tb1.tail())



# well1 = well("CD4-597", [df_wb,df_wb1], [df_tb,df_tb1])
# name, wb, tb = well1.to_string()
# print(name, wb, tb)