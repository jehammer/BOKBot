from aws import Dynamo
class SchemaSetup:
    """Class for making local DynamoDB Schema. Local development and Test uses only."""

    @staticmethod
    def roster_db_schema(dynamo:Dynamo, table_name):
        schema = {
            'TableName': table_name,
            'KeySchema': [
                {
                    'AttributeName': 'channelID',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            'AttributeDefinitions': [
                {
                    'AttributeName': 'channelID',
                    'AttributeType': 'S'  # String type
                },
                {
                    'AttributeName': 'data',
                    'AttributeType': 'M'  # Map type
                }
            ],
            'ProvisionedThroughput': {
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        }
        table = dynamo.create(schema)
        return table