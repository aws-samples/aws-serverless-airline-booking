#!/usr/bin/env node
import cdk = require('@aws-cdk/core');
import { CdkLoadTestStack } from '../lib/cdk-load-test-stack';

const app = new cdk.App();
new CdkLoadTestStack(app, 'CdkLoadTestStack');