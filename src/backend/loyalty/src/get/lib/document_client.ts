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
  query(params: DocumentClient.QueryInput, callback?: (err: AWSError, data: DocumentClient.QueryOutput) => void): Request<DocumentClient.QueryOutput, AWSError>;
}

/**
 * Default Document Client
 * 
 * @type DocumentClientInterface
 */
// export let DefaultDocumentClient: DocumentClientInterface = new DocumentClient();
export let DefaultDocumentClient: DocumentClientInterface = client;
export type QueryInput = DocumentClient.QueryInput
export type ItemList = DocumentClient.ItemList