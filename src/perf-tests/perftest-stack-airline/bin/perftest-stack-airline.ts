#!/usr/bin/env node
import cdk = require('@aws-cdk/core');
import { PerftestStackAirlineStack } from '../lib/perftest-stack-airline-stack';

const STACK_NAME = process.env.PERF_TEST_STACK_NAME

const app = new cdk.App();
new PerftestStackAirlineStack(app, 'PerftestStackAirlineStack', {stackName: STACK_NAME});