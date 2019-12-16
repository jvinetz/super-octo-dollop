def pd_loop(df, txt):
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    if type(df) == list:
        print(txt)
        print('len : ', len(df))
        print(df)
    else:
        print(txt)
        print('len : ', len(df))
        print('unique row : ',len(df.drop_duplicates()))
        for i in df.columns:
            print(df[i].head(3))
            print('unique in this column : ', len(df[i].unique()))
    print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')

