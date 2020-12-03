import os
from collections import defaultdict
import supervisely_lib as sly

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])
WORKSPACE_ID = int(os.environ['context.workspaceId'])
PROJECT_ID = int(os.environ["modal.state.slyProjectId"])

@my_app.callback("group_reference_objects")
@sly.timeit
def group_reference_objects(api: sly.Api, task_id, context, state, app_logger):
    pass


def main():
    sly.logger.info("Script arguments", extra={
        "TEAM_ID": TEAM_ID,
        "WORKSPACE_ID": WORKSPACE_ID,
        "PROJECT_ID": PROJECT_ID
    })

    # Run application service
    my_app.run(initial_events=[{"command": "group_reference_objects"}])


if __name__ == "__main__":
    sly.main_wrapper("main", main)
