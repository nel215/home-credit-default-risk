import pandas as pd
from utility import reduce_memory


def _aggregate():
    df = pd.read_feather('./data/pos.preprocessed.feather')
    grp = df.groupby('SK_ID_CURR')
    fs = ['sum', 'median', 'mean', 'std', 'max', 'min']
    agg = {
        # original
        'CNT_INSTALMENT': fs,
        'CNT_INSTALMENT_FUTURE': fs,
        'SK_DPD': fs,
        'SK_DPD_DEF': fs,
        # preprocessed
        'RATIO_CNT_INST': ['max', 'min'],
    }
    g = grp.agg(agg)
    g.columns = ['{}_{}'.format(a, b.upper()) for a, b in g.columns]
    g['COUNT'] = grp.size()

    g.columns = ['POS_{}'.format(c) for c in g.columns]

    return g.reset_index()


def main():
    agg = _aggregate()
    reduce_memory(agg)
    agg.to_feather('./data/pos.agg.feather')


if __name__ == '__main__':
    main()
