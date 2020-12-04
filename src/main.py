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


@my_app.callback("preview_reference_files")
@sly.timeit
def preview_reference_files(api: sly.Api, task_id, context, state, app_logger):
    fields = None
    try:
        dir_path = state["referenceDir"]
        if dir_path == "":
            raise ValueError("Directory path is not defined")
        files = api.file.list(TEAM_ID, dir_path)
        paths = [file_info["path"] for file_info in files]
        if len(paths) == 0:
            raise FileNotFoundError("Directory not found or empty")

        fields = [
            {"field": "data.referencePaths", "payload": paths},
            {"field": "data.referenceError", "payload": ""},
            {"field": "data.referenceSelected", "payload": [False] * len(paths)}
        ]
    except Exception as e:
        fields = [
            {"field": "data.referencePaths", "payload": []},
            {"field": "data.referenceError", "payload": repr(e)},
            {"field": "data.referenceSelected", "payload": []}
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
    data = {}
    state = {}

    data["catalog"] = {"columns": [], "data": []}
    data["catalogError"] = ""
    state["catalogPath"] = "/sample-data/products_01.csv"

    state["referenceDir"] = "/reference_items/"
    data["referencePaths"] = []
    data["referenceError"] = ""
    state["referenceSelected"] = []

    state["perPage"] = 15,
    state["pageSizes"] = [10, 15, 30, 50, 100]

    # Run application service
    my_app.run(data=data, state=state, initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
