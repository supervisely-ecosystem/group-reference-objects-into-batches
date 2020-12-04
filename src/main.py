import os
import csv
import io
from collections import defaultdict
import pandas as pd
import supervisely_lib as sly

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])


@my_app.callback("group_reference_objects")
@sly.timeit
def group_reference_objects(api: sly.Api, task_id, context, state, app_logger):
    # with io.open(local_csv_path, "r", encoding='utf-8-sig') as f_obj:
    #     new_users = {}
    #     reader = csv.DictReader(f_obj, delimiter=DEFAULT_DELIMITER)
    brands = "../sample-data/brands_original.csv"
    products = "../sample-data/products_original.csv"

    brands_df = pd.read_csv(brands)
    print(brands_df[:10])

    products_df = pd.read_csv(products)
    print(products_df[:10])

    final_products = products_df.merge(brands_df, left_on='grp_id', right_on='grp_id')
    print(final_products[:10])

    final_products.to_csv('../sample-data/products.csv', index=False)



def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
    })

    # Run application service
    my_app.run(initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
