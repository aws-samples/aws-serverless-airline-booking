"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const cdk = require("@aws-cdk/core");
const ec2 = require("@aws-cdk/aws-ec2");
const ecs = require("@aws-cdk/aws-ecs");
const ecr = require("@aws-cdk/aws-ecr");
const aws_iam_1 = require("@aws-cdk/aws-iam");
const sfn = require("@aws-cdk/aws-stepfunctions");
const tasks = require("@aws-cdk/aws-stepfunctions-tasks");
const aws_logs_1 = require("@aws-cdk/aws-logs");
const aws_stepfunctions_1 = require("@aws-cdk/aws-stepfunctions");
const s3 = require("@aws-cdk/aws-s3");
const aws_events_1 = require("@aws-cdk/aws-events");
const lambda = require("@aws-cdk/aws-lambda");
const COGNITO_USER_POOL_ARN = process.env.COGNITO_USER_POOL_ARN;
const STACK_NAME = process.env.STACK_NAME;
const ROLE_NAME = `${STACK_NAME}-fargate-role`;
const VPC_NAME = `${STACK_NAME}-vpc`;
const CIDR_BLOCK = `198.162.0.0/24`;
const MAX_AZs = 2;
const ECR_GATLING_REPO_NAME = `${STACK_NAME}-gatling`;
const ECR_MOCKDATA_REPO_NAME = `${STACK_NAME}-mockdata`;
const ECS_CLUSTER = `${STACK_NAME}-cluster`;
const GATLING_FARGATE_TASK_DEF = `${STACK_NAME}-gatling-task-def`;
const MOCKDATA_FARGATE_TASK_DEF = `${STACK_NAME}-mockdata-task-def`;
const MEMORY_LIMIT = 2048;
const CPU = 1024;
const GATLING_CONTAINER_NAME = `${STACK_NAME}-gatling-container`;
const MOCKDATA_CONTAINER_NAME = `${STACK_NAME}-mockdata-container`;
const STATE_MACHINE_NAME = `loadtest-${STACK_NAME}`;
const S3_BUCKET_NAME = `${STACK_NAME}-loadtest`;
class PerftestStackAirlineStack extends cdk.Stack {
    constructor(scope, id, props) {
        super(scope, id, props);
        const role = new aws_iam_1.Role(this, ROLE_NAME, {
            roleName: ROLE_NAME,
            assumedBy: new aws_iam_1.ServicePrincipal('ecs-tasks.amazonaws.com')
        });
        const bucket = new s3.Bucket(this, "s3bucket", {
            bucketName: S3_BUCKET_NAME
        });
        role.addToPolicy(new aws_iam_1.PolicyStatement({
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
        }));
        role.addToPolicy(new aws_iam_1.PolicyStatement({
            resources: [`${COGNITO_USER_POOL_ARN}`],
            actions: [
                'cognito-idp:AdminInitiateAuth',
                'cognito-idp:AdminCreateUser',
                'cognito-idp:AdminCreateUser',
                'cognito-idp:AdminSetUserPassword',
                'cognito-idp:UpdateUserPoolClient',
                'cognito-idp:AdminDeleteUser'
            ]
        }));
        const vpc = new ec2.Vpc(this, VPC_NAME, {
            cidr: CIDR_BLOCK,
            maxAzs: MAX_AZs
        });
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
            logGroup: new aws_logs_1.LogGroup(this, GATLING_CONTAINER_NAME, {
                logGroupName: `/aws/ecs/${GATLING_CONTAINER_NAME}`,
                retention: aws_logs_1.RetentionDays.ONE_WEEK
            }),
            streamPrefix: "gatling"
        });
        const mockDatalogging = new ecs.AwsLogDriver({
            logGroup: new aws_logs_1.LogGroup(this, MOCKDATA_CONTAINER_NAME, {
                logGroupName: `/aws//ecs/${MOCKDATA_CONTAINER_NAME}`,
                retention: aws_logs_1.RetentionDays.ONE_WEEK
            }),
            streamPrefix: "mockdata"
        });
        // Create container from local `Dockerfile` for Gatling
        const gatlingAppContainer = gatlingTaskDefinition.addContainer(GATLING_CONTAINER_NAME, {
            image: ecs.ContainerImage.fromEcrRepository(gatlingRepository),
            logging: gatlingLogging
        });
        const mockDataAppContainer = mockDataTaskDefinition.addContainer(MOCKDATA_CONTAINER_NAME, {
            image: ecs.ContainerImage.fromEcrRepository(mockDataRepository),
            logging: mockDatalogging
        });
        // Step function for setting the load test
        const setupUsers = new sfn.Task(this, "Setup Users", {
            task: new tasks.RunEcsFargateTask({
                cluster,
                taskDefinition: mockDataTaskDefinition,
                assignPublicIp: true,
                containerOverrides: [{
                        containerName: mockDataAppContainer.containerName,
                        command: aws_stepfunctions_1.Data.listAt('$.commands'),
                        environment: [
                            {
                                name: 'setup-users',
                                value: aws_stepfunctions_1.Context.taskToken
                            }
                        ]
                    }],
                integrationPattern: aws_stepfunctions_1.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
            })
        });
        const loadFlights = new sfn.Task(this, "Load Flights", {
            task: new tasks.RunEcsFargateTask({
                cluster,
                taskDefinition: mockDataTaskDefinition,
                assignPublicIp: true,
                containerOverrides: [{
                        containerName: mockDataAppContainer.containerName,
                        command: aws_stepfunctions_1.Data.listAt('$.commands'),
                        environment: [
                            {
                                name: 'load-flights',
                                value: aws_stepfunctions_1.Context.taskToken
                            }
                        ]
                    }],
                integrationPattern: aws_stepfunctions_1.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
            })
        });
        const runGatling = new sfn.Task(this, "Run Gatling", {
            task: new tasks.RunEcsFargateTask({
                cluster,
                taskDefinition: gatlingTaskDefinition,
                assignPublicIp: true,
                containerOverrides: [{
                        containerName: gatlingAppContainer.containerName,
                        command: aws_stepfunctions_1.Data.listAt('$.commands'),
                        environment: [
                            {
                                name: 'run-gatling',
                                value: aws_stepfunctions_1.Context.taskToken
                            }
                        ]
                    }],
                integrationPattern: aws_stepfunctions_1.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
            })
        });
        const consolidateReport = new sfn.Task(this, "Consolidate Report", {
            task: new tasks.RunEcsFargateTask({
                cluster,
                taskDefinition: gatlingTaskDefinition,
                assignPublicIp: true,
                containerOverrides: [{
                        containerName: gatlingAppContainer.containerName,
                        command: aws_stepfunctions_1.Data.listAt('$.commands'),
                        environment: [
                            {
                                name: 'consolidate-report',
                                value: aws_stepfunctions_1.Context.taskToken
                            }
                        ]
                    }],
                integrationPattern: aws_stepfunctions_1.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
            })
        });
        const cleanUp = new sfn.Task(this, "Clean Up", {
            task: new tasks.RunEcsFargateTask({
                cluster,
                taskDefinition: mockDataTaskDefinition,
                assignPublicIp: true,
                containerOverrides: [{
                        containerName: mockDataAppContainer.containerName,
                        command: aws_stepfunctions_1.Data.listAt('$.commands'),
                        environment: [
                            {
                                name: 'clean-up',
                                value: aws_stepfunctions_1.Context.taskToken
                            }
                        ]
                    }],
                integrationPattern: aws_stepfunctions_1.ServiceIntegrationPattern.WAIT_FOR_TASK_TOKEN
            })
        });
        const stepfuncDefinition = setupUsers
            .next(loadFlights)
            .next(runGatling)
            .next(consolidateReport)
            .next(cleanUp);
        new sfn.StateMachine(this, STATE_MACHINE_NAME, {
            stateMachineName: STATE_MACHINE_NAME,
            definition: stepfuncDefinition
        });
        const lambdaFunc = new lambda.Function(this, "ecstasklambda", {
            runtime: lambda.Runtime.NODEJS_10_X,
            handler: "index.handler",
            code: new lambda.AssetCode("lambda"),
            functionName: `${STACK_NAME}-ecs-task-change`
        });
        const cwRule = new aws_events_1.Rule(this, "cw-rule", {
            description: "Rule that looks at ECS Task change state and triggers Lambda function",
            enabled: true,
            ruleName: "ECS-task-change-cdk",
            targets: []
        });
        cwRule.addEventPattern({
            source: ['aws.ecs'],
            detailType: ["ECS Task State Change"],
            detail: {
                clusterArn: [cluster.clusterArn]
            }
        });
        new cdk.CfnOutput(this, 's3-bucket', {
            value: bucket.bucketName
        });
    }
}
exports.PerftestStackAirlineStack = PerftestStackAirlineStack;
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoicGVyZnRlc3Qtc3RhY2stYWlybGluZS1zdGFjay5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbInBlcmZ0ZXN0LXN0YWNrLWFpcmxpbmUtc3RhY2sudHMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6Ijs7QUFBQSxxQ0FBc0M7QUFDdEMsd0NBQXdDO0FBQ3hDLHdDQUF3QztBQUN4Qyx3Q0FBd0M7QUFDeEMsOENBQTJFO0FBQzNFLGtEQUFtRDtBQUNuRCwwREFBMkQ7QUFDM0QsZ0RBQTREO0FBQzVELGtFQUFzRjtBQUN0RixzQ0FBdUM7QUFFdkMsb0RBQTJDO0FBQzNDLDhDQUE4QztBQUk5QyxNQUFNLHFCQUFxQixHQUFHLE9BQU8sQ0FBQyxHQUFHLENBQUMscUJBQXFCLENBQUM7QUFDaEUsTUFBTSxVQUFVLEdBQUcsT0FBTyxDQUFDLEdBQUcsQ0FBQyxVQUFVLENBQUM7QUFDMUMsTUFBTSxTQUFTLEdBQUcsR0FBRyxVQUFVLGVBQWUsQ0FBQztBQUMvQyxNQUFNLFFBQVEsR0FBRyxHQUFHLFVBQVUsTUFBTSxDQUFDO0FBQ3JDLE1BQU0sVUFBVSxHQUFHLGdCQUFnQixDQUFDO0FBQ3BDLE1BQU0sT0FBTyxHQUFHLENBQUMsQ0FBQTtBQUNqQixNQUFNLHFCQUFxQixHQUFHLEdBQUcsVUFBVSxVQUFVLENBQUE7QUFDckQsTUFBTSxzQkFBc0IsR0FBRyxHQUFHLFVBQVUsV0FBVyxDQUFBO0FBQ3ZELE1BQU0sV0FBVyxHQUFHLEdBQUcsVUFBVSxVQUFVLENBQUE7QUFDM0MsTUFBTSx3QkFBd0IsR0FBRyxHQUFHLFVBQVUsbUJBQW1CLENBQUE7QUFDakUsTUFBTSx5QkFBeUIsR0FBRyxHQUFHLFVBQVUsb0JBQW9CLENBQUE7QUFDbkUsTUFBTSxZQUFZLEdBQUcsSUFBSSxDQUFBO0FBQ3pCLE1BQU0sR0FBRyxHQUFHLElBQUksQ0FBQTtBQUNoQixNQUFNLHNCQUFzQixHQUFHLEdBQUcsVUFBVSxvQkFBb0IsQ0FBQTtBQUNoRSxNQUFNLHVCQUF1QixHQUFHLEdBQUcs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bkIsVUFBVSxFQUFFLENBQUMsdUJBQXVCLENBQUM7WUFDckMsTUFBTSxFQUFFO2dCQUNOLFVBQVUsRUFBRSxDQUFDLE9BQU8sQ0FBQyxVQUFVLENBQUM7YUFDakM7U0FDRixDQUFDLENBQUE7UUFJRixJQUFJLEdBQUcsQ0FBQyxTQUFTLENBQUMsSUFBSSxFQUFFLFdBQVcsRUFBRTtZQUNuQyxLQUFLLEVBQUUsTUFBTSxDQUFDLFVBQVU7U0FDekIsQ0FBQyxDQUFBO0lBRUosQ0FBQztDQUNGO0FBOU9ELDhEQThPQyIsInNvdXJjZXNDb250ZW50IjpbImltcG9ydCBjZGsgPSByZXF1aXJlKCdAYXdzLWNkay9jb3JlJyk7XG5pbXBvcnQgZWMyID0gcmVxdWlyZSgnQGF3cy1jZGsvYXdzLWVjMicpXG5pbXBvcnQgZWNzID0gcmVxdWlyZSgnQGF3cy1jZGsvYXdzLWVjcycpXG5pbXBvcnQgZWNyID0gcmVxdWlyZSgnQGF3cy1jZGsvYXdzLWVjcicpXG5pbXBvcnQgeyBSb2xlLCBTZXJ2aWNlUHJpbmNpcGFsLCBQb2xpY3lTdGF0ZW1lbnQgfSBmcm9tICdAYXdzLWNkay9hd3MtaWFtJztcbmltcG9ydCBzZm4gPSByZXF1aXJlKCdAYXdzLWNkay9hd3Mtc3RlcGZ1bmN0aW9ucycpO1xuaW1wb3J0IHRhc2tzID0gcmVxdWlyZSgnQGF3cy1jZGsvYXdzLXN0ZXBmdW5jdGlvbnMtdGFza3MnKTtcbmltcG9ydCB7IExvZ0dyb3VwLCBSZXRlbnRpb25EYXlzIH0gZnJvbSAnQGF3cy1jZGsvYXdzLWxvZ3MnO1xuaW1wb3J0IHsgRGF0YSwgU2VydmljZUludGVncmF0aW9uUGF0dGVybiwgQ29udGV4dCB9IGZyb20gJ0Bhd3MtY2RrL2F3cy1zdGVwZnVuY3Rpb25zJztcbmltcG9ydCBzMyA9IHJlcXVpcmUoJ0Bhd3MtY2RrL2F3cy1zMycpO1xuaW1wb3J0IHJ1bGUgPSByZXF1aXJlKCdAYXdzLWNkay9hd3MtZXZlbnRzJylcbmltcG9ydCB7IFJ1bGUgfSBmcm9tICdAYXdzLWNkay9hd3MtZXZlbnRzJztcbmltcG9ydCBsYW1iZGEgPSByZXF1aXJlKCdAYXdzLWNkay9hd3MtbGFtYmRhJylcbmltcG9ydCB7IEFybiB9IGZyb20gJ0Bhd3MtY2RrL2NvcmUnO1xuXG5cbmNvbnN0IENPR05JVE9fVVNFUl9QT09MX0FSTiA9IHByb2Nlc3MuZW52LkNPR05JVE9fVVNFUl9QT09MX0FSTjtcbmNvbnN0IFNUQUNLX05BTUUgPSBwcm9jZXNzLmVudi5TVEFDS19OQU1FO1xuY29uc3QgUk9MRV9OQU1FID0gYCR7U1RBQ0tfTkFNRX0tZmFyZ2F0ZS1yb2xlYDtcbmNvbnN0IFZQQ19OQU1FID0gYCR7U1RBQ0tfTkFNRX0tdnBjYDtcbmNvbnN0IENJRFJfQkxPQ0sgPSBgMTk4LjE2Mi4wLjAvMjRgO1xuY29uc3QgTUFYX0FacyA9IDJcbmNvbnN0IEVDUl9HQVRMSU5HX1JFUE9fTkFNRSA9IGAke1NUQUNLX05BTUV9LWdhdGxpbmdgXG5jb25zdCBFQ1JfTU9DS0RBVEFfUkVQT19OQU1FID0gYCR7U1RBQ0tfTkFNRX0tbW9ja2RhdGFgXG5jb25zdCBFQ1NfQ0xVU1RFUiA9IGAke1NUQUNLX05BTUV9LWNsdXN0ZXJgXG5jb25zdCBHQVRMSU5HX0ZBUkdBVEVfVEFTS19ERUYgPSBgJHtTVEFDS19OQU1FfS1nYXRsaW5nLXRhc2stZGVmYFxuY29uc3QgTU9DS0RBVEFfRkFSR0FURV9UQVNLX0RFRiA9IGAke1NUQUNLX05BTUV9LW1vY2tkYXRhLXRhc2stZGVmYFxuY29uc3QgTUVNT1JZX0xJTUlUID0gMjA0OFxuY29uc3QgQ1BVID0gMTAyNFxuY29uc3QgR0FUTElOR19DT05UQUlORVJfTkFNRSA9IGAke1NUQUNLX05BTUV9LWdhdGxpbmctY29udGFpbmVyYFxuY29uc3QgTU9DS0RBVEFfQ09OVEFJTkVSX05BTUUgPSBgJHtTVEFDS19OQU1FfS1tb2NrZGF0YS1jb250YWluZXJgXG5jb25zdCBTVEFURV9NQUNISU5FX05BTUUgPSBgbG9hZHRlc3QtJHtTVEFDS19OQU1FfWBcbmNvbnN0IFMzX0JVQ0tFVF9OQU1FID0gYCR7U1RBQ0tfTkFNRX0tbG9hZHRlc3RgXG5cbmV4cG9ydCBjbGFzcyBQZXJmdGVzdFN0YWNrQWlybGluZVN0YWNrIGV4dGVuZHMgY2RrLlN0YWNrIHtcbiAgY29uc3RydWN0b3Ioc2NvcGU6IGNkay5BcHAsIGlkOiBzdHJpbmcsIHByb3BzPzogY2RrLlN0YWNrUHJvcHMpIHtcbiAgICBzdXBlcihzY29wZSwgaWQsIHByb3BzKTtcblxuICAgIGNvbnN0IHJvbGUgPSBuZXcgUm9sZSh0aGlzLCBST0xFX05BTUUsIHtcbiAgICAgIHJvbGVOYW1lOiBST0xFX05BTUUsXG4gICAgICBhc3N1bWVkQnk6IG5ldyBTZXJ2aWNlUHJpbmNpcGFsKCdlY3MtdGFza3MuYW1hem9uYXdzLmNvbScpXG4gICAgfSlcblxuICAgIGNvbnN0IGJ1Y2tldCA9IG5ldyBzMy5CdWNrZXQodGhpcywgXCJzM2J1Y2tldFwiLCB7XG4gICAgICBidWNrZXROYW1lOiBTM19CVUNLRVRfTkFNRVxuICAgIH0pXG5cbiAgICByb2xlLmFkZFRvUG9saWN5KG5ldyBQb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgcmVzb3VyY2VzOiBbXG4gICAgICAgIGAke2J1Y2tldC5idWNrZXRBcm59YCxcbiAgICAgICAgYCR7YnVja2V0LmJ1Y2tldEFybn0vKmBcbiAgICAgIF0sXG4gICAgICBhY3Rpb25zOiBbXG4gICAgICAgICdzMzpQdXRPYmplY3QnLFxuICAgICAgICAnczM6R2V0T2JqZWN0QWNsJyxcbiAgICAgICAgJ3MzOkdldE9iamVjdCcsXG4gICAgICAgICdzMzpMaXN0QnVja2V0JyxcbiAgICAgICAgJ3MzOlB1dE9iamVjdEFjbCcsXG4gICAgICAgICdzMzpEZWxldGVPYmplY3QnXG4gICAgICBdXG4gICAgfSkpXG5cbiAgICByb2xlLmFkZFRvUG9saWN5KG5ldyBQb2xpY3lTdGF0ZW1lbnQoe1xuICAgICAgcmVzb3VyY2VzOiBbYCR7Q09HTklUT19VU0VSX1BPT0xfQVJOfWBdLFxuICAgICAgYWN0aW9uczogW1xuICAgICAgICAnY29nbml0by1pZHA6QWRtaW5Jbml0aWF0ZUF1dGgnLFxuICAgICAgICAnY29nbml0by1pZHA6QWRtaW5DcmVhdGVVc2VyJyxcbiAgICAgICAgJ2NvZ25pdG8taWRwOkFkbWluQ3JlYXRlVXNlcicsXG4gICAgICAgICdjb2duaXRvLWlkcDpBZG1pblNldFVzZXJQYXNzd29yZCcsXG4gICAgICAgICdjb2duaXRvLWlkcDpVcGRhdGVVc2VyUG9vbENsaWVudCcsXG4gICAgICAgICdjb2duaXRvLWlkcDpBZG1pbkRlbGV0ZVVzZXInXG4gICAgICBdXG4gICAgfSkpXG5cbiAgICBjb25zdCB2cGMgPSBuZXcgZWMyLlZwYyh0aGlzLCBWUENfTkFNRSwge1xuICAgICAgY2lkcjogQ0lEUl9CTE9DSyxcbiAgICAgIG1heEF6czogTUFYX0Fac1xuICAgIH0pXG5cbiAgICBjb25zdCBnYXRsaW5nUmVwb3NpdG9yeSA9IG5ldyBlY3IuUmVwb3NpdG9yeSh0aGlzLCBFQ1JfR0FUTElOR19SRVBPX05BTUUsIHtcbiAgICAgIHJlcG9zaXRvcnlOYW1lOiBFQ1JfR0FUTElOR19SRVBPX05BTUVcbiAgICB9KTtcblxuICAgIGNvbnN0IG1vY2tEYXRhUmVwb3NpdG9yeSA9IG5ldyBlY3IuUmVwb3NpdG9yeSh0aGlzLCBFQ1JfTU9DS0RBVEFfUkVQT19OQU1FLCB7XG4gICAgICByZXBvc2l0b3J5TmFtZTogRUNSX01PQ0tEQVRBX1JFUE9fTkFNRVxuICAgIH0pO1xuXG4gICAgY29uc3QgY2x1c3RlciA9IG5ldyBlY3MuQ2x1c3Rlcih0aGlzLCBFQ1NfQ0xVU1RFUiwge1xuICAgICAgdnBjOiB2cGMsXG4gICAgICBjbHVzdGVyTmFtZTogRUNTX0NMVVNURVJcbiAgICB9KTtcblxuICAgIGNvbnN0IGdhdGxpbmdUYXNrRGVmaW5pdGlvbiA9IG5ldyBlY3MuRmFyZ2F0ZVRhc2tEZWZpbml0aW9uKHRoaXMsIEdBVExJTkdfRkFSR0FURV9UQVNLX0RFRiwge1xuICAgICAgZmFtaWx5OiBHQVRMSU5HX0ZBUkdBVEVfVEFTS19ERUYsXG4gICAgICBleGVjdXRpb25Sb2xlOiByb2xlLFxuICAgICAgdGFza1JvbGU6IHJvbGUsXG4gICAgICBtZW1vcnlMaW1pdE1pQjogTUVNT1JZX0xJTUlULFxuICAgICAgY3B1OiBDUFVcbiAgICB9KTtcblxuICAgIGNvbnN0IG1vY2tEYXRhVGFza0RlZmluaXRpb24gPSBuZXcgZWNzLkZhcmdhdGVUYXNrRGVmaW5pdGlvbih0aGlzLCBNT0NLREFUQV9GQVJHQVRFX1RBU0tfREVGLCB7XG4gICAgICBmYW1pbHk6IE1PQ0tEQVRBX0ZBUkdBVEVfVEFTS19ERUYsXG4gICAgICBleGVjdXRpb25Sb2xlOiByb2xlLFxuICAgICAgdGFza1JvbGU6IHJvbGUsXG4gICAgICBtZW1vcnlMaW1pdE1pQjogTUVNT1JZX0xJTUlULFxuICAgICAgY3B1OiBDUFVcbiAgICB9KTtcblxuICAgIGNvbnN0IGdhdGxpbmdMb2dnaW5nID0gbmV3IGVjcy5Bd3NMb2dEcml2ZXIoe1xuICAgICAgbG9nR3JvdXA6IG5ldyBMb2dHcm91cCh0aGlzLCBHQVRMSU5HX0NPTlRBSU5FUl9OQU1FLCB7XG4gICAgICAgIGxvZ0dyb3VwTmFtZTogYC9hd3MvZWNzLyR7R0FUTElOR19DT05UQUlORVJfTkFNRX1gLFxuICAgICAgICByZXRlbnRpb246IFJldGVudGlvbkRheXMuT05FX1dFRUtcbiAgICAgIH0pLFxuICAgICAgc3RyZWFtUHJlZml4OiBcImdhdGxpbmdcIlxuICAgIH0pXG5cbiAgICBjb25zdCBtb2NrRGF0YWxvZ2dpbmcgPSBuZXcgZWNzLkF3c0xvZ0RyaXZlcih7XG4gICAgICBsb2dHcm91cDogbmV3IExvZ0dyb3VwKHRoaXMsIE1PQ0tEQVRBX0NPTlRBSU5FUl9OQU1FLCB7XG4gICAgICAgIGxvZ0dyb3VwTmFtZTogYC9hd3MvL2Vjcy8ke01PQ0tEQVRBX0NPTlRBSU5FUl9OQU1FfWAsXG4gICAgICAgIHJldGVudGlvbjogUmV0ZW50aW9uRGF5cy5PTkVfV0VFS1xuICAgICAgfSksXG4gICAgICBzdHJlYW1QcmVmaXg6IFwibW9ja2RhdGFcIlxuICAgIH0pXG5cbiAgICAvLyBDcmVhdGUgY29udGFpbmVyIGZyb20gbG9jYWwgYERvY2tlcmZpbGVgIGZvciBHYXRsaW5nXG4gICAgY29uc3QgZ2F0bGluZ0FwcENvbnRhaW5lciA9IGdhdGxpbmdUYXNrRGVmaW5pdGlvbi5hZGRDb250YWluZXIoR0FUTElOR19DT05UQUlORVJfTkFNRSwge1xuICAgICAgaW1hZ2U6IGVjcy5Db250YWluZXJJbWFnZS5mcm9tRWNyUmVwb3NpdG9yeShnYXRsaW5nUmVwb3NpdG9yeSksXG4gICAgICBsb2dnaW5nOiBnYXRsaW5nTG9nZ2luZ1xuICAgIH0pO1xuXG4gICAgY29uc3QgbW9ja0RhdGFBcHBDb250YWluZXIgPSBtb2NrRGF0YVRhc2tEZWZpbml0aW9uLmFkZENvbnRhaW5lcihNT0NLREFUQV9DT05UQUlORVJfTkFNRSwge1xuICAgICAgaW1hZ2U6IGVjcy5Db250YWluZXJJbWFnZS5mcm9tRWNyUmVwb3NpdG9yeShtb2NrRGF0YVJlcG9zaXRvcnkpLFxuICAgICAgbG9nZ2luZzogbW9ja0RhdGFsb2dnaW5nXG4gICAgfSk7XG5cbiAgICAvLyBTdGVwIGZ1bmN0aW9uIGZvciBzZXR0aW5nIHRoZSBsb2FkIHRlc3RcbiAgICBjb25zdCBzZXR1cFVzZXJzID0gbmV3IHNmbi5UYXNrKHRoaXMsIFwiU2V0dXAgVXNlcnNcIiwge1xuICAgICAgdGFzazogbmV3IHRhc2tzLlJ1bkVjc0ZhcmdhdGVUYXNrKHtcbiAgICAgICAgY2x1c3RlcixcbiAgICAgICAgdGFza0RlZmluaXRpb246IG1vY2tEYXRhVGFza0RlZmluaXRpb24sXG4gICAgICAgIGFzc2lnblB1YmxpY0lwOiB0cnVlLFxuICAgICAgICBjb250YWluZXJPdmVycmlkZXM6IFt7XG4gICAgICAgICAgY29udGFpbmVyTmFtZTogbW9ja0RhdGFBcHBDb250YWluZXIuY29udGFpbmVyTmFtZSxcbiAgICAgICAgICBjb21tYW5kOiBEYXRhLmxpc3RBdCgnJC5jb21tYW5kcycpLFxuICAgICAgICAgIGVudmlyb25tZW50OiBbXG4gICAgICAgICAgICB7XG4gICAgICAgICAgICAgIG5hbWU6ICdzZXR1cC11c2VycycsXG4gICAgICAgICAgICAgIHZhbHVlOiBDb250ZXh0LnRhc2tUb2tlblxuICAgICAgICAgICAgfVxuICAgICAgICAgIF1cbiAgICAgICAgfV0sXG4gICAgICAgIGludGVncmF0aW9uUGF0dGVybjogU2VydmljZUludGVncmF0aW9uUGF0dGVybi5XQUlUX0ZPUl9UQVNLX1RPS0VOXG4gICAgICB9KVxuICAgIH0pXG5cbiAgICBjb25zdCBsb2FkRmxpZ2h0cyA9IG5ldyBzZm4uVGFzayh0aGlzLCBcIkxvYWQgRmxpZ2h0c1wiLCB7XG4gICAgICB0YXNrOiBuZXcgdGFza3MuUnVuRWNzRmFyZ2F0ZVRhc2soe1xuICAgICAgICBjbHVzdGVyLFxuICAgICAgICB0YXNrRGVmaW5pdGlvbjogbW9ja0RhdGFUYXNrRGVmaW5pdGlvbixcbiAgICAgICAgYXNzaWduUHVibGljSXA6IHRydWUsXG4gICAgICAgIGNvbnRhaW5lck92ZXJyaWRlczogW3tcbiAgICAgICAgICBjb250YWluZXJOYW1lOiBtb2NrRGF0YUFwcENvbnRhaW5lci5jb250YWluZXJOYW1lLFxuICAgICAgICAgIGNvbW1hbmQ6IERhdGEubGlzdEF0KCckLmNvbW1hbmRzJyksXG4gICAgICAgICAgZW52aXJvbm1lbnQ6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgbmFtZTogJ2xvYWQtZmxpZ2h0cycsXG4gICAgICAgICAgICAgIHZhbHVlOiBDb250ZXh0LnRhc2tUb2tlblxuICAgICAgICAgICAgfVxuICAgICAgICAgIF1cbiAgICAgICAgfV0sXG4gICAgICAgIGludGVncmF0aW9uUGF0dGVybjogU2VydmljZUludGVncmF0aW9uUGF0dGVybi5XQUlUX0ZPUl9UQVNLX1RPS0VOXG4gICAgICB9KVxuICAgIH0pXG5cbiAgICBjb25zdCBydW5HYXRsaW5nID0gbmV3IHNmbi5UYXNrKHRoaXMsIFwiUnVuIEdhdGxpbmdcIiwge1xuICAgICAgdGFzazogbmV3IHRhc2tzLlJ1bkVjc0ZhcmdhdGVUYXNrKHtcbiAgICAgICAgY2x1c3RlcixcbiAgICAgICAgdGFza0RlZmluaXRpb246IGdhdGxpbmdUYXNrRGVmaW5pdGlvbixcbiAgICAgICAgYXNzaWduUHVibGljSXA6IHRydWUsXG4gICAgICAgIGNvbnRhaW5lck92ZXJyaWRlczogW3tcbiAgICAgICAgICBjb250YWluZXJOYW1lOiBnYXRsaW5nQXBwQ29udGFpbmVyLmNvbnRhaW5lck5hbWUsXG4gICAgICAgICAgY29tbWFuZDogRGF0YS5saXN0QXQoJyQuY29tbWFuZHMnKSxcbiAgICAgICAgICBlbnZpcm9ubWVudDogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBuYW1lOiAncnVuLWdhdGxpbmcnLFxuICAgICAgICAgICAgICB2YWx1ZTogQ29udGV4dC50YXNrVG9rZW5cbiAgICAgICAgICAgIH1cbiAgICAgICAgICBdXG4gICAgICAgIH1dLFxuICAgICAgICBpbnRlZ3JhdGlvblBhdHRlcm46IFNlcnZpY2VJbnRlZ3JhdGlvblBhdHRlcm4uV0FJVF9GT1JfVEFTS19UT0tFTlxuICAgICAgfSlcbiAgICB9KVxuXG4gICAgY29uc3QgY29uc29saWRhdGVSZXBvcnQgPSBuZXcgc2ZuLlRhc2sodGhpcywgXCJDb25zb2xpZGF0ZSBSZXBvcnRcIiwge1xuICAgICAgdGFzazogbmV3IHRhc2tzLlJ1bkVjc0ZhcmdhdGVUYXNrKHtcbiAgICAgICAgY2x1c3RlcixcbiAgICAgICAgdGFza0RlZmluaXRpb246IGdhdGxpbmdUYXNrRGVmaW5pdGlvbixcbiAgICAgICAgYXNzaWduUHVibGljSXA6IHRydWUsXG4gICAgICAgIGNvbnRhaW5lck92ZXJyaWRlczogW3tcbiAgICAgICAgICBjb250YWluZXJOYW1lOiBnYXRsaW5nQXBwQ29udGFpbmVyLmNvbnRhaW5lck5hbWUsXG4gICAgICAgICAgY29tbWFuZDogRGF0YS5saXN0QXQoJyQuY29tbWFuZHMnKSxcbiAgICAgICAgICBlbnZpcm9ubWVudDogW1xuICAgICAgICAgICAge1xuICAgICAgICAgICAgICBuYW1lOiAnY29uc29saWRhdGUtcmVwb3J0JyxcbiAgICAgICAgICAgICAgdmFsdWU6IENvbnRleHQudGFza1Rva2VuXG4gICAgICAgICAgICB9XG4gICAgICAgICAgXVxuICAgICAgICB9XSxcbiAgICAgICAgaW50ZWdyYXRpb25QYXR0ZXJuOiBTZXJ2aWNlSW50ZWdyYXRpb25QYXR0ZXJuLldBSVRfRk9SX1RBU0tfVE9LRU5cbiAgICAgIH0pXG4gICAgfSlcblxuICAgIGNvbnN0IGNsZWFuVXAgPSBuZXcgc2ZuLlRhc2sodGhpcywgXCJDbGVhbiBVcFwiLCB7XG4gICAgICB0YXNrOiBuZXcgdGFza3MuUnVuRWNzRmFyZ2F0ZVRhc2soe1xuICAgICAgICBjbHVzdGVyLFxuICAgICAgICB0YXNrRGVmaW5pdGlvbjogbW9ja0RhdGFUYXNrRGVmaW5pdGlvbixcbiAgICAgICAgYXNzaWduUHVibGljSXA6IHRydWUsXG4gICAgICAgIGNvbnRhaW5lck92ZXJyaWRlczogW3tcbiAgICAgICAgICBjb250YWluZXJOYW1lOiBtb2NrRGF0YUFwcENvbnRhaW5lci5jb250YWluZXJOYW1lLFxuICAgICAgICAgIGNvbW1hbmQ6IERhdGEubGlzdEF0KCckLmNvbW1hbmRzJyksXG4gICAgICAgICAgZW52aXJvbm1lbnQ6IFtcbiAgICAgICAgICAgIHtcbiAgICAgICAgICAgICAgbmFtZTogJ2NsZWFuLXVwJyxcbiAgICAgICAgICAgICAgdmFsdWU6IENvbnRleHQudGFza1Rva2VuXG4gICAgICAgICAgICB9XG4gICAgICAgICAgXVxuICAgICAgICB9XSxcbiAgICAgICAgaW50ZWdyYXRpb25QYXR0ZXJuOiBTZXJ2aWNlSW50ZWdyYXRpb25QYXR0ZXJuLldBSVRfRk9SX1RBU0tfVE9LRU5cbiAgICAgIH0pXG4gICAgfSlcblxuICAgIGNvbnN0IHN0ZXBmdW5jRGVmaW5pdGlvbiA9IHNldHVwVXNlcnNcbiAgICAgIC5uZXh0KGxvYWRGbGlnaHRzKVxuICAgICAgLm5leHQocnVuR2F0bGluZylcbiAgICAgIC5uZXh0KGNvbnNvbGlkYXRlUmVwb3J0KVxuICAgICAgLm5leHQoY2xlYW5VcClcblxuICAgIG5ldyBzZm4uU3RhdGVNYWNoaW5lKHRoaXMsIFNUQVRFX01BQ0hJTkVfTkFNRSwge1xuICAgICAgc3RhdGVNYWNoaW5lTmFtZTogU1RBVEVfTUFDSElORV9OQU1FLFxuICAgICAgZGVmaW5pdGlvbjogc3RlcGZ1bmNEZWZpbml0aW9uXG4gICAgfSlcblxuICAgIGNvbnN0IGxhbWJkYUZ1bmMgPSBuZXcgbGFtYmRhLkZ1bmN0aW9uKHRoaXMsIFwiZWNzdGFza2xhbWJkYVwiLCB7XG4gICAgICBydW50aW1lOiBsYW1iZGEuUnVudGltZS5OT0RFSlNfMTBfWCxcbiAgICAgIGhhbmRsZXI6IFwiaW5kZXguaGFuZGxlclwiLFxuICAgICAgY29kZTogbmV3IGxhbWJkYS5Bc3NldENvZGUoXCJsYW1iZGFcIiksXG4gICAgICBmdW5jdGlvbk5hbWU6IGAke1NUQUNLX05BTUV9LWVjcy10YXNrLWNoYW5nZWBcbiAgICB9KVxuXG4gICAgY29uc3QgY3dSdWxlID0gbmV3IFJ1bGUodGhpcywgXCJjdy1ydWxlXCIsIHtcbiAgICAgIGRlc2NyaXB0aW9uOiBcIlJ1bGUgdGhhdCBsb29rcyBhdCBFQ1MgVGFzayBjaGFuZ2Ugc3RhdGUgYW5kIHRyaWdnZXJzIExhbWJkYSBmdW5jdGlvblwiLFxuICAgICAgZW5hYmxlZDogdHJ1ZSxcbiAgICAgIHJ1bGVOYW1lOiBcIkVDUy10YXNrLWNoYW5nZS1jZGtcIixcbiAgICAgIHRhcmdldHM6IFtcbiAgICAgIF1cbiAgICB9KVxuXG4gICAgY3dSdWxlLmFkZEV2ZW50UGF0dGVybih7XG4gICAgICBzb3VyY2U6IFsnYXdzLmVjcyddLFxuICAgICAgZGV0YWlsVHlwZTogW1wiRUNTIFRhc2sgU3RhdGUgQ2hhbmdlXCJdLFxuICAgICAgZGV0YWlsOiB7XG4gICAgICAgIGNsdXN0ZXJBcm46IFtjbHVzdGVyLmNsdXN0ZXJBcm5dXG4gICAgICB9XG4gICAgfSlcblxuXG5cbiAgICBuZXcgY2RrLkNmbk91dHB1dCh0aGlzLCAnczMtYnVja2V0Jywge1xuICAgICAgdmFsdWU6IGJ1Y2tldC5idWNrZXROYW1lXG4gICAgfSlcblxuICB9XG59XG4iXX0=