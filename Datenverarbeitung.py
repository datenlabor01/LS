# Länderübersicht-Dashboard

import wbgapi as wb
import pandas as pd
import numpy as np
pd.options.mode.chained_assignment = None

indicators_la = ["SP.POP.GROW", "SI.POV.DDAY", "NY.GNP.PCAP.CD",
              "DT.ODA.ODAT.XP.ZS", "NY.GDP.MKTP.CD", "NY.GDP.MKTP.KD.ZG",
              "NY.GDP.DEFL.KD.ZG", "SL.EMP.TOTL.SP.ZS", "SL.EMP.1524.SP.ZS",
              "GC.REV.XGRT.GD.ZS", "DT.DOD.DECT.GN.ZS", "BX.KLT.DINV.WD.GD.ZS",
              "BX.TRF.PWKR.CD.DT", "EG.ELC.RNWX.ZS", "EN.ATM.CO2E.PC",
              "AG.LND.FRST.ZS", "SI.POV.GINI", "SI.POV.NAHC", "DT.ODA.ODAT.CD",
              "DT.ODA.ODAT.PC.ZS"] 

#Get data with latest 5 year:
dat_wb = wb.data.DataFrame(indicators_la, economy = wb.region.members("EAP", "ECA"), labels = True, mrv=5)
dat_wb = dat_wb.reset_index()
dat_wb = dat_wb[["economy", "Series", "YR2017", "YR2018", "YR2019", "YR2020", "YR2021"]]
dat_wb.columns = dat_wb.columns.str.replace("YR", '')
dat_wb = dat_wb.rename(columns={dat_wb.columns[0]: "index"})

#Corruption index downloaded from https://www.transparency.org/en/cpi/2021
df_cor = pd.read_excel("https://github.com/datenlabor01/LS/blob/main/CPI2021_GlobalResults&Trends.xlsx?raw=true", sheet_name=1, header=2)
df_cor = df_cor[["ISO3","CPI score 2021", "CPI score 2020", "CPI score 2019", "CPI score 2018", "CPI score 2017"]]
df_cor["Series"] = "Corruption_Perception_Index"
df_cor = df_cor.rename(columns={df_cor.columns[0]: "index"})
df_cor.columns = df_cor.columns.str.replace("CPI score ", '')

#Governance Index downloaded from bti-project.org
df_bti_1 = pd.read_excel("https://github.com/datenlabor01/LS/blob/main/BTI_2006-2022_Scores.xlsx?raw=true", sheet_name=0)
df_bti_2 = pd.read_excel("https://github.com/datenlabor01/LS/blob/main/BTI_2006-2022_Scores.xlsx?raw=true", sheet_name=1)
df_bti_3 = pd.read_excel("https://github.com/datenlabor01/LS/blob/main/BTI_2006-2022_Scores.xlsx?raw=true", sheet_name=2)

df_bti = pd.DataFrame()
df_bti["Country"] = df_bti_1.iloc[:,0]
df_bti["2022"] = df_bti_1.iloc[:,53]
df_bti["2020"] = df_bti_2.iloc[:,53]
df_bti["2018"] = df_bti_3.iloc[:,53]
df_bti["Series"] = "Governance_Index"

df_env = pd.DataFrame()
df_env["Country"] = df_bti_1.iloc[:,0]
df_env["2022"] = df_bti_1.iloc[:,50]
df_env["2020"] = df_bti_2.iloc[:,50]
df_env["2018"] = df_bti_3.iloc[:,50]
df_env["Series"] = "Environment_Policy_Index"

#Revenue, excluding grants (% of GDP): GGRXG_GDP
#Net debt: GGXWDN_G01_GDP_PT

import requests
response = requests.get("https://www.imf.org/external/datamapper/api/v1/GGXWDN_G01_GDP_PT")
temp = pd.DataFrame.from_records(response.json())
temp = temp.loc["GGXWDN_G01_GDP_PT", "values"]
debt_data = pd.DataFrame.from_records(temp)
debt_data = debt_data.transpose().reset_index()
debt_data = debt_data[["index", "2017", "2018", "2019", "2020", "2021"]]
debt_data["Series"] = "Net debt (% of GPD)"

response = requests.get("https://www.imf.org/external/datamapper/api/v1/GGRXG_GDP")
temp = pd.DataFrame.from_records(response.json())
temp = temp.loc["GGRXG_GDP", "values"]
revenue_data = pd.DataFrame.from_records(temp)
revenue_data = revenue_data.transpose().reset_index()
revenue_data = revenue_data[["index", "2017", "2018", "2019", "2020", "2021"]]
revenue_data["Series"] = "Revenue excluding grants (% of GDP)"

#Read-in data for HDI downloaded from https://hdr.undp.org/data-center/documentation-and-downloads
hdi = pd.read_csv("https://github.com/datenlabor01/LS/raw/main/HDR21-22_Composite_indices_complete_time_series.csv")
#For HDI-score:
hdi_score = hdi[["iso3", "hdi_2017", "hdi_2018", "hdi_2019", "hdi_2020", "hdi_2021"]]
hdi_score["Series"] = "HDI_Score" 
hdi_score = hdi_score.rename(columns={hdi_score.columns[0]: "index"})
hdi_score.columns = hdi_score.columns.str.replace("hdi_", '')

df = pd.read_excel("https://github.com/datenlabor01/ODA-Ranking/blob/main/gross_oda.xlsx?raw=true", header = 11)
df = prepare_dataframe(df, "gross")
oda_ger = df[["Recipient", "Year", "Germany"]]
oda_ger["Germany"] = oda_ger["Germany"]*1000000
oda_ger = pd.pivot_table(oda_ger, values = "Germany", columns = "Year", index = "Recipient").reset_index()
oda_ger["Series"] = "Gross_ODA_Germany (in US$)"
oda_ger = oda_ger.rename(columns={oda_ger.columns[0]: "Country"})
oda_ger.Country = oda_ger.Country.str.strip()

#Add country codes based on OECD ISO codes
dfkeys = pd.read_excel("https://github.com/datenlabor01/ODA-Ranking/blob/main/Country%20Mapping.xlsx?raw=true")
dic = dfkeys.set_index('ISOcode').to_dict()['Recipient name (EN)']

df_la_dash = pd.concat([dat_wb, debt_data, revenue_data, hdi_score, df_cor])
df_la_dash["Country"] = df_la_dash['index'].map(dic)

dic = dfkeys.set_index('Recipient name (EN)').to_dict()['ISOcode']
oda_ger["index"] = oda_ger['Country'].map(dic)
df_bti["index"] = df_bti['Country'].map(dic)
df_env["index"] = df_env['Country'].map(dic)
df_la_dash = pd.concat([df_la_dash, oda_ger, df_bti, df_env])

df_la_dash = df_la_dash[df_la_dash.Country.notnull()]
df_la_dash = df_la_dash[df_la_dash['index'].notna()]
df_la_dash = pd.melt(df_la_dash, id_vars=['index', "Series", "Country"], value_vars=["2017", "2018","2019","2020","2021","2022"], var_name='Year')
df_la_dash["value"] = df_la_dash["value"].replace("-", np.nan)
df_la_dash = df_la_dash[df_la_dash.value.notnull()]
df_la_dash.to_csv("landubersicht_data.csv")
