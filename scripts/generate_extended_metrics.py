import os
import pandas as pd
import numpy as np
from scipy import stats


def main(workdir='.'):
    workdir = os.path.abspath(workdir)
    nav_fp = os.path.join(workdir, 'data', 'processed', 'cleaned_02_nav_history.csv')
    bench_fp = os.path.join(workdir, 'data', 'processed', 'cleaned_10_benchmark_indices.csv')
    score_fp = os.path.join(workdir, 'fund_scorecard.csv')

    nav = pd.read_csv(nav_fp, parse_dates=['date'])
    bench = pd.read_csv(bench_fp, parse_dates=['date'])
    score = pd.read_csv(score_fp)

    nav = nav[nav['is_forward_filled'] == 0].sort_values(['amfi_code', 'date'])
    nav['daily_return'] = nav.groupby('amfi_code')['nav'].pct_change()
    returns = nav.pivot(index='date', columns='amfi_code', values='daily_return')

    bench_pivot = bench.pivot(index='date', columns='index_name', values='close_value')
    bench_returns = bench_pivot.pct_change()

    # available benchmark names
    print('Benchmarks available:', list(bench_pivot.columns))

    benches = []
    for b in ['NIFTY100', 'NIFTY50']:
        if b in bench_returns.columns:
            benches.append(b)

    alpha_rows = []
    for code in score['amfi_code'].unique():
        try:
            code_int = int(code)
        except:
            code_int = code
        fr = returns[code_int].dropna() if code_int in returns.columns else pd.Series(dtype=float)
        for b in benches:
            if fr.empty:
                alpha_rows.append({'amfi_code': code_int, 'benchmark': b, 'alpha': np.nan, 'beta': np.nan})
                continue
            merged = pd.concat([fr, bench_returns[b]], axis=1).dropna()
            if merged.empty:
                alpha_rows.append({'amfi_code': code_int, 'benchmark': b, 'alpha': np.nan, 'beta': np.nan})
                continue
            res = stats.linregress(merged.iloc[:,1].values, merged.iloc[:,0].values)
            alpha_a = res.intercept * 252
            beta_a = res.slope
            alpha_rows.append({'amfi_code': code_int, 'benchmark': b, 'alpha': alpha_a, 'beta': beta_a})

    alpha_df = pd.DataFrame(alpha_rows)
    out_alpha = os.path.join(workdir, 'alpha_beta_extended_fixed.csv')
    alpha_df.to_csv(out_alpha, index=False)
    print('Wrote', out_alpha)

    # tracking error for top5 by cagr_3yr
    top5 = score.sort_values('cagr_3yr', ascending=False).head(5)['amfi_code'].astype(int).tolist()
    te_rows = []
    for code in top5:
        if code not in returns.columns:
            continue
        fr = returns[code].dropna()
        for b in benches:
            merged = pd.concat([fr, bench_returns[b]], axis=1).dropna()
            if merged.empty:
                continue
            diff = merged.iloc[:,0] - merged.iloc[:,1]
            te = diff.std() * np.sqrt(252)
            te_rows.append({'amfi_code': code, 'benchmark': b, 'tracking_error': te})

    te_df = pd.DataFrame(te_rows)
    out_te = os.path.join(workdir, 'tracking_error_top5_fixed.csv')
    te_df.to_csv(out_te, index=False)
    print('Wrote', out_te)


if __name__ == '__main__':
    main('.')
