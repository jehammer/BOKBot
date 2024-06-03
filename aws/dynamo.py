import boto3
import logging
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class Dynamo:
    def __init__(self, table, endpoint, region, access, secret):
        self.table_name = table
        self.client = boto3.client('dynamodb', endpoint_url=endpoint,
                                   region_name=region, aws_access_key_id=access, aws_secret_access_key=secret)

    def get(self, query):
        """Fetch an item based on the defined query."""
        try:
            response = self.client.get_item(TableName=self.table_name, Key=query)
            return response
        except ClientError as e:
            logging.error(f"Dynamo Get Item Error Table: %s, error: %s: %s",
                self.table.name,
                e.response['Error']['Code'],
                e.response['Error']['Message'],
            )
            raise e

    def put(self, data):
        """Put new entry into the database using the defined data parameter."""
        try:
            self.client.put_item(TableName=self.table_name, Item=data)
        except ClientError as e:
            logging.error(f"Dynamo Put Item Error Table: %s, error: %s: %s",
                self.table.name,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
            raise e

    def update(self, query, data):
        """Update an item found from the passed in query and data to update."""
        try:
            update = "set "
            update_vals = {}
            for key, value in data:
                update += f":{key} =:{key}, "
                update_vals[f"{key}"] = value
            expression = update[:-2] # NOTE: Need to remove trailing space and comma included in for-loop
            response = self.client.update_item(
                TableName=self.table_name,
                Key=query,
                UpdateExpression=expression,
                ExpressionAttributeValues=update_vals,
                ReturnValues="UPDATED_NEW"
            )
        except ClientError as e:
            logging.error(f"Dynamo Update Item Error Table: %s, error: %s: %s",
                self.table.name,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )
        else:
            return response["Attributes"]

    def batch_get(self, query):
        """Gets a batch of items from the db based upon the query"""
        pass
        # TODO: Implement a batch_get, useful for getting all counts to be increased in a roster.

    def batch_put(self, data):
        """Put a batch of items into the db"""
        pass
        #TODO: Implement a batch_put for mass data update, since we charge based upon total write requests