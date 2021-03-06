import pandas as pd
from utility import reduce_memory
pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 220)


def aggregate_bb():
    bb = pd.read_feather('./data/bureau_balance.preprocessed.feather')

    # aggregate
    grp = bb.groupby('SK_ID_BUREAU')
    g = grp.agg({
        'DPD': ['mean'],
        'STATUS': ['nunique'],
    })
    g.columns = [a + "_" + b.upper() for a, b in g.columns]

    # edge
    edge = pd.read_feather('./data/bb.edge.feather')
    edge = edge.set_index('SK_ID_BUREAU')
    agg = g.join(edge, on='SK_ID_BUREAU')

    agg.columns = ["BB_" + c for c in agg.columns]

    reduce_memory(agg)

    return agg.reset_index()


def main():
    agg = aggregate_bb()
    agg.to_feather('./data/bb.agg.feather')


if __name__ == '__main__':
    main()
