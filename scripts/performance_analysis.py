import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import os


RF = 0.065  # annual risk-free


def annualize_return(daily_mean):
    return daily_mean * 252


def annualize_vol(daily_std):
    return daily_std * np.sqrt(252)


def compute_returns(nav_df):
    nav_df = nav_df[nav_df["is_forward_filled"] == 0].copy()
    nav_df["date"] = pd.to_datetime(nav_df["date"])
    nav_df = nav_df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    nav_df["daily_return"] = nav_df.groupby("amfi_code")["nav"].pct_change()
    return nav_df


def cagr_for_period(series, last_date, years):
    target = last_date - pd.DateOffset(years=years)
    series = series.dropna()
    if series.empty:
        return np.nan
    prior = series.loc[series.index <= target]
    if prior.empty:
        return np.nan
    start_nav = prior.iloc[-1]
    end_nav = series.loc[series.index <= last_date].iloc[-1]
    n = years
    return (end_nav / start_nav) ** (1 / n) - 1


def max_drawdown(nav_series):
    running_max = nav_series.cummax()
    drawdown = nav_series / running_max - 1
    min_dd = drawdown.min()
    if np.isnan(min_dd):
        return min_dd, None, None
    end_idx = drawdown.idxmin()
    start_idx = nav_series.loc[:end_idx].idxmax()
    return float(min_dd), start_idx, end_idx


def main(workdir='.', out_dir='.'):
    workdir = os.path.abspath(workdir)
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    nav_path = os.path.join(workdir, 'data', 'processed', 'cleaned_02_nav_history.csv')
    master_path = os.path.join(workdir, 'data', 'processed', 'cleaned_01_fund_master.csv')
    bench_path = os.path.join(workdir, 'data', 'processed', 'cleaned_10_benchmark_indices.csv')

    nav = pd.read_csv(nav_path)
    master = pd.read_csv(master_path)
    bench = pd.read_csv(bench_path)

    nav = compute_returns(nav)
    nav["date"] = pd.to_datetime(nav["date"]) 

    returns = nav.pivot(index='date', columns='amfi_code', values='daily_return')

    results = []
    alpha_rows = []

    bench['date'] = pd.to_datetime(bench['date'])
    bench_pivot = bench.pivot(index='date', columns='index_name', values='close_value')
    bench_returns = bench_pivot.pct_change()

    all_amfi = master['amfi_code'].unique()

    for code in all_amfi:
        s_nav = nav.loc[nav['amfi_code'] == code, ['date', 'nav']].set_index('date')['nav'].sort_index()
        s_ret = returns[code].dropna() if code in returns.columns else pd.Series(dtype=float)
        last_date = s_nav.index.max() if not s_nav.empty else None

        cagr_1 = cagr_for_period(s_nav, last_date, 1) if last_date is not None else np.nan
        cagr_3 = cagr_for_period(s_nav, last_date, 3) if last_date is not None else np.nan
        cagr_5 = cagr_for_period(s_nav, last_date, 5) if last_date is not None else np.nan

        mean_daily = s_ret.mean()
        std_daily = s_ret.std()
        ann_ret = annualize_return(mean_daily) if not np.isnan(mean_daily) else np.nan
        ann_vol = annualize_vol(std_daily) if not np.isnan(std_daily) else np.nan
        sharpe = (ann_ret - RF) / ann_vol if ann_vol and not np.isnan(ann_vol) else np.nan

        negative_rets = s_ret[s_ret < 0]
        downside_std = negative_rets.std()
        sortino = (ann_ret - RF) / (downside_std * np.sqrt(252)) if downside_std and not np.isnan(downside_std) else np.nan

        mdd, mdd_start, mdd_end = max_drawdown(s_nav)

        bench_name = 'NIFTY 100 TRI'
        alpha = beta = r_value = p_value = stderr = np.nan
        if bench_name in bench_returns.columns and not s_ret.empty:
            merged = pd.concat([s_ret, bench_returns[bench_name]], axis=1).dropna()
            if not merged.empty:
                x = merged[bench_name].values
                y = merged[code].values
                res = stats.linregress(x, y)
                beta = float(res.slope)
                alpha = float(res.intercept) * 252
                r_value = float(res.rvalue)
                p_value = float(res.pvalue)
                stderr = float(res.stderr)

        results.append({
            'amfi_code': code,
            'cagr_1yr': cagr_1,
            'cagr_3yr': cagr_3,
            'cagr_5yr': cagr_5,
            'sharpe': sharpe,
            'sortino': sortino,
            'max_drawdown': mdd,
            'mdd_start': mdd_start,
            'mdd_end': mdd_end,
        })

        alpha_rows.append({
            'amfi_code': code,
            'alpha': alpha,
            'beta': beta,
            'r_value': r_value,
            'p_value': p_value,
            'stderr': stderr,
        })

    metrics = pd.DataFrame(results).set_index('amfi_code')
    alpha_df = pd.DataFrame(alpha_rows).set_index('amfi_code')

    df = master.set_index('amfi_code').join(metrics).join(alpha_df)

    df['rank_cagr_3yr'] = df['cagr_3yr'].rank(ascending=False, method='min')
    df['rank_sharpe'] = df['sharpe'].rank(ascending=False, method='min')
    df['rank_alpha'] = df['alpha'].rank(ascending=False, method='min')
    df['rank_expense_inv'] = (df['expense_ratio_pct'].rank(ascending=True, method='min') * -1)
    df['rank_mdd_inv'] = (df['max_drawdown'].rank(ascending=True, method='min') * -1)

    def percentile_rank(s):
        return s.rank(pct=True)

    w_cagr = 0.30
    w_sharpe = 0.25
    w_alpha = 0.20
    w_exp = 0.15
    w_mdd = 0.10

    p_cagr = percentile_rank(df['cagr_3yr'].fillna(-999))
    p_sharpe = percentile_rank(df['sharpe'].fillna(-999))
    p_alpha = percentile_rank(df['alpha'].fillna(-999))
    p_exp = 1 - percentile_rank(df['expense_ratio_pct'].fillna(df['expense_ratio_pct'].max()))
    p_mdd = 1 - percentile_rank(df['max_drawdown'].fillna(0))

    df['fund_score'] = (w_cagr * p_cagr + w_sharpe * p_sharpe + w_alpha * p_alpha + w_exp * p_exp + w_mdd * p_mdd) * 100
    df['fund_score_rank'] = df['fund_score'].rank(ascending=False, method='min')

    score_path = os.path.join(out_dir, 'fund_scorecard.csv')
    alpha_path = os.path.join(out_dir, 'alpha_beta.csv')
    df_out = df.reset_index()
    df_out.to_csv(score_path, index=False)
    alpha_df.reset_index().to_csv(alpha_path, index=False)

    top5 = df.sort_values('cagr_3yr', ascending=False).head(5).index.astype(int).tolist()
    chart_path = None
    if top5:
        start_date = nav['date'].max() - pd.DateOffset(years=3)
        fig, ax = plt.subplots(figsize=(10, 6))
        for code in top5:
            s_nav = nav.loc[(nav['amfi_code'] == code) & (nav['date'] >= start_date)].set_index('date')['nav'].sort_index()
            if s_nav.empty:
                continue
            norm = s_nav / s_nav.iloc[0] * 100
            ax.plot(norm.index, norm.values, label=f"{code}")

        for b in ['NIFTY 50 TRI', 'NIFTY 100 TRI']:
            if b in bench_pivot.columns:
                s = bench_pivot.loc[bench_pivot.index >= start_date, b]
                if not s.empty:
                    s_norm = s / s.iloc[0] * 100
                    ax.plot(s_norm.index, s_norm.values, label=b, linewidth=2, linestyle='--')

        ax.legend()
        ax.set_title('Top 5 funds vs Benchmarks (3yr)')
        ax.set_ylabel('Normalized value (start=100)')
        ax.grid(True)
        chart_path = os.path.join(out_dir, 'benchmark_comparison.png')
        fig.savefig(chart_path, bbox_inches='tight')

    print('Outputs written: ', score_path, alpha_path, chart_path)


if __name__ == '__main__':
    main(workdir='.', out_dir='.')
