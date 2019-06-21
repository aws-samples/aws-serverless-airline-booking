import { DocumentClient } from 'aws-sdk/clients/dynamodb';
import { AWSError } from 'aws-sdk/lib/error';
import { Request } from 'aws-sdk/lib/request';

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
export let DefaultDocumentClient: DocumentClientInterface = new DocumentClient();
export type PutInput = DocumentClient.PutItemInput