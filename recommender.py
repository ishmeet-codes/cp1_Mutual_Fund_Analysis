import pandas as pd
import sys

SCHEME_FILE = 'data/raw/07_scheme_performance.csv'

RISK_MAP = {
    'Low': ['Low'],
    'Moderate': ['Moderate','Moderately High'],
    'High': ['High','Very High']
}


def recommend(risk_appetite='Moderate', top_n=3):
    df = pd.read_csv(SCHEME_FILE)
    risk_appetite = risk_appetite.capitalize()
    allowed = RISK_MAP.get(risk_appetite, ['Moderate'])
    cand = df[df['risk_grade'].isin(allowed)].copy()
    cand = cand.sort_values('sharpe_ratio', ascending=False)
    out = cand[['amfi_code','scheme_name','fund_house','category','sharpe_ratio','risk_grade']].head(top_n)
    return out


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv)>1 else 'Moderate'
    topn = int(sys.argv[2]) if len(sys.argv)>2 else 3
    rec = recommend(arg, topn)
    print(rec.to_string(index=False))
