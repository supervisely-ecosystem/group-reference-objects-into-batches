import os
import pandas as pd
from generate_example import prepare_example

import supervisely_lib as sly


my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])


@my_app.callback("group_reference_objects")
@sly.timeit
def group_reference_objects(api: sly.Api, task_id, context, state, app_logger):
    pass


def main():

    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
    })

    prepare_example()

    # Run application service
    my_app.run(initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
