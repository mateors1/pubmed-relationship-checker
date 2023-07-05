import os
import docker
import boto3

# AWS access keys
access_key = 'YOUR_ACCESS_KEY'
secret_key = 'YOUR_SECRET_KEY'

# AWS region
region = 'us-east-1'

# Configure AWS access keys and region
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=region
)

def find_dockerfile(directory):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dockerfile_path = os.path.join(script_dir, directory, 'Dockerfile')
    if os.path.isfile(dockerfile_path):
        return dockerfile_path
    return None

def build_docker_image(dockerfile_path, image_name):
    client = docker.from_env()
    image, _ = client.images.build(
        path=os.path.dirname(dockerfile_path),
        dockerfile=os.path.basename(dockerfile_path),
        tag=image_name
    )
    return image

def deploy_to_ecs(cluster_name, service_name, task_definition_name, image_name):
    client = session.client('ecs')

    response = client.register_task_definition(
        family=task_definition_name,
        containerDefinitions=[
            {
                'name': 'my-container',
                'image': image_name,
                'portMappings': [
                    {
                        'containerPort': 80,
                        'hostPort': 80,
                        'protocol': 'tcp'
                    },
                ],
                'environment': [
                    {
                        'name': 'MY_ENV_VARIABLE',
                        'value': 'my_value'
                    }
                ],
            },
        ],
    )

    task_definition_arn = response['taskDefinition']['taskDefinitionArn']

    response = client.update_service(
        cluster=cluster_name,
        service=service_name,
        taskDefinition=task_definition_arn,
    )

    print(f"Deployment to ECS initiated. Service ARN: {response['service']['serviceArn']}")

# Name for the Docker image
image_name = 'my-docker-image'

# Name of the ECS cluster and service to deploy to
cluster_name = 'my-ecs-cluster'
service_name = 'my-ecs-service'

# Name for the ECS task definition
task_definition_name = 'my-task-definition'

# Find the Dockerfile in the script's directory
dockerfile_path = find_dockerfile('.')
if dockerfile_path:
    # Build the Docker image
    image = build_docker_image(dockerfile_path, image_name)

    # Deploy the image to ECS
    deploy_to_ecs(cluster_name, service_name, task_definition_name, image_name)
else:
    print("Dockerfile not found in the script's directory.")
