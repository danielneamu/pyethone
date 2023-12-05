#Importing packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')

#Read the dataset
df = pd.read_csv(r"/var/www/html/pyethone/scripts/df1.csv", low_memory=False)
df.head()

# in order to import and generate df from multiple csv source
# option 1
# file_paths = [r"df1.csv", r"df2.csv", r"df3.csv"]
# df = pd.concat([pd.read_csv(file_path) for file_path in file_paths])

# option 2
# import pandas as pd
# import glob
#
# file_paths = glob.glob("*.csv")
# df = pd.concat([pd.read_csv(file_path) for file_path in file_paths])

#a single index(Sex)
table = pd.pivot_table(
    df[df['CATEGORY'].isin(['7_FIXED_DATA', 'FIXED_DATA_HFC', 'FIXED_DATA_INTERNET', 'FIXED_DATA_INTERNET_FO', 'FIXED_DATA_VOC', 'FIXED_DATA_VPN', 'FIXED_VOICE', 'FIXED_VOICE_HFC', 'HSPA_VPN', 'IOT_OTC', 'IP_TRUNKING', 'LTE_INTERNET', 'LTE_VPN', 'M2M_ANALYTICS', 'M2M_CONNECTIVITY', 'M2M_FLOTA', 'M2M_IOT_SOLUTIONS', 'MANAGED_SERVICES', 'MANAGED_SERVICES_CONF', 'MANAGED_SERVICES_ICT', 'MANAGED_SERVICES_OTC', 'MANAGED_SERVICES_PARAM', 'OFFICE_ZONE', 'OFFICE365', 'TV_DIGITAL', 'TV_DVBC', 'VAS_FIXED_VOICE', 'VAS_IP_TRUNKING', 'VAS_M2M_CONNECTIVITY', 'VAS_M2M_FLEET_MANAGEMENT', 'VAS_M2M_FLOTA', 'VAS_REDUCERE_FIX_PP', 'VF_COMPLET'])],
    # data=df,
    index=['TEAM','AGENT_NAME'],
    columns=['ACT_MONTH'],
    values=['VALOARE_TOTALA'],
    fill_value=0,
    aggfunc="sum",
    dropna=True,
    margins=True
    )
print(table)