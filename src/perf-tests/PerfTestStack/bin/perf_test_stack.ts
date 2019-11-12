#!/usr/bin/env node
import cdk = require('@aws-cdk/core');
import { PerfTestStack } from '../lib/perf_test_stack-stack';

const STACK_NAME = process.env.PERF_TEST_STACK_NAME

const app = new cdk.App();
new PerfTestStack(app, 'PerfTestStackStack', {stackName: STACK_NAME});