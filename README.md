# dynamodb-autoscaling-to-slack
Notifies in Slack when dynamoDB table autoscaling takes place

[![Build Status](https://travis-ci.org/Signiant/dynamodb-autoscaling-to-slack.svg?branch=master)](https://travis-ci.org/Signiant/dynamodb-autoscaling-to-slack)


# Purpose
DynamoDB native autoscaling is fantastic but what happens if you want to see when it's actually scaling tables?  This project will use a lambda function to notify a slack channel when a table or index is autoscaled (up or down)

# Sample Output

![Sample Slack Posts](https://raw.githubusercontent.com/Signiant/dynamodb-autoscaling-to-slack/master/images/dynamodb-autoscaler-notifier.jpg)

# Installing and Configuring

## Slack Setup
Before installing anything to AWS, you will need to a "bot" in Slack to handle the posting for you. You need an API token for this bot and provide it in the CloudFormation setup parameters.

The old method, which is now deprecated;
* ~~In Slack, choose _Manage Apps_ -> _Custom Integrations_ -> _Bots_~~
  * ~~Add a new bot configuration~~
  * ~~username: dynamodb-notifier~~
  * ~~Copy the API Token.~~
  * ~~Don't worry about other parameters - the notifier over-rides them anyway~~

Current working method;
* Generate a [legacy API Token](https://api.slack.com/custom-integrations/legacy-tokens) (scroll down to "Legacy token generator", you may need to be logged in to slack workspace account)

Optionally install the DDB custom emoji;
* In Slack, upload a custom emoji and name it _:dynamodb-autoscaling:_
  * You can use any image here...one is provided in the _emoji_ folder of this project also

## AWS Setup

> You must have [Cloudtrail enabled](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html) in your AWS account for this solution to work.  It uses a [Cloudwatch rule triggered on a Cloudtrail event](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/Create-CloudWatch-Events-Rule.html) to capture the `UpdateTable` calls made by autoscaling (when setting up the trail, ensure it is monitoring "Write" Management Events)

* Grab the latest Lambda function zip from [Releases](https://github.com/Signiant/dynamodb-autoscaling-to-slack/releases)
* Create a new cloudformation stack using the template in the cfn folder

The stack asks for the function zip file location in S3, the slack API Key and the slack channel to post notifications to. Once the stack is created, a cloudwatch event is created to subscribe the lambda function to the `UpdateTable` dynamodb call when it comes from `application-autoscaling.amazonaws.com`.
