#!/bin/bash

set -e

# Create/Update the SageMaker Pipeline and wait for the execution to be completed

VIRTUAL_ENV=.venv
DATA_MANIFEST=`cat ./dataManifest.json`

pushd ml_pipeline

# Set up virtual env
virtualenv -p python3 $VIRTUAL_ENV
. $VIRTUAL_ENV/bin/activate 

#Install requirements
pip install -r requirements.txt
pip install sagemaker==2.88.2

echo "Starting Pipeline Execution"
export PYTHONUNBUFFERED=TRUE
echo $PYTHONUNBUFFERED
echo $SAGEMAKER_PIPELINE_ROLE_ARN
echo $SAGEMAKER_PROJECT_NAME
echo $AWS_REGION
echo $SAGEMAKER_ARTIFACT_BUCKET
echo "[{\"Key\":\"sagemaker:project-name\", \"Value\":\"${SAGEMAKER_PROJECT_NAME}\"}]"
python run_pipeline.py --module-name pipeline \
        --role-arn $SAGEMAKER_PIPELINE_ROLE_ARN \
        --tags "[{\"Key\":\"sagemaker:project-name\", \"Value\":\"${SAGEMAKER_PROJECT_NAME}\"}]" \
        --kwargs "{\"region\":\"${AWS_REGION}\",\"role\":\"${SAGEMAKER_PIPELINE_ROLE_ARN}\",\"default_bucket\":\"${SAGEMAKER_ARTIFACT_BUCKET}\",\"pipeline_name\":\"${SAGEMAKER_PROJECT_NAME}\",\"model_package_group_name\":\"${SAGEMAKER_PROJECT_NAME}\",\"base_job_prefix\":\"${SAGEMAKER_PROJECT_NAME}\"}"

echo "Create/Update of the SageMaker Pipeline and execution Completed."

# Deactivate virtual envs
deactivate

popd

export MODEL_PACKAGE_NAME=`cat ml_pipeline/pipelineExecutionArn` 
echo "{\"arn\": \"${MODEL_PACKAGE_NAME}\"}" > pipelineExecution.json
