import cdk = require('@aws-cdk/core');
import ec2 = require('@aws-cdk/aws-ec2')
import ecs = require('@aws-cdk/aws-ecs')
import ecr = require('@aws-cdk/aws-ecr')
import { Role, ServicePrincipal, ManagedPolicy } from '@aws-cdk/aws-iam';
import sfn = require('@aws-cdk/aws-stepfunctions');
import tasks = require('@aws-cdk/aws-stepfunctions-tasks');
import { LogGroup, RetentionDays } from '@aws-cdk/aws-logs';
import { Data } from '@aws-cdk/aws-stepfunctions';

const STACK_NAME = process.env.STACK_NAME;
const ROLE_NAME = `${STACK_NAME}-fargate-role`;
const VPC_NAME = `${STACK_NAME}-vpc`;
const CIDR_BLOCK = `198.162.0.0/24`;
const MAX_AZs = 2
const ECR_REPO_NAME = `${STACK_NAME}-gatling`
const ECS_CLUSTER = `${STACK_NAME}-cluster`
const FARGATE_TASK_DEF = `${STACK_NAME}-fargate-task-def`
const MEMORY_LIMIT = 2048
const CPU = 1024
const CONTAINER_NAME = `${STACK_NAME}-container`
const STATE_MACHINE_NAME = `${STACK_NAME}`

export class PerfTestStackStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const role = new Role(this, ROLE_NAME, {
      roleName: ROLE_NAME,
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')]
    })

    const vpc = new ec2.Vpc(this, VPC_NAME, {
      cidr: CIDR_BLOCK,
      maxAzs: MAX_AZs
    })

    const repository = new ecr.Repository(this, ECR_REPO_NAME, {
      repositoryName: ECR_REPO_NAME
    });

    const cluster = new ecs.Cluster(this, ECS_CLUSTER, {
      vpc: vpc,
      clusterName: ECS_CLUSTER
    });

    const fargateTaskDefinition = new ecs.FargateTaskDefinition(this, FARGATE_TASK_DEF, {
      family: FARGATE_TASK_DEF,
      executionRole: role,
      taskRole: role,
      memoryLimitMiB: MEMORY_LIMIT,
      cpu: CPU
    });

    const logging = new ecs.AwsLogDriver({
      logGroup: new LogGroup(this, 'loggroup', {
        logGroupName: `/ecs/${cluster.clusterName}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: CONTAINER_NAME
    })

    // Create container from local `Dockerfile`
    const appContainer = fargateTaskDefinition.addContainer(CONTAINER_NAME, {
      image: ecs.ContainerImage.fromEcrRepository(repository),
      logging: logging
    });

    // Step function for setting the load test
    const setupUsers = new sfn.Task(this, "Setup Users", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: fargateTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: appContainer.containerName,
          command: Data.listAt('$.commands')
        }]
      })
    })


    const stepfuncDefinition = setupUsers
    // .next(generateAccessTokens)
    // .next(loadFlights)
    // .next(runGatling)
    // .next(generateReport)

    new sfn.StateMachine(this, STATE_MACHINE_NAME, {
      stateMachineName: STATE_MACHINE_NAME,
      definition: stepfuncDefinition
    })

  }
}
