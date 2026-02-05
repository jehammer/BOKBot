# Script to setup local Docker DynamoDB
# Tables to make:
#   Defaults
#   Rosters
#   Ranks
#   Misc
#   Count
#   Birthdays

import boto3
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(message)s",
    handlers=[logging.FileHandler("../log.log", mode="a"), logging.StreamHandler()],
)  # , datefmt="%Y-%m-%d %H:%M:%S")

ddb_local_endpoint = "http://localhost:8000"
region = "us-east-2"
access_key = "dummy"
secret_key = "dummy"
dynamodb = boto3.client(
    "dynamodb",
    endpoint_url=ddb_local_endpoint,
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
)


def setup_misc_table():
    table_name = "Misc"
    key_schema = [{"AttributeName": "key", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "key", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Misc Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Misc Table already exists.")
    except Exception as e:
        logging.error(f"Misc Table setup error: {str(e)}")


def setup_roster_table():
    table_name = "Rosters"
    key_schema = [{"AttributeName": "channelID", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "channelID", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Rosters Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Rosters Table already exists.")
    except Exception as e:
        logging.error(f"Rosters Table setup error: {str(e)}")


def setup_count_table():
    table_name = "Count"
    key_schema = [{"AttributeName": "userID", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "userID", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Count Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Count Table already exists.")
    except Exception as e:
        logging.error(f"Count Table setup error: {str(e)}")


def setup_default_table():
    table_name = "Defaults"
    key_schema = [{"AttributeName": "userID", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "userID", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Defaults Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Defaults Table already exists.")
    except Exception as e:
        logging.error(f"Defaults Table setup error: {str(e)}")


def setup_ranks_table():
    table_name = "Ranks"
    key_schema = [{"AttributeName": "userID", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "userID", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Ranks Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Ranks Table already exists.")
    except Exception as e:
        logging.error(f"Ranks Table setup error: {str(e)}")


def setup_birthdays_table():  # TODO: Revisit this, this is just a setup for now.
    table_name = "Birthdays"
    key_schema = [{"AttributeName": "userID", "KeyType": "HASH"}]
    attribute_definitions = [{"AttributeName": "userID", "AttributeType": "S"}]
    provisioned_throughput = {"ReadCapacityUnits": 2, "WriteCapacityUnits": 2}
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=key_schema,
            AttributeDefinitions=attribute_definitions,
            ProvisionedThroughput=provisioned_throughput,
        )
        logging.info(
            f"Birthdays Table status: {response['TableDescription']['TableStatus']}"
        )
    except dynamodb.exceptions.ResourceInUseException:
        logging.info(f"Birthdays Table already exists.")
    except Exception as e:
        logging.error(f"Birthdays Table setup error: {str(e)}")


def main():
    setup_misc_table()
    setup_roster_table()
    setup_count_table()
    setup_default_table()
    setup_ranks_table()
    setup_birthdays_table()


main()
