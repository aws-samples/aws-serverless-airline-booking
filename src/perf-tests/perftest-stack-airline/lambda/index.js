'use strict'

// 
//  The Loadtest Step function executes a series of tasks (creates mock users, load flight data etc) 
//  and this Lambda function calls Step Functions with the task token for each of those tasks 

const AWS = require('aws-sdk')
const sfn = new AWS.StepFunctions()

exports.handler = async function (event, context) {
    console.log(JSON.stringify(event));

    const detail = event.detail;
    const token = detail.overrides.containerOverrides[0].environment[0].value;
    const taskType = detail.overrides.containerOverrides[0].environment[0].name;

    if (detail.lastStatus == "STOPPED") {
        let cmds;

        switch (taskType) {
            case "setup-users":
                cmds = "./load-flight-data.py";
                break;
            case "load-flights":
                cmds = "-s Airline -nr -rf /opt/gatling/results/airline";
                break;
            case "run-gatling":
                cmds = "-ro airline";
                break;
            case "consolidate-report":
                cmds = "./cleanup.py";
                break;
        }

        const params = {
            output: JSON.stringify({ "commands": [cmds] }), /* required */
            taskToken: token /* required */
        };

        await sfn.sendTaskSuccess(params).promise();
    }
};