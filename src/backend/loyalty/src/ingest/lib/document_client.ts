const AWSXRay = require('aws-xray-sdk-core')

import { DocumentClient } from 'aws-sdk/clients/dynamodb';
import { AWSError } from 'aws-sdk/lib/error';
import { Request } from 'aws-sdk/lib/request';

let client: DocumentClient;
client = new DocumentClient();

AWSXRay.captureAWSClient((client as any).service);

/**
 * Document Client Interface
 * 
 * A replaceable document client object that can be replaced 
 */
export interface DocumentClientInterface {
  put(params: DocumentClient.PutItemInput, callback?: (err: AWSError, data: DocumentClient.PutItemOutput) => void): Request<DocumentClient.PutItemOutput, AWSError>;
}

/**
 * Default Document Client
 * 
 * @type DocumentClientInterface
 */
export let DefaultDocumentClient: DocumentClientInterface = client;
export type PutInput = DocumentClient.PutItemInput