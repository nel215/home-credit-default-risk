import pandas as pd
from category_encoders.target_encoder import TargetEncoder


def encode_train(train_df, test_df):
    cols = [
        'CODE_GENDER',
        'FLAG_OWN_CAR',
        'FLAG_OWN_REALTY',
        'NAME_TYPE_SUITE',
        'NAME_INCOME_TYPE',
        'NAME_EDUCATION_TYPE',  # Level of highest education the client achieved,  # noqa
        'NAME_FAMILY_STATUS',
        'NAME_HOUSING_TYPE',
        'FLAG_MOBIL',
        'FLAG_EMP_PHONE',
        'FLAG_WORK_PHONE',
        'FLAG_CONT_MOBILE',
        'FLAG_PHONE',
        'FLAG_EMAIL',
        'OCCUPATION_TYPE',
        'WEEKDAY_APPR_PROCESS_START',
        'HOUR_APPR_PROCESS_START',
        'REG_REGION_NOT_LIVE_REGION',
        'REG_REGION_NOT_WORK_REGION',
        'LIVE_REGION_NOT_WORK_REGION',
        'REG_CITY_NOT_LIVE_CITY',
        'REG_CITY_NOT_WORK_CITY',
        'LIVE_CITY_NOT_WORK_CITY',
        'ORGANIZATION_TYPE',
        'FONDKAPREMONT_MODE',
        'HOUSETYPE_MODE',
        'WALLSMATERIAL_MODE',
        'EMERGENCYSTATE_MODE',
        'NAME_CONTRACT_TYPE',  # Identification if loan is cash or revolving,
    ]
    encoder = TargetEncoder(cols=cols)
    encoder.fit(train_df[cols], train_df['TARGET'])
    encoded_train_df = encoder.transform(train_df[cols])
    encoded_test_df = encoder.transform(test_df[cols])
    encoded_train_df.columns = ['ENCODED_{}'.format(c) for c in cols]
    encoded_test_df.columns = ['ENCODED_{}'.format(c) for c in cols]
    pd.concat([train_df, encoded_train_df], axis=1).to_feather(
        './data/application_train.csv.encoded.feather')
    pd.concat([test_df, encoded_test_df], axis=1).to_feather(
        './data/application_test.csv.encoded.feather')


def encode_prev(train_df):
    prev_df = pd.read_feather(
        './data/previous_application.csv.feather')
    df = train_df.merge(prev_df, on='SK_ID_CURR')

    cols = [
        'NAME_CONTRACT_TYPE',
        'WEEKDAY_APPR_PROCESS_START',  # On which day of the week did the client apply for previous application, # noqa
        'HOUR_APPR_PROCESS_START',  # Approximately at what day hour did the client apply for the previous application,rounded # noqa
        'FLAG_LAST_APPL_PER_CONTRACT',  # Flag if it was last application for the previous contract. Sometimes by mistake of client or our clerk there could be more applications for one single contract, # noqa
        'NFLAG_LAST_APPL_IN_DAY',  # Flag if the application was the last application per day of the client. Sometimes clients apply for more applications a day. Rarely it could also be error in our system that one application is in the database twice, # noqa
        # 'NFLAG_MICRO_CASH',  # Flag Micro finance loan, # missing? # noqa
        'NAME_CASH_LOAN_PURPOSE',  # Purpose of the cash loan, # noqa
        'NAME_CONTRACT_STATUS',
        'NAME_PAYMENT_TYPE',  # Payment method that client chose to pay for the previous application, # noqa
        'CODE_REJECT_REASON',  # Why was the previous application rejected, # noqa
        'NAME_TYPE_SUITE',  # Who accompanied client when applying for the previous application, # noqa
        'NAME_CLIENT_TYPE',  # Was the client old or new client when applying for the previous application, # noqa
        'NAME_GOODS_CATEGORY',  # What kind of goods did the client apply for in the previous application, # noqa
        'NAME_PORTFOLIO',  # "Was the previous application for CASH, POS, CAR, <85>", # noqa
        'NAME_PRODUCT_TYPE',  # Was the previous application x-sell o walk-in, # noqa
        'CHANNEL_TYPE',  # Through which channel we acquired the client on the previous application, # noqa
        'SELLERPLACE_AREA',  # Selling area of seller place of the previous application, # encoded # noqa
        'NAME_SELLER_INDUSTRY',  # The industry of the seller, # noqa
        'NAME_YIELD_GROUP',  # Grouped interest rate into small medium and high of the previous application,grouped # noqa
        'PRODUCT_COMBINATION',  # Detailed product combination of the previous application, # noqa
        'NFLAG_INSURED_ON_APPROVAL',  # Did the client requested insurance during the previous application, # noqa
    ]
    encoder = TargetEncoder(cols=cols)
    encoder.fit(df[cols], df['TARGET'])
    res_df = encoder.transform(prev_df[cols])
    res_df.columns = ['ENCODED_{}'.format(c) for c in cols]
    pd.concat([prev_df, res_df], axis=1).to_feather(
        './data/previous_application.csv.encoded.feather')


def encode_inst(train_df):
    inst_df = pd.read_feather(
        './data/installments_payments.csv.feather')
    df = train_df.merge(inst_df, on='SK_ID_CURR')

    cols = [
        'NUM_INSTALMENT_VERSION',  # Version of installment calendar (0 is for credit card) of previous credit. Change of installment version from month to month signifies that some parameter of payment calendar has changed,  # noqa
    ]
    encoder = TargetEncoder(cols=cols)
    encoder.fit(df[cols], df['TARGET'])
    res_df = encoder.transform(inst_df[cols])
    res_df.columns = ['ENCODED_{}'.format(c) for c in cols]
    pd.concat([inst_df, res_df], axis=1).to_feather(
        './data/installments_payments.csv.encoded.feather')


def main():
    train_df = pd.read_feather('./data/application_train.csv.feather')
    test_df = pd.read_feather('./data/application_test.csv.feather')
    encode_train(train_df, test_df)

    train_df = train_df[['SK_ID_CURR', 'TARGET']]
    encode_prev(train_df)
    encode_inst(train_df)


if __name__ == '__main__':
    main()