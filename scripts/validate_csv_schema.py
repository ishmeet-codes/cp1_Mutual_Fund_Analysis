import csv
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'data' / 'processed'

expected = {
    'cleaned_01_fund_master.csv': ['amfi_code','fund_house','scheme_name','category','sub_category','plan','launch_date','benchmark','expense_ratio_pct','exit_load_pct','min_sip_amount','min_lumpsum_amount','fund_manager','risk_category','sebi_category_code'],
    'cleaned_02_nav_history.csv': ['amfi_code','date','nav','is_forward_filled'],
    'cleaned_03_aum_by_fund_house.csv': ['date','fund_house','aum_lakh_crore','aum_crore','num_schemes'],
    'cleaned_04_monthly_sip_inflows.csv': ['month','sip_inflow_crore','active_sip_accounts_crore','new_sip_accounts_lakh','sip_aum_lakh_crore','yoy_growth_pct'],
    'cleaned_05_category_inflows.csv': ['month','category','net_inflow_crore'],
    'cleaned_06_industry_folio_count.csv': ['month','total_folios_crore','equity_folios_crore','debt_folios_crore','hybrid_folios_crore','others_folios_crore'],
    'cleaned_07_scheme_performance.csv': ['amfi_code','scheme_name','fund_house','category','plan','return_1yr_pct','return_3yr_pct','return_5yr_pct','benchmark_3yr_pct','alpha','beta','sharpe_ratio','sortino_ratio','std_dev_ann_pct','max_drawdown_pct','aum_crore','expense_ratio_pct','morningstar_rating','risk_grade'],
    'cleaned_08_investor_transactions.csv': ['investor_id','transaction_date','amfi_code','transaction_type','amount_inr','state','city','city_tier','age_group','gender','annual_income_lakh','payment_mode','kyc_status'],
    'cleaned_09_portfolio_holdings.csv': ['amfi_code','stock_symbol','stock_name','sector','weight_pct','market_value_cr','current_price_inr','portfolio_date'],
    'cleaned_10_benchmark_indices.csv': ['date','index_name','close_value']
}

results = {}
for fname, cols in expected.items():
    path = PROC / fname
    if not path.exists():
        results[fname] = {'found': False, 'error': 'file missing'}
        continue
    with path.open(newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            results[fname] = {'found': True, 'error': 'empty file'}
            continue
    missing = [c for c in cols if c not in header]
    extra = [h for h in header if h not in cols]
    results[fname] = {'found': True, 'missing_columns': missing, 'extra_columns': extra}

out = ROOT / 'data_schema_report.json'
out.write_text(json.dumps(results, indent=2))
print(f'Wrote report to: {out}')
