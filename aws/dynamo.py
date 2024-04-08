import boto3
import logging
from botocore.exceptions import ClientError

class Dynamo:
    def __init__(self, table, endpoint):
        self.table_name = table
        self.resource = boto3.resource('dynamodb', endpoint=endpoint)
        self.table = self.dynamodb.Table(table)

    def create(self, schema):
        """Creates new table in DynamoDB given specified name and schema."""
        # NOTE: This is for testing mainly, as AWS resources will be provisioned through CloudFormation
        try:
            logging.info(f"Received request to create table {schema['TableName']} with schema {schema}")
            new_table = self.resource.create_table(**schema)
            new_table.wait_until_exists()
            return new_table
        except Exception as e:
            logging.error(f"Dynamo Create Table Error: {str(e)}")

    def get(self, query):
        """Fetch an item based on the defined query."""
        try:
            response = self.table.get_item(Key={query})
            return response
        except ClientError as e:
            logging.error(f"Dynamo Get Item Error Table: {self.table_name} error: {str(e)} ")

    def put(self, data):
        """Put new entry into the database using the defined data parameter."""
        try:
            self.table.put_item(Item=data)
        except ClientError as e:
            logging.error(f"Dynamo Put Item Error Table: %s, error: %s: %s",
                self.table.name,
                e.response["Error"]["Code"],
                e.response["Error"]["Message"],
            )

    def update(self, query, data):
        """Update an item found from the passed in query and data to update."""
        try:
            update = "set "
            update_vals = {}
            for key, value in data:
                update += f":{key} =:{key}, "
                update_vals[f"{key}"] = value
            expression = update[:-2] # NOTE: Need to remove trailing space and comma included in for-loop
            response = self.table.update_item(
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