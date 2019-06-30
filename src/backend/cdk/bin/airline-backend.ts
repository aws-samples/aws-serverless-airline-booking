#!/usr/bin/env node
import 'source-map-support/register';
import cdk = require('@aws-cdk/core');
import { AirlineBackendStack } from '../lib/airline-backend-stack';

const app = new cdk.App();
new AirlineBackendStack(app, 'AirlineBackendStack');
