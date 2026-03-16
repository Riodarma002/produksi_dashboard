import pickle
import pandas as pd
from datetime import date
from calculations.production import filter_data, get_plan_values, calc_actuals, calc_achievements, calc_stripping_ratio, calc_global_stripping_ratio, calc_coal_stock

# Load Data
with open('data/cache.pkl', 'rb') as f:
    data = pickle.load(f)

sheets = data['sheets']
input_values = data['input_values']

# Target Date: March 16, 2026
target_date = pd.Timestamp('2026-03-16')
date_range = (target_date, target_date)

JOS = ['North JO IC', 'North JO GAM', 'South JO IC', 'South JO GAM']

print('\n=============================================')
print('        DATA VALIDATION: 2026-03-16          ')
print('=============================================')

for jo in JOS:
    print(f'\n--- {jo} ---')
    # Filter Data
    filtered = filter_data(sheets, date_range, jo)
    
    # 1. OB Data Check
    ob_f = filtered['ob_f']
    actual_ob_raw = ob_f['Volume'].sum() if not ob_f.empty else 0
    print(f'Raw Sum OB Volume: {actual_ob_raw:,.2f}')
    
    # 2. CH Data Check
    ch_f = filtered['ch_f']
    if not ch_f.empty:
        if 'Volume' in ch_f.columns:
            actual_ch_raw = ch_f['Volume'].sum()
            print(f'Raw Sum CH Volume (MT): {actual_ch_raw:,.2f}')
        elif 'Netto' in ch_f.columns:
            actual_ch_raw = ch_f['Netto'].sum() / 1000
            print(f'Raw Sum CH Netto -> MT: {actual_ch_raw:,.2f}')
        else:
            actual_ch_raw = 0
            print('CH: No Volume or Netto col found.')
    else:
        actual_ch_raw = 0
        print('CH: Empty.')
    
    # 3. CT Data Check
    ct_f = filtered['ct_f']
    
    # API Checks
    actuals = calc_actuals(filtered)
    plans = get_plan_values(sheets, jo)
    ach = calc_achievements(actuals, plans)
    sr = calc_stripping_ratio(actuals)
    
    print(f'[Function Outputs]')
    print(f'OB: Act {actuals["actual_ob"]:,.2f} | Plan {plans["plan_ob"]:,.2f} | Ach {ach["ach_ob"]:.2f}%')
    print(f'CH: Act {actuals["actual_ch"]:,.2f} | Plan {plans["plan_ch"]:,.2f} | Ach {ach["ach_ch"]:.2f}%')
    print(f'CT: Act {actuals["actual_ct"]:,.2f} | Plan {plans["plan_ct"]:,.2f} | Ach {ach["ach_ct"]:.2f}%')
    print(f'SR: {sr:,.2f}')
    
print('\n=============================================')
print('                 GLOBAL METRICS              ')
print('=============================================')

global_sr = calc_global_stripping_ratio(sheets, date_range)
stocks = calc_coal_stock(sheets, date_range, input_values)

print(f'Global Daily SR: {global_sr:.2f}')
print(f'Input Opening ROM: {input_values["opening_rom"]:,.2f}')
print(f'Input Opening Port: {input_values["opening_port"]:,.2f}')
print(f'Input Plan Barging: {input_values["plan_barging"]:,.2f}')
print(f'Calc Stock ROM: {stocks["coal_stock_rom"]:,.2f}')
print(f'Calc Stock PORT: {stocks["coal_stock_port"]:,.2f}')
