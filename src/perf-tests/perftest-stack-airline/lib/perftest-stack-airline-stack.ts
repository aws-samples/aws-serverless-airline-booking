import cdk = require('@aws-cdk/core');
import ec2 = require('@aws-cdk/aws-ec2')
import ecs = require('@aws-cdk/aws-ecs')
import ecr = require('@aws-cdk/aws-ecr')
import { Role, ServicePrincipal, PolicyStatement } from '@aws-cdk/aws-iam';
import sfn = require('@aws-cdk/aws-stepfunctions');
import tasks = require('@aws-cdk/aws-stepfunctions-tasks');
import { LogGroup, RetentionDays } from '@aws-cdk/aws-logs';
import { Data, ServiceIntegrationPattern, Context } from '@aws-cdk/aws-stepfunctions';
import s3 = require('@aws-cdk/aws-s3');
import { Rule } from '@aws-cdk/aws-events';
import lambda = require('@aws-cdk/aws-lambda')
import targets = require('@aws-cdk/aws-events-targets')
import ssm = require('@aws-cdk/aws-ssm');

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
const BRANCH_NAME = process.env.AWS_BRANCH
const FOLDERPATH = "./"

export class PerftestStackAirlineStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // retrieving all environment variables
    const AWS_DEFAULT_REGION = process.env.AWS_DEFAULT_REGION
    const COGNITO_USER_POOL_ARN = process.env.COGNITO_USER_POOL_ARN || "not_defined"
    // const USER_POOL_ID = process.env.USER_POOL_ID || "not_defined"
    // const COGNITO_CLIENT_ID = process.env.COGNITO_CLIENT_ID || "not_defined"
    // const COGNITO_URL = `https://cognito-idp.${AWS_DEFAULT_REGION}.amazonaws.com/`
    // const APPSYNC_URL = process.env.APPSYNC_URL || "not_defined"
    // const API_URL = process.env.API_URL || "not_defined"
    // const GRAPHQL_API_ID = process.env.GRAPHQL_API_ID || "not_defined"

    const role = new Role(this, ROLE_NAME, {
      roleName: ROLE_NAME,
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com')
    })

    const bucket = new s3.Bucket(this, "s3bucket", {
      bucketName: S3_BUCKET_NAME
    })

    role.addToPolicy(new PolicyStatement({
      resources: [
        `${bucket.bucketArn}`,
        `${bucket.bucketArn}/*`
      ],
      actions: [
        's3:PutObject',
        's3:GetObjectAcl',
        's3:GetObject',
        's3:ListBucket',
        's3:PutObjectAcl',
        's3:DeleteObject'
      ]
    }))

    role.addToPolicy(new PolicyStatement({
      resources: [`${COGNITO_USER_POOL_ARN}`],
      actions: [
        'cognito-idp:AdminInitiateAuth',
        'cognito-idp:AdminCreateUser',
        'cognito-idp:AdminSetUserPassword',
        'cognito-idp:UpdateUserPoolClient',
        'cognito-idp:AdminDeleteUser'
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
      logGroup: new LogGroup(this, GATLING_CONTAINER_NAME, {
        logGroupName: `/aws/ecs/${GATLING_CONTAINER_NAME}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: "gatling"
    })

    const mockDatalogging = new ecs.AwsLogDriver({
      logGroup: new LogGroup(this, MOCKDATA_CONTAINER_NAME, {
        logGroupName: `/aws/ecs/${MOCKDATA_CONTAINER_NAME}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: "mockdata"
    })

    const tokenCSV = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/loadtest/csv/token`);
    const userCSV = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/loadtest/csv/user`);
    const loadtestBucket = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/s3/loadtest/bucket`);
    const userPoolID = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/amplify/auth/userpool/id`);
    const cognitoClientID = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/amplify/auth/userpool/clientId`);
    const appsyncAPIKey = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/amplify/api/id`)
    const appsyncURL = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/amplify/api/url`)
    const cognitoURL = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/auth/userpool/url`)
    const apiURL = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/payment/api/charge/url`)
    const stripePublicKey = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/payment/stripe/publicKey`)
    const userCount = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/loadtest/usercount`)
    const duration = ssm.StringParameter.valueForStringParameter(this, `/${BRANCH_NAME}/service/loadtest/duration`)

    // Create container from local `Dockerfile` for Gatling
    const gatlingAppContainer = gatlingTaskDefinition.addContainer(GATLING_CONTAINER_NAME, {
      image: ecs.ContainerImage.fromEcrRepository(gatlingRepository),
      logging: gatlingLogging,
      environment: {
        "APPSYNC_URL": appsyncURL,
        "API_URL": apiURL,
        "COGNITO_URL": cognitoURL,
        "S3_BUCKET": loadtestBucket,
        "TOKEN_CSV": tokenCSV,
        "STRIPE_PUBLIC_KEY": stripePublicKey,
        "USER_COUNT": userCount,
        "DURATION": duration
      }
    });

    const mockDataAppContainer = mockDataTaskDefinition.addContainer(MOCKDATA_CONTAINER_NAME, {
      image: ecs.ContainerImage.fromEcrRepository(mockDataRepository),
      logging: mockDatalogging,
      environment: {
        "TOKEN_CSV": tokenCSV,
        "USER_CSV": userCSV,
        "AWS_REGION": `${AWS_DEFAULT_REGION}`,
        "S3_BUCKET": loadtestBucket,
        "USER_POOL_ID": userPoolID,
        "COGNITO_CLIENT_ID": cognitoClientID,
        "FOLDERPATH": FOLDERPATH,
        "APPSYNC_API_KEY": appsyncAPIKey,
        "APPSYNC_URL": appsyncURL
      }
    });

    // Step function for setting the load test
    const setupUsers = new sfn.Task(this, "Setup Users", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: mockDataTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: mockDataAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'setup-users',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const loadFlights = new sfn.Task(this, "Load Flights", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: mockDataTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: mockDataAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'load-flights',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const runGatling = new sfn.Task(this, "Run Gatling", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: gatlingTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: gatlingAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'run-gatling',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const consolidateReport = new sfn.Task(this, "Consolidate Report", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: gatlingTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: gatlingAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'consolidate-report',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const cleanUp = new sfn.Task(this, "Clean Up", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: mockDataTaskDefinition,
        assignPublicIp: true,
        containerOverrides: [{
          containerName: mockDataAppContainer.containerName,
          command: Data.listAt('$.commands'),
          environment: [
            {
              name: 'clean-up',
              value: Context.taskToken
            }
          ]
        }],
        integrationPattern: ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
      })
    })

    const stepfuncDefinition = setupUsers
      .next(loadFlights)
      .next(runGatling)
      .next(consolidateReport)
      .next(cleanUp)

    const loadtestsfn = new sfn.StateMachine(this, STATE_MACHINE_NAME, {
      stateMachineName: STATE_MACHINE_NAME,
      definition: stepfuncDefinition
    })

    const ecsLambda = new lambda.Function(this, "ecstasklambda", {
      runtime: lambda.Runtime.NODEJS_10_X,
      handler: "index.handler",
      code: new lambda.AssetCode("lambda"),
      functionName: `${STACK_NAME}-ecs-task-change`
    })

    ecsLambda.addToRolePolicy(new PolicyStatement({
      actions: ["states:SendTaskSuccess"],
      resources: [loadtestsfn.stateMachineArn]
    }))

    const cwRule = new Rule(this, "cw-rule", {
      description: "Rule that looks at ECS Task change state and triggers Lambda function",
      enabled: true,
      ruleName: "ECS-task-change-cdk",
      targets: [
      ]
    })

    new ssm.StringParameter(this, 'LoadTestS3Bucket', {
      // description: 'Some user-friendly description',
      parameterName: `/${BRANCH_NAME}/service/s3/loadtest/bucket`,
      stringValue: bucket.bucketName,
      // allowedPattern: '.*',
    });

    cwRule.addEventPattern({
      source: ['aws.ecs'],
      detailType: ["ECS Task State Change"],
      detail: {
        clusterArn: [cluster.clusterArn],
        lastStatus: ["STOPPED"]
      }
    })

    cwRule.addTarget(new targets.LambdaFunction(ecsLambda))

  }
}
