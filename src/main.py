import os
import json
import pandas as pd
from collections import defaultdict

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
KEY_EXAMPLES = None

GROUP_COLUMNS = None
BATCHES = []


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
            {"field": "data.referenceSelected", "payload": [False] * len(paths)},
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
    global REFERENCE_DATA, KEY_TAG_NAME, KEY_EXAMPLES
    all_keys = set()
    references_count = 0
    KEY_EXAMPLES = defaultdict(list)

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

            for key, examples in cur_ref_data["references"].items():
                KEY_EXAMPLES[key].extend(examples)

            all_keys.update(cur_ref_data["all_keys"])
            for k, v in cur_ref_data["references"].items():
                references_count += len(v)
        fields = [
            {"field": "data.referenceMessage", "payload": "Validation passed: {} reference items with {} examples"
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


@my_app.callback("preview_groups")
@sly.timeit
def preview_groups(api: sly.Api, task_id, context, state, app_logger):
    global BATCHES, GROUP_COLUMNS

    BATCHES = []
    main_column_name = state["selectedColumn"]
    group_size = state["groupSize"]

    #@TODO: for debug; use real items - NIY
    reference_keys = list(CATALOG_DF[main_column_name])[:300]
    filtered_catalog = CATALOG_DF[CATALOG_DF[main_column_name].isin(reference_keys)]

    GROUP_COLUMNS = []
    for col_name, checked in zip(CATALOG_COLUMNS, state["groupingColumns"]):
        if checked is True:
            GROUP_COLUMNS.append(col_name)
    groups_preview = []
    groups = filtered_catalog.groupby(GROUP_COLUMNS)
    group_index = 0
    for k, v in groups:
        g = groups.get_group(k)
        #g = g.drop(GROUP_COLUMNS, axis=1)

        group_name = ""
        for col_name, col_value in zip(GROUP_COLUMNS, k):
            group_name += "{}: {}; ".format(col_name, col_value)

        list_df = [g[i:i + group_size] for i in range(0, g.shape[0], group_size)]
        for batch_df in list_df:
            BATCHES.append({
                "column_names": GROUP_COLUMNS,
                "column_values": k,
                "df": batch_df
            })
            html = batch_df.to_html()
            groups_preview.append({"name": group_name, "htmlTable": html, "index": group_index})
            group_index += 1

    save_path = api.file.get_free_name(TEAM_ID, os.path.join(state["referenceDir"], "batches.json"))
    fields = [
        {"field": "data.groupsPreview", "payload": groups_preview},
        {"field": "state.savePath", "payload": save_path},
    ]
    api.app.set_fields(task_id, fields)


@my_app.callback("save_groups")
@sly.timeit
def save_groups(api: sly.Api, task_id, context, state, app_logger):
    try:
        if state["savePath"] == "":
            raise ValueError("Save path is undefined")
        if api.file.exists(TEAM_ID, state["savePath"]):
            raise ValueError("File already exists. Remove it manually or change save path")

        result = []
        for idx, batch_original in enumerate(BATCHES):
            batch = {
                "batch_index": idx,
                "group_columns": dict(zip(batch_original["column_names"], batch_original["column_values"])),
                "key_col_name": state["selectedColumn"],
                "references": {},
                "references_catalog_info": {}
            }

            batch_original["df"]: pd.DataFrame
            batch_catalog = batch_original["df"].to_json(orient="records")
            batch_catalog = json.loads(batch_catalog)
            for batch_catalog_row in batch_catalog:
                key = batch_catalog_row[state["selectedColumn"]]
                batch["references"][key] = KEY_EXAMPLES[key]
                del batch_catalog_row['#']
                batch["references_catalog_info"][key] = batch_catalog_row

            result.append(batch)

        local_path = os.path.join(my_app.data_dir, sly.fs.get_file_name_with_ext(state["savePath"]))
        sly.json.dump_json_file(result, local_path)
        api.file.upload(TEAM_ID, local_path, state["savePath"])
        sly.fs.silent_remove(local_path)

        fields = [
            {"field": "data.saveMessage", "payload": "File has been successfully saved"},
            {"field": "data.saveColor", "payload": "greed"},
        ]
    except Exception as e:
        fields = [
            {"field": "data.saveMessage", "payload": repr(e)},
            {"field": "data.saveColor", "payload": "red"},
        ]

    api.app.set_fields(task_id, fields)


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

    state["referenceDir"] = "/reference_items/"
    data["referencePaths"] = []
    data["referenceMessage"] = ""
    data["messageColor"] = "red"
    state["referenceSelected"] = []
    data["validationMsg"] = ""
    data["keyTagName"] = ""

    state["groupSize"] = 9
    state["groupingColumns"] = [False] * len(CATALOG_COLUMNS)
    data["groupsPreview"] = []

    data["savePath"] = ""
    data["saveMessage"] = ""
    data["saveColor"] = "red"

    state["perPage"] = 15,
    state["pageSizes"] = [10, 15, 30, 50, 100]

    # Run application service
    my_app.run(data=data, state=state)


#@TODO: style group tables
#@TODO: use real keys from files
if __name__ == "__main__":
    sly.main_wrapper("main", main)
