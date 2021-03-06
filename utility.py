import gc
import random
import chainer
import numpy as np
import pandas as pd
import lightgbm as lgb


def factorize(df):
    columns = df.select_dtypes([np.object]).columns.tolist()
    for c in columns:
        df[c], _ = pd.factorize(df[c])
        nan = df[c].max() + 1
        df[c] = df[c].replace(-1, nan)
        df[c] = df[c].astype('category')


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def split_train(df):
    pos_df = df[df['TARGET'] == 1].sample(frac=1)
    neg_df = df[df['TARGET'] == 0].sample(frac=1)
    n_pos = pos_df.shape[0]
    n_neg = neg_df.shape[0]
    n_pos_train = int(0.85*n_pos)
    n_neg_train = int(0.85*n_neg)
    train_df = pd.concat([pos_df[:n_pos_train], neg_df[:n_neg_train]])
    train_df = train_df.sample(frac=1).reset_index(drop=True)
    test_df = pd.concat([pos_df[n_pos_train:], neg_df[n_neg_train:]])
    test_df = test_df.sample(frac=1).reset_index(drop=True)
    return train_df, test_df


def one_hot_encoder(df):
    original_columns = list(df.columns)
    categorical_columns = [
        col for col in df.columns if df[col].dtype == 'object']
    df = pd.get_dummies(
        df, columns=categorical_columns, dummy_na=True)
    new_columns = [c for c in df.columns if c not in original_columns]
    return df, new_columns


def reduce_memory(df):
    for c in df.columns:
        if df[c].dtype == 'float64':
            df[c] = df[c].astype('float32')
        if df[c].dtype == 'int64':
            df[c] = df[c].astype('int32')


def filter_by_corr(df):
    train = pd.read_feather('./data/application_train.feather')
    train = train[['SK_ID_CURR', 'TARGET']]
    train = train.merge(df, on='SK_ID_CURR')
    train = train.drop(['SK_ID_CURR'], 1)
    corr = train.corr()[['TARGET']]
    corr['TARGET'] = corr['TARGET'].apply(abs)
    corr = corr.sort_values('TARGET', ascending=False)
    print(corr)

    cols = corr[corr['TARGET'] > 0.01].index.values.tolist()
    cols.remove('TARGET')
    if 'SK_ID_CURR' not in cols:
        cols.append('SK_ID_CURR')
    return df[cols]


def save_importance(bst, fname):
    split = bst.feature_importance('split', iteration=bst.best_iteration)
    gain = bst.feature_importance('gain', iteration=bst.best_iteration)
    feature_name = bst.feature_name()

    df = pd.DataFrame(
        list(zip(feature_name, split, gain)),
        columns=['feature', 'split', 'gain'],
    )
    df = df.sort_values('split', ascending=False)

    print('save {}...'.format(fname))
    df.to_csv(fname, index=False)


def reset_seed(seed=0):
    random.seed(seed)
    np.random.seed(seed)
    if chainer.cuda.available:
        chainer.cuda.cupy.random.seed(seed)


def filter_by_lgb(df, thres=3.00):
    print(df.shape)
    orig = df.copy()
    if 'TARGET' in df.columns:
        df = df.drop(['TARGET'], axis=1)

    factorize(df)

    train = pd.read_feather('./data/application_train.feather')
    train = train[['SK_ID_CURR', 'TARGET']]
    gc.collect()

    df = df.merge(train, on='SK_ID_CURR')
    del df['SK_ID_CURR']
    y = df.pop('TARGET')

    xgtrain = lgb.Dataset(
        df.values, label=y.values,
        feature_name=df.columns.values.tolist(),
        categorical_feature=[],
    )

    lgb_params = {
        'boosting_type': 'gbdt',
        'objective': 'binary',
        'metric': 'auc',
        'learning_rate': 0.2,
        'num_leaves': 30,
        'max_depth': -1,  # -1 means no limit
        'subsample': 1.0,
        'colsample_bytree': 1.0,
        # 'min_child_weight': 40,
        # 'min_child_samples': 70,
        # 'min_split_gain': 0.5,
        'reg_alpha': 10,
        'reg_lambda': 0,
        'nthread': 12,
        'verbose': 0,
    }
    bst = lgb.train(
        lgb_params,
        xgtrain,
        valid_sets=[xgtrain],
        valid_names=['train'],
        num_boost_round=1000,
        verbose_eval=100,
        categorical_feature=[],
    )

    importance = bst.feature_importance('gain', iteration=bst.best_iteration)
    mean = np.mean(importance)
    feature_name = bst.feature_name()

    importances = list(sorted(zip(feature_name, importance), key=lambda x: -x[1]))

    selected = []
    for f, s in importances:
        if f not in orig.columns:
            continue
        if s < 0.1*mean:
            continue
        selected.append(f)
        print(f, s)

    print(len(selected))
    return orig[['SK_ID_CURR']+selected]
