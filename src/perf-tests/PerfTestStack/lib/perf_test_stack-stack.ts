import cdk = require('@aws-cdk/core');
import ec2 = require('@aws-cdk/aws-ec2')
import ecs = require('@aws-cdk/aws-ecs')
import ecr = require('@aws-cdk/aws-ecr')
import { Role, ServicePrincipal, ManagedPolicy, PolicyStatement } from '@aws-cdk/aws-iam';
import sfn = require('@aws-cdk/aws-stepfunctions');
import tasks = require('@aws-cdk/aws-stepfunctions-tasks');
import { LogGroup, RetentionDays } from '@aws-cdk/aws-logs';
import { Data, ServiceIntegrationPattern, Context } from '@aws-cdk/aws-stepfunctions';
import s3 = require('@aws-cdk/aws-s3');
import { Bucket } from '@aws-cdk/aws-s3';

const STACK_NAME = process.env.STACK_NAME;
const ROLE_NAME = `${STACK_NAME}-fargate-role`;
const VPC_NAME = `${STACK_NAME}-vpc`;
const CIDR_BLOCK = `198.162.0.0/24`;
const MAX_AZs = 2
const ECR_GATLING_REPO_NAME = `${STACK_NAME}-gatling`
const ECR_MOCKDATA_REPO_NAME = `${STACK_NAME}-mockdata`
const ECS_CLUSTER = `${STACK_NAME}-cluster`
const GATLING_FARGATE_TASK_DEF = `${STACK_NAME}-gatling-task-def`
const MOCKDATA_FARGATE_TASK_DEF = `${STACK_NAME}-mockdata-task-def`
const MEMORY_LIMIT = 2048
const CPU = 1024
const GATLING_CONTAINER_NAME = `${STACK_NAME}-gatling-container`
const MOCKDATA_CONTAINER_NAME = `${STACK_NAME}-mockdata-container`
const STATE_MACHINE_NAME = `loadtest-${STACK_NAME}`
const S3_BUCKET_NAME = `${STACK_NAME}-loadtest`

export class PerfTestStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const role = new Role(this, ROLE_NAME, {
      roleName: ROLE_NAME,
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [
        ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')
      ]
    })

    const bucket = new s3.Bucket(this, "s3bucket", {
      bucketName: S3_BUCKET_NAME       
    })

    role.addToPolicy(new PolicyStatement({
      resources : [
        `${bucket.bucketArn}`,
        `${bucket.bucketArn}/*`
      ],
      actions: [
        's3:PutObject',
        's3:GetObjectAcl',
        's3:GetObject',
        's3:ListBucket',
        's3:PutObjectAcl'
      ]
    }))
   
    const vpc = new ec2.Vpc(this, VPC_NAME, {
      cidr: CIDR_BLOCK,
      maxAzs: MAX_AZs
    })

    const gatlingRepository = new ecr.Repository(this, ECR_GATLING_REPO_NAME, {
      repositoryName: ECR_GATLING_REPO_NAME
    });

    const mockDataRepository = new ecr.Repository(this, ECR_MOCKDATA_REPO_NAME, {
      repositoryName: ECR_MOCKDATA_REPO_NAME
    });

    const cluster = new ecs.Cluster(this, ECS_CLUSTER, {
      vpc: vpc,
      clusterName: ECS_CLUSTER
    });

    const gatlingTaskDefinition = new ecs.FargateTaskDefinition(this, GATLING_FARGATE_TASK_DEF, {
      family: GATLING_FARGATE_TASK_DEF,
      executionRole: role,
      taskRole: role,
      memoryLimitMiB: MEMORY_LIMIT,
      cpu: CPU
    });

    const mockDataTaskDefinition = new ecs.FargateTaskDefinition(this, MOCKDATA_FARGATE_TASK_DEF, {
      family: MOCKDATA_FARGATE_TASK_DEF,
      executionRole: role,
      taskRole: role,
      memoryLimitMiB: MEMORY_LIMIT,
      cpu: CPU
    });

    const gatlingLogging = new ecs.AwsLogDriver({
      logGroup: new LogGroup(this, 'loggroup', {
        logGroupName: `/ecs/${cluster.clusterName}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: GATLING_CONTAINER_NAME
    })

    const mockDatalogging = new ecs.AwsLogDriver({
      logGroup: new LogGroup(this, 'loggroup', {
        logGroupName: `/ecs/${cluster.clusterName}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: MOCKDATA_CONTAINER_NAME
    })

    // Create container from local `Dockerfile` for Gatling
    const gatlingAppContainer = gatlingTaskDefinition.addContainer(GATLING_CONTAINER_NAME, {
      image: ecs.ContainerImage.fromEcrRepository(gatlingRepository),
      logging: gatlingLogging
    });

    // Step function for setting the load test
    const setupUsers = new sfn.Task(this, "Setup Users", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: gatlingTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: gatlingAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'setup-complete',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const mockDataAppContainer = mockDataTaskDefinition.addContainer(MOCKDATA_CONTAINER_NAME, {
      image: ecs.ContainerImage.fromEcrRepository(mockDataRepository),
      logging: mockDatalogging
    });

    const generateTokens = new sfn.Task(this, "Generate Tokens", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: mockDataTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: mockDataAppContainer.containerName,
          command: Data.listAt('$.commands')
        }]
      })
    })


    const stepfuncDefinition = setupUsers
                                  .next(generateTokens)
    // .next(loadFlights)
    // .next(runGatling)
    // .next(generateReport)

    new sfn.StateMachine(this, STATE_MACHINE_NAME, {
      stateMachineName: STATE_MACHINE_NAME,
      definition: stepfuncDefinition
    })

  }
}
