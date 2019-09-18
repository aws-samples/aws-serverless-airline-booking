import cdk = require('@aws-cdk/core');
import ec2 = require('@aws-cdk/aws-ec2')
import ecs = require('@aws-cdk/aws-ecs')
import ecr = require('@aws-cdk/aws-ecr')
import { Role, ServicePrincipal, ManagedPolicy } from '@aws-cdk/aws-iam';
import sfn = require('@aws-cdk/aws-stepfunctions');
import tasks = require('@aws-cdk/aws-stepfunctions-tasks');
import { LogGroup, RetentionDays } from '@aws-cdk/aws-logs';
import { Data } from '@aws-cdk/aws-stepfunctions';

// s3 bucket name
// COGNITO_URL = "https://cognito-idp.eu-west-2.amazonaws.com/"  -> 
// CLIENT_ID   = "1k0ip9j0e6ne61m49cjh8fjete"   --> auth cognito
// val GRAPHQL_URL = "https://qz6v5gusl5e2xdcevlxrbxtgim.appsync-api.eu-west-2.amazonaws.com/graphql"  --> nested apiaws
// val API_URL     = "https://1rwnkmerpi.execute-api.eu-west-2.amazonaws.com/prod/charge"  --> PaymentStack

export class CdkLoadTestStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const role = new Role(this, "loadtest-fargate-role", {
      roleName: 'loadtest-fargate-role',
      assumedBy: new ServicePrincipal('ecs-tasks.amazonaws.com'),
      managedPolicies: [ManagedPolicy.fromAwsManagedPolicyName('service-role/AmazonECSTaskExecutionRolePolicy')]
    })

    const vpc = new ec2.Vpc(this, 'load-test-vpc', {
      cidr: '198.162.0.0/24',
      maxAzs: 2,

    })

    const repository = new ecr.Repository(this, 'gatling-fargate', {
      repositoryName: 'cdk-gatling-fargate'
    });

    const cluster = new ecs.Cluster(this, 'load-test-cluster', {
      vpc: vpc,
      clusterName: 'load-test-cluster'
    });

    const fargateTaskDefinition = new ecs.FargateTaskDefinition(this, "fargate-task-def", {
      family: 'loadtest-fargate',
      executionRole: role,
      taskRole: role,
      memoryLimitMiB: 2048,    
      cpu: 1024      
    });

    const logging = new ecs.AwsLogDriver({
      logGroup: new LogGroup(this, 'loggroup', {
        logGroupName: `/ecs/${cluster.clusterName}`,
        retention: RetentionDays.ONE_WEEK
      }),
      streamPrefix: 'load-test-container'
    })

    // Create container from local `Dockerfile`
    const appContainer = fargateTaskDefinition.addContainer("load-test-container", {
      image: ecs.ContainerImage.fromEcrRepository(repository),
      logging: logging
    });

    // // building Step function for setting the load test
    const setupUsers = new sfn.Task(this, "Setup Users", {
      task: new tasks.RunEcsFargateTask({
        cluster,
        taskDefinition: fargateTaskDefinition,
        assignPublicIp : true,
        containerOverrides: [{
          containerName: appContainer.containerName,
          command : Data.listAt('$.commands')       
        }]
      })
    })

    // const generateAccessTokens = new sfn.Task(this, "Generate Test Access Tokens", {
    //   task: new tasks.RunEcsFargateTask({
    //     cluster,
    //     taskDefinition: fargateTaskDefinition,
    //     assignPublicIp : true,
    //     containerOverrides: [{
    //       containerName: appContainer.containerName,
    //       command : Data.listAt('$.commands')       
    //     }]
    //   })
    // })

    // const loadFlights = new sfn.Task(this, "Load flights", {
    //   task: new tasks.RunEcsFargateTask({
    //     cluster,
    //     taskDefinition: fargateTaskDefinition,
    //     assignPublicIp : true,
    //     containerOverrides: [{
    //       containerName: appContainer.containerName,
    //       command : Data.listAt('$.commands')       
    //     }]
    //   })
    // })

    // const runGatling = new sfn.Task(this, "Run Gatling", {
    //   task: new tasks.RunEcsFargateTask({
    //     cluster,
    //     taskDefinition: fargateTaskDefinition,
    //     assignPublicIp : true,
    //     containerOverrides: [{
    //       containerName: appContainer.containerName,
    //       command : Data.listAt('$.commands')       
    //     }]
    //   })
    // })

    // const generateReport = new sfn.Task(this, "Generate Report", {
    //   task: new tasks.RunEcsFargateTask({
    //     cluster,
    //     taskDefinition: fargateTaskDefinition,
    //     assignPublicIp : true,
    //     containerOverrides: [{
    //       containerName: appContainer.containerName,
    //       command : Data.listAt('$.commands')       
    //     }]
    //   })
    // })

    const stepfuncDef = setupUsers
                      // .next(generateAccessTokens)
                      // .next(loadFlights)
                      // .next(runGatling)
                      // .next(generateReport)

    new sfn.StateMachine(this, "step-load-test", {
      stateMachineName : "cdk-step-load-test",
      definition: stepfuncDef
    })

  }
}

