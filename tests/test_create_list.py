import pandas as pd


def cu(market_book_list,df):
    for mk in market_book_list:
        mk_list = mk['list']
        list_lenght = len(mk_list)
        if list_lenght > 0:
            for runner in mk_list[0]['runners']:
                df_it = df[df['market_id']==mk_list[0]['marketId']]
                for back in runner['ex']['availableToBack']:
                    df_it2 = df_it
                    print(f'aqui é teste:\n {df_it}')
                    print(runner['selectionId'])
                    df_it2['selection_id']=runner['selectionId']
                    df_it2['odd'] = back['price']
                    df_it2['odd_size'] = back['size']
                    df_it2['odd_type'] = 'back'
                    print("solo una:\n\n back \n {}\n\n".format(df_it2))
                    df = pd.concat([df_it2, df], axis=0)
                for lay in runner['ex']['availableToLay']:
                    df_it2 = df_it
                    df_it2['selection_id']=runner['selectionId']
                    df_it2['odd'] = lay['price']
                    df_it2['odd_size'] = lay['size']
                    print("solo una:\n\n lay \n{}\n\n".format(df_it2))
                    df['odd_type'] = 'lay'
                    df = pd.concat([df_it2, df], axis=0)
        df = df[df['selection_id'] != 'TF']
        print("I'm here")
        return df
