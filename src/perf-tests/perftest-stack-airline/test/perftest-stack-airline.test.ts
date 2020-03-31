import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import cdk = require('@aws-cdk/core');
import Stack = require('../lib/perftest-stack-airline-stack');

test('Stack Name should be picked from ENV variable and should be`airline-stack`', () => {
      const app = new cdk.App();
  //     // WHEN
       const stack = new Stack.PerftestStackAirlineStack(app, 'MyTestStack', {stackName: process.env.PERF_TEST_STACK_NAME});
  //     // // THEN
       expect(stack.stackName).toEqual(process.env.PERF_TEST_STACK_NAME);
   });