import pickle
import pandas as pd
from calculations.production import filter_data, get_plan_values, calc_actuals, calc_achievements, calc_stripping_ratio, calc_global_stripping_ratio, calc_coal_stock

with open('data/cache.pkl', 'rb') as f:
    data = pickle.load(f)

sheets = data['sheets']
input_values = data['input_values']

target_date = pd.Timestamp('2026-03-16')
date_range = (target_date, target_date)

JOS = ['North JO IC', 'North JO GAM', 'South JO IC', 'South JO GAM']

with open('validation.log', 'w', encoding='utf-8') as f:
    f.write('=============================================\n')
    f.write('        DATA VALIDATION: 2026-03-16          \n')
    f.write('=============================================\n')

    for jo in JOS:
        f.write(f'\n--- {jo} ---\n')
        filtered = filter_data(sheets, date_range, jo)
        
        ob_f = filtered['ob_f']
        f.write(f'OB Records: {len(ob_f)}\n')
        actual_ob_raw = ob_f['Volume'].sum() if not ob_f.empty else 0
        f.write(f'Raw Sum OB Volume: {actual_ob_raw:,.2f}\n')
        
        ch_f = filtered['ch_f']
        f.write(f'CH Records: {len(ch_f)}\n')
        if not ch_f.empty:
            if 'Volume' in ch_f.columns:
                actual_ch_raw = ch_f['Volume'].sum()
                f.write(f'Raw Sum CH Volume (MT): {actual_ch_raw:,.2f}\n')
            elif 'Netto' in ch_f.columns:
                actual_ch_raw = ch_f['Netto'].sum() / 1000
                f.write(f'Raw Sum CH Netto -> MT: {actual_ch_raw:,.2f}\n')
        
        # Dashboard Calculation Engine
        actuals = calc_actuals(filtered)
        plans = get_plan_values(sheets, jo)
        ach = calc_achievements(actuals, plans)
        sr = calc_stripping_ratio(actuals)
        
        f.write(f'[Function Outputs]\n')
        f.write(f'OB: Act {actuals["actual_ob"]:,.2f} | Plan {plans["plan_ob"]:,.2f} | Ach {ach["ach_ob"]:.2f}%\n')
        f.write(f'CH: Act {actuals["actual_ch"]:,.2f} | Plan {plans["plan_ch"]:,.2f} | Ach {ach["ach_ch"]:.2f}%\n')
        f.write(f'CT: Act {actuals["actual_ct"]:,.2f} | Plan {plans["plan_ct"]:,.2f} | Ach {ach["ach_ct"]:.2f}%\n')
        f.write(f'SR: {sr:,.2f}\n')
        
    f.write('\n=============================================\n')
    f.write('                 GLOBAL METRICS              \n')
    f.write('=============================================\n')

    global_sr = calc_global_stripping_ratio(sheets, date_range)
    stocks = calc_coal_stock(sheets, date_range, input_values)

    f.write(f'Global Daily SR: {global_sr:.2f}\n')
    f.write(f'Input Opening ROM: {input_values["opening_rom"]:,.2f}\n')
    f.write(f'Input Opening Port: {input_values["opening_port"]:,.2f}\n')
    f.write(f'Input Plan Barging: {input_values["plan_barging"]:,.2f}\n')
    f.write(f'Calc Stock ROM: {stocks["coal_stock_rom"]:,.2f}\n')
    f.write(f'Calc Stock PORT: {stocks["coal_stock_port"]:,.2f}\n')
