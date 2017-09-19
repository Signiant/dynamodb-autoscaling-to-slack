import json
import sys,os
from slacker import Slacker

def send_to_slack(message,channel,key):
    status = True
    print "sending slack message " + message
    emoji=":dynamodb-autoscaling:"

    if not channel.startswith( '#' ):
        channel = '#' + channel

    slack = Slacker(key)
    slack.chat.post_message(
        channel=channel,
        text=message,
        as_user="false",
        username="DynamoDB Notifier",
        icon_emoji=emoji)

    return status

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
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

            region=event['region']
            event_name=event['detail']['eventName']
            table_name = event['detail']['requestParameters']['tableName']

            if 'globalSecondaryIndexUpdates' in event['detail']['requestParameters']:
                # We are updating an index - find out which one
                # It looks like Autoscale only updates one index per event hence the [0]
                update_type="index"
                index_name_update=event['detail']['requestParameters']['globalSecondaryIndexUpdates'][0]['update']['indexName']
                new_read_tput=event['detail']['requestParameters']['globalSecondaryIndexUpdates'][0]['update']['provisionedThroughput']['readCapacityUnits']
                new_write_tput=event['detail']['requestParameters']['globalSecondaryIndexUpdates'][0]['update']['provisionedThroughput']['writeCapacityUnits']

                # Now we need to get the current tput which is in an array in the response
                # unlike the requestParameters, the responseElements contains all indexes...
                for gsi in event['detail']['responseElements']['tableDescription']['globalSecondaryIndexes']:
                    print "Found GSI: " + gsi['indexName']
                    if gsi['indexName'] == index_name_update:
                        current_read_tput=gsi['provisionedThroughput']['readCapacityUnits']
                        current_write_tput=gsi['provisionedThroughput']['writeCapacityUnits']
            else:
                # It's a table update
                update_type="table"
                new_read_tput = event['detail']['requestParameters']['provisionedThroughput']['readCapacityUnits']
                new_write_tput = event['detail']['requestParameters']['provisionedThroughput']['writeCapacityUnits']

                table_status = event['detail']['responseElements']['tableDescription']['tableStatus']
                current_read_tput=event['detail']['responseElements']['tableDescription']['provisionedThroughput']['readCapacityUnits']
                current_write_tput=event['detail']['responseElements']['tableDescription']['provisionedThroughput']['writeCapacityUnits']

            # even indexes have the updateTable event name.
            if event_name == "UpdateTable":
                if new_read_tput > current_read_tput:
                    action="increasing"
                    operation="read"
                    current_tput=current_read_tput
                    new_tput=new_read_tput
                elif new_read_tput < current_read_tput:
                    action="decreasing"
                    operation="read"
                    current_tput=current_read_tput
                    new_tput=new_read_tput
                elif new_write_tput > current_write_tput:
                    action="increasing"
                    operation="write"
                    current_tput=current_write_tput
                    new_tput=new_write_tput
                elif new_write_tput < current_write_tput:
                    action="decreasing"
                    operation="write"
                    current_tput=current_write_tput
                    new_tput=new_write_tput
                else:
                    message = "DynamoDB autoscaling is performing an unknown action for table *" + table_name + "*"
                    print "Unknown action detected - raw event follows"
                    print("Received event: " + json.dumps(event, indent=2))

                if update_type == "table":
                    message = "Autoscaling (" + region + ") is `" + action + "` provisioned " + operation + " from " + str(current_tput) + " to " + str(new_tput) + " for table *" + table_name + "*"
                elif update_type == "index":
                    message = "Autoscaling (" + region + ") is `" + action + "` provisioned " + operation + " from " + str(current_tput) + " to " + str(new_tput) + " for index *" + index_name_update + "* on table *" + table_name + "*"
                else:
                    message = "Unknown update operation"
                status = send_to_slack(message,slack_channel,slack_api_token)
        else:
            print "Event has no responseElements - ignoring"

    return status
