# Copyright 2021 Amazon.com, Inc. or its affiliates. All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.                                                                              *

"""A CLI to create or update and run pipelines."""
from __future__ import absolute_import

import argparse
import json
import sys

from _utils import get_pipeline_driver, convert_struct
print("run pipeline started")

def get_model_package_name(pipeline_steps):
    for step in pipeline_steps:
        if step["StepName"] == "RegisterModel":
            return step["Metadata"]["RegisterModel"]["Arn"]

def main():  # pragma: no cover
    """The main harness that creates or updates and runs the pipeline.

    Creates or updates the pipeline and runs it.
    """
    parser = argparse.ArgumentParser(
        "Creates or updates and runs the pipeline for the pipeline script."
    )

    parser.add_argument(
        "-n",
        "--module-name",
        dest="module_name",
        type=str,
        help="The module name of the pipeline to import.",
    )
    parser.add_argument(
        "-kwargs",
        "--kwargs",
        dest="kwargs",
        default=None,
        help="Dict string of keyword arguments for the pipeline generation (if supported)",
    )
    parser.add_argument(
        "-role-arn",
        "--role-arn",
        dest="role_arn",
        type=str,
        help="The role arn for the pipeline service execution role.",
    )
    parser.add_argument(
        "-description",
        "--description",
        dest="description",
        type=str,
        default=None,
        help="The description of the pipeline.",
    )
    parser.add_argument(
        "-tags",
        "--tags",
        dest="tags",
        default=None,
        help="""List of dict strings of '[{"Key": "string", "Value": "string"}, ..]'""",
    )
    args = parser.parse_args()
    print("argssssss", args)

    if args.module_name is None or args.role_arn is None:
        parser.print_help()
        sys.exit(2)
    tags = convert_struct(args.tags)

    try:
        pipeline = get_pipeline_driver(args.module_name, args.kwargs)
        print("###### Creating/updating a SageMaker Pipeline with the following definition:")
        parsed = json.loads(pipeline.definition())
        print(json.dumps(parsed, indent=2, sort_keys=True))

        upsert_response = pipeline.upsert(
            role_arn=args.role_arn, description=args.description, tags=tags
        )
        print("\n###### Created/Updated SageMaker Pipeline: Response received:")
        print(upsert_response)

        execution = pipeline.start()
        print(f"\n###### Execution started with PipelineExecutionArn: {execution.arn}")

        print("Waiting for the execution to finish...")
        execution.wait()
        print("\n#####Execution completed. Execution step details:")

        pipeline_steps = execution.list_steps()
        print(pipeline_steps)

        model_package_name = get_model_package_name(pipeline_steps)
        out_file = open("pipelineExecutionArn", "w")
        out_file.write(model_package_name)
        out_file.close()
                
    except Exception as e:  # pylint: disable=W0703
        print(f"Exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
