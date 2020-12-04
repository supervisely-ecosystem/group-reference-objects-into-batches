import os
import json
import pandas as pd
import supervisely_lib as sly
from generate_example import prepare_example


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
CATALOG_DF = None
REFERENCE_PATHS = None
REFERENCE_DATA = {}


@my_app.callback("preview_catalog")
@sly.timeit
def preview_catalog(api: sly.Api, task_id, context, state, app_logger):
    global CATALOG_PATH, CATALOG_DF
    catalog_path: str = state["catalogPath"]
    local_path = os.path.join(my_app.data_dir, catalog_path.lstrip("/"))
    try:
        api.file.download(TEAM_ID, catalog_path, local_path)
        catalog_df = pd.read_csv(local_path)
        catalog_df.insert(0, '#', list(range(len(catalog_df))))
        fields = [
            {"field": "data.catalog", "payload": json.loads(catalog_df.to_json(orient="split"))},
            {"field": "data.catalogError", "payload": ""},
        ]
        CATALOG_DF = catalog_df
    except Exception as e:
        fields = [
            {"field": "data.catalog", "payload": {"columns": [], "data": []}},
            {"field": "data.catalogError", "payload": repr(e)},
        ]
        CATALOG_DF = None
    api.app.set_fields(task_id, fields)


@my_app.callback("preview_reference_files")
@sly.timeit
def preview_reference_files(api: sly.Api, task_id, context, state, app_logger):
    global REFERENCE_PATHS
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
        REFERENCE_PATHS = paths
    except Exception as e:
        fields = [
            {"field": "data.referencePaths", "payload": []},
            {"field": "data.referenceError", "payload": repr(e)},
            {"field": "data.referenceSelected", "payload": []}
        ]
        REFERENCE_PATHS = None
    api.app.set_fields(task_id, fields)


@my_app.callback("validate_reference_files")
@sly.timeit
def validate_reference_files(api: sly.Api, task_id, context, state, app_logger):
    global REFERENCE_DATA
    try:
        selected = state["referenceSelected"]
        for flag, remote_path in zip(selected, REFERENCE_PATHS):
            if flag is False:
                continue
            local_path = os.path.join(my_app.data_dir, remote_path.lstrip("/"))
            api.file.download(TEAM_ID, remote_path, local_path)
            REFERENCE_DATA[remote_path] = sly.json.load_json_file(local_path)
        fields = [
            {"field": "data.referenceError", "payload": ""},
        ]
    except Exception as e:
        fields = [
            {"field": "data.referenceError", "payload": repr(e)},
        ]
        REFERENCE_DATA = {}

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
