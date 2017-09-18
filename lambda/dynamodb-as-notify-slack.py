import json
import sys,os
from slacker import Slacker

def send_to_slack(message,channel,key):
    status = True
    print "sending slack message " + message
    emoji=":dynamodb-autoscaling:"

    slack = Slacker(key)
    slack.chat.post_message(
        channel='#' + channel,
        text=message,
        as_user="false",
        username="DynamoDB Notifier",
        icon_emoji=emoji)

    return status

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    status=True

    if 'slack_api_token' in os.environ:
        slack_api_token=os.environ['slack_api_token']
    else:
        print("FATAL: No slack api token set in the slack_api_token environment variable")
        status=False

    if 'slack_channel' in os.environ:
        slack_channel=os.environ['slack_channel']
    else:
        print("FATAL: No slack channel set in the slack_channel environment variable")
        status=False

    if status:
        if event['detail']['responseElements']:
            print("Event has a response - reading elements")

            event_name=event['detail']['eventName']
            table_name = event['detail']['requestParameters']['tableName']
            new_read_tput = event['detail']['requestParameters']['provisionedThroughput']['readCapacityUnits']
            new_write_tput = event['detail']['requestParameters']['provisionedThroughput']['writeCapacityUnits']

            table_status = event['detail']['responseElements']['tableDescription']['tableStatus']
            current_read_tput=event['detail']['responseElements']['tableDescription']['provisionedThroughput']['readCapacityUnits']
            current_write_tput=event['detail']['responseElements']['tableDescription']['provisionedThroughput']['writeCapacityUnits']

            if event_name == "UpdateTable":
                if new_read_tput > current_read_tput:
                    message = "DynamoDB autoscaling is `increasing` provisioned read throughput from " + str(current_read_tput) + " to " + str(new_read_tput) + " for table *" + table_name + "*"
                elif new_read_tput < current_read_tput:
                    message = "DynamoDB autoscaling is `decreasing` provisioned read throughput from " + str(current_read_tput) + " to " + str(new_read_tput) + " for table *" + table_name + "*"
                elif new_write_tput > current_write_tput:
                    message = "DynamoDB autoscaling is `increasing` provisioned write throughput from " + str(current_write_tput) + " to " + str(new_write_tput) + " for table *" + table_name + "*"
                elif new_write_tput > current_write_tput:
                    message = "DynamoDB autoscaling is `decreasing` provisioned write throughput from " + str(current_write_tput) + " to " + str(new_write_tput) + " for table *" + table_name + "*"
                else:
                    message = "DynamoDB autoscaling is performing an unknown action for table *" + table_name + "*"

                status = send_to_slack(message,slack_channel,slack_api_token)
        else:
            print "Event has no responseElements - ignoring"

    return status
