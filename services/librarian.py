from aws import Dynamo


def create_instance(config, credentials):
    return Dynamo(table=config['TableName'], endpoint=config['Endpoint'], region=config['Region'],
                         access=credentials['Access'], secret=credentials['Secret'])

class Librarian:
    """
    Utility Service Class featuring static methods to consolidate DynamoDB interactions into one class rather than
    spread out across various components.
    """

    @staticmethod
    def get_roster(channel_id, config, credentials):
        pass

    @staticmethod
    def put_roster(channel_id, data, config, credentials):
        pass

    @staticmethod
    def get_rank(user_id, config, credentials):
        pass

    @staticmethod
    def put_rank(user_id, data, config, credentials):
        pass

    @staticmethod
    def get_default(user_id, config, credentials):
        pass

    @staticmethod
    def put_default(user_id, default,config, credentials):
        pass

    @staticmethod
    def get_count(user_id, config, credentials):
        pass

    @staticmethod
    def put_count(user_id, data, config, credentials):
        pass

    @staticmethod
    def get_progs(config, credentials):
        db_instance = create_instance(config, credentials)
        query = {'key': {'S': 'progs'}}
        data = db_instance.get(query)
        if data is not None and 'Item' in data:
            return data['Item']
        else:
            return None

    @staticmethod
    def put_progs(data, config, credentials):
        db_instance = create_instance(config, credentials)
        item = {
            'key': {'S': 'progs'},
            'data': {'M': data}
        }
        db_instance.put(item)


    @staticmethod
    def get_role_channel(config, credentials):
        pass

    @staticmethod
    def put_role_chanel(data, config, credentials):
        pass