import os
import json
import pandas as pd
import supervisely_lib as sly
from generate_example import prepare_example


my_app = sly.AppService()
TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
CATALOG_DF = None
CATALOG_COLUMNS = []

REFERENCE_PATHS = None
REFERENCE_DATA = {}
KEY_TAG_NAME = None


@my_app.callback("preview_catalog")
@sly.timeit
def preview_catalog(api: sly.Api, task_id, context, state, app_logger):
    global CATALOG_PATH, CATALOG_DF, CATALOG_COLUMNS
    catalog_path: str = state["catalogPath"]
    local_path = os.path.join(my_app.data_dir, catalog_path.lstrip("/"))
    try:
        api.file.download(TEAM_ID, catalog_path, local_path)
        catalog_df = pd.read_csv(local_path)
        CATALOG_COLUMNS = [col for col in catalog_df.columns]
        catalog_df.insert(0, '#', list(range(len(catalog_df))))
        fields = [
            {"field": "data.catalog", "payload": json.loads(catalog_df.to_json(orient="split"))},
            {"field": "data.catalogError", "payload": ""},
            {"field": "data.catalogColumns", "payload": CATALOG_COLUMNS},
            {"field": "state.selectedColumn", "payload": CATALOG_COLUMNS[0]},
            {"field": "state.groupingColumns", "payload": [False] * len(CATALOG_COLUMNS)},
        ]
        CATALOG_DF = catalog_df
    except Exception as e:
        fields = [
            {"field": "data.catalog", "payload": {"columns": [], "data": []}},
            {"field": "data.catalogError", "payload": repr(e)},
            {"field": "data.catalogColumns", "payload": []},
            {"field": "state.selectedColumn", "payload": ""},
            {"field": "state.groupingColumns", "payload": []},
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
    global REFERENCE_DATA, KEY_TAG_NAME
    all_keys = set()
    references_count = 0

    try:
        selected = state["referenceSelected"]
        for flag, remote_path in zip(selected, REFERENCE_PATHS):
            if flag is False:
                continue
            local_path = os.path.join(my_app.data_dir, remote_path.lstrip("/"))
            api.file.download(TEAM_ID, remote_path, local_path)
            cur_ref_data = sly.json.load_json_file(local_path)
            if KEY_TAG_NAME is None:
                KEY_TAG_NAME = cur_ref_data["key_tag_name"]
            else:
                if cur_ref_data["key_tag_name"] != KEY_TAG_NAME:
                    raise ValueError("Key tag name {!r} in file {!r} differs from name in other files"
                                     .format(cur_ref_data["key_tag_name"], remote_path))
            REFERENCE_DATA[remote_path] = cur_ref_data
            all_keys.update(cur_ref_data["all_keys"])
            for k, v in cur_ref_data["references"].items():
                references_count += len(v)
        fields = [
            {"field": "data.referenceMessage", "payload": "Validation passed: {} keys has {} items in total"
                                                          .format(len(all_keys), references_count)},
            {"field": "data.messageColor", "payload": "green"},
            {"field": "data.keyTagName", "payload": KEY_TAG_NAME},
            {"field": "data.keysCount", "payload": len(all_keys)},
            {"field": "data.referencesCount", "payload": references_count},
        ]
    except Exception as e:
        fields = [
            {"field": "data.referenceMessage", "payload": repr(e)},
            {"field": "data.messageColor", "payload": "red"},
            {"field": "data.keyTagName", "payload": ""},
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
    data["catalogColumns"] = CATALOG_COLUMNS
    state["selectedColumn"] = ""
    state["groupingColumns"] = [False] * len(CATALOG_COLUMNS)

    state["referenceDir"] = "/reference_items/"
    data["referencePaths"] = []
    data["referenceMessage"] = ""
    data["messageColor"] = "red"
    state["referenceSelected"] = []
    data["validationMsg"] = ""
    data["keyTagName"] = ""

    state["perPage"] = 15,
    state["pageSizes"] = [10, 15, 30, 50, 100]

    # Run application service
    my_app.run(data=data, state=state, initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
