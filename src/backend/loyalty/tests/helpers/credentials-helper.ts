import Sts, { AssumeRoleRequest } from 'aws-sdk/clients/sts';

const sts = new Sts();

interface Credentials {
  accessKeyId: string,
  secretAccessKey: string,
  sessionToken: string
}

export async function getCredentials(roleArn: string, externalId: string | undefined): Promise<Credentials> {
  const params:AssumeRoleRequest = {
    RoleArn: roleArn,
    DurationSeconds: 900,
    RoleSessionName: 'AirlineTest'
  };
  if (externalId !== undefined) {
    params.ExternalId = externalId;
  }
  const result = await sts.assumeRole(params).promise();

  return {
    accessKeyId: result.Credentials!.AccessKeyId,
    secretAccessKey: result.Credentials!.SecretAccessKey,
    sessionToken: result.Credentials!.SessionToken
  };
}