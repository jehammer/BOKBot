from aws import Dynamo


def create_instance(table_config, credentials):
    return Dynamo(table=table_config['TableName'], endpoint=table_config['Endpoint'], region=table_config['Region'],
                         access=credentials['Access'], secret=credentials['Secret'])

class Librarian:
    """
    Utility Service Class featuring static methods to consolidate DynamoDB interactions into one class rather than
    spread out across various components.
    """

    @staticmethod
    def get_roster(channel_id, table_config, credentials):
        pass

    @staticmethod
    def put_roster(channel_id, data, table_config, credentials):
        pass

    @staticmethod
    def get_rank(user_id, table_config, credentials):
        pass

    @staticmethod
    def put_rank(user_id, data, table_config, credentials):
        pass

    @staticmethod
    def get_default(user_id, table_config, credentials):
        pass

    @staticmethod
    def put_default(user_id, default,table_config, credentials):
        pass

    @staticmethod
    def get_count(user_id, table_config, credentials):
        pass

    @staticmethod
    def put_count(user_id, data, table_config, credentials):
        pass

    @staticmethod
    def get_progs(table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'key': {'S': 'progs'}}
        data = db_instance.get(query)
        if data is not None and 'Item' in data:
            return data['Item']
        else:
            return None

    @staticmethod
    def put_progs(data, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        item = {
            'key': {'S': 'progs'},
            'data': {'M': data}
        }
        db_instance.put(item)


    @staticmethod
    def get_role_channel(table_config, credentials):
        pass

    @staticmethod
    def put_role_chanel(data, table_config, credentials):
        pass