#!/usr/bin/env node
import cdk = require('@aws-cdk/core');
import { PerfTestStackStack } from '../lib/perf_test_stack-stack';

const STACK_NAME = process.env.STACK_NAME

const app = new cdk.App();
new PerfTestStackStack(app, 'PerfTestStackStack', {stackName: STACK_NAME});