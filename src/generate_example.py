import pandas as pd
import random

def prepare_example():
    # sample data from here https://data.world/datafiniti/electronic-products-and-pricing-data
    local_path = "../sample-data/electronics.csv"
    products_df = pd.read_csv(local_path)
    products_df.drop(products_df.columns.difference(['prices.amountMax', 'prices.merchant', 'brand',
                                                     'categories', 'name', 'upc', 'weight']), 1, inplace=True)
    products_df['category'] = products_df['categories'].apply(lambda x: x.split(',')[0])
    products_df['sub-category'] = products_df['categories'].apply(lambda x: x.split(',')[1])

    products_df["price"] = products_df['prices.amountMax']
    products_df["merchant"] = products_df['prices.merchant']

    count = len(products_df)
    random_upcs = set()
    for i in range(count):
        upc = random.randint(1000000, 9999999)
        while upc in random_upcs:
            upc = random.randint(1000000, 9999999)
        random_upcs.add(upc)

    products_df['upc'] = list(random_upcs)
    products_df = products_df.drop(columns=['categories', 'prices.amountMax', 'prices.merchant'])
    products_df.to_csv('../sample-data/products_01.csv', index=False)