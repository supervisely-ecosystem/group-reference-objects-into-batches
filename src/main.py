import os
import json
import pandas as pd
import supervisely_lib as sly

from generate_example import prepare_example


my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])


@my_app.callback("preview_catalog")
@sly.timeit
def preview_catalog(api: sly.Api, task_id, context, state, app_logger):
    catalog_path: str = state["catalogPath"]

    local_path = os.path.join(my_app.data_dir, catalog_path.lstrip("/"))
    fields = None
    try:
        api.file.download(TEAM_ID, catalog_path, local_path)
        catalog_df = pd.read_csv(local_path)
        catalog_df.insert(0, '#', list(range(len(catalog_df))))
        fields = [
            {"field": "data.catalog", "payload": json.loads(catalog_df.to_json(orient="split"))},
            {"field": "data.catalogError", "payload": ""},
        ]
    except Exception as e:
        fields = [
            {"field": "data.catalog", "payload": {"columns": [], "data": []}},
            {"field": "data.catalogError", "payload": repr(e)},
        ]
    api.app.set_fields(task_id, fields)


@my_app.callback("group_reference_objects")
@sly.timeit
def group_reference_objects(api: sly.Api, task_id, context, state, app_logger):
    pass


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
    })

    #prepare_example()

    data = {
        "catalog": {"columns": [], "data": []},
        "catalogError": ""
    }
    state = {
        # @TODO: for debug
        "catalogPath": "/sample-data/products_01.csv",
        #table view settings
        "perPage": 15,
        "pageSizes": [10, 15, 30, 50, 100],
    }
    # Run application service
    my_app.run(data=data, state=state, initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
