# Script to setup local Docker DynamoDB
# Tables to make:
#   Defaults
#   Rosters
#   Ranks
#   Misc
#   Count

import boto3
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('../log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")



ddb_local_endpoint = 'http://localhost:8000'
region = 'us-east-2'
access_key = 'dummy'
secret_key = 'dummy'
dynamodb = boto3.client('dynamodb', endpoint_url=ddb_local_endpoint,
                        region_name=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)

def setup_misc_table():
    table_name = 'Misc'
    key_schema = [
        {
            'AttributeName': 'key',
            'KeyType': 'HASH'
        }
    ]
    attribute_definitions = [
        {
            'AttributeName': 'key',
            'AttributeType': 'S'
        }
    ]
    provisioned_throughput = {
        'ReadCapacityUnits': 2,
        'WriteCapacityUnits': 2
    }
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )
        logging.info(f"Misc Table status: {response['TableDescription']['TableStatus']}")
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Misc Table already exists.")
    except Exception as e:
        logging.error(f"Misc Table setup error: {str(e)}")



def setup_trial_table():
    table_name = 'Trial'
    key_schema = [
        {
            'AttributeName': 'channelID',
            'KeyType': 'HASH'
        }
    ]
    attribute_definitions = [
        {
            'AttributeName': 'channelID',
            'AttributeType': 'S'
        }
    ]
    provisioned_throughput = {
        'ReadCapacityUnits': 2,
        'WriteCapacityUnits': 2
    }
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput
        )
        logging.info(f"Trial Table status: {response['TableDescription']['TableStatus']}")
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Trial Table already exists.")
    except Exception as e:
        logging.error(f"Trial Table setup error: {str(e)}")

def main():
    setup_misc_table()
    setup_trial_table()


main()