// import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import cdk = require('@aws-cdk/core');
import Stack = require('../lib/perf_test_stack-stack');

test('Stack Name should be picked from ENV variable and should be`airline-stack`', () => {
    const app = new cdk.App();
    // WHEN
    const stack = new Stack.PerfTestStack(app, 'MyTestStack', {stackName: process.env.STACK_NAME});
    // // THEN
    expect(stack.stackName).toEqual(process.env.STACK_NAME);
});