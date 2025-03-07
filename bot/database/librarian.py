from bot.aws import Dynamo
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from bot.models import Roster, Count, Rank


def create_instance(table_config, credentials):
    return Dynamo(table=table_config['TableName'], endpoint=table_config['Endpoint'], region=table_config['Region'],
                  access=credentials['Access'], secret=credentials['Secret'])


def serialize(data):
    serializer = TypeSerializer()
    if isinstance(data, dict):
        serialized = {k: serializer.serialize(v) for k, v in data.items()}
    elif isinstance(data, list):
        serialized = [serializer.serialize(item) for item in data]
    else:
        serialized = serializer.serialize(data)
    return serialized


def deserialize(data):
    deserializer = TypeDeserializer()
    if isinstance(data, dict):
        deserialized = {k: deserializer.deserialize(v) for k, v in data.items()}
    elif isinstance(data, list):
        deserialized = [deserializer.deserialize(item) for item in data]
    else:
        deserialized = deserializer.deserialize(data)
    return deserialized


class Librarian:
    """
    Utility Service Class featuring static methods to consolidate DynamoDB interactions into one class rather than
    spread out across various components.
    """

    @staticmethod
    def get_all_rosters(table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        db_data = db_instance.scan_get_all()
        if db_data is None:
            return None

        all_rosters = {}
        for i in db_data:
            deserial = deserialize(i)
            data = deserial['data']
            channel_id = deserial['channelID']
            all_rosters[int(channel_id)] = Roster(data['trial'], data['date'], data['leader'], data['dps'],
                                                  data['healers'], data['tanks'],
                                                  data['backup_dps'], data['backup_healers'], data['backup_tanks'],
                                                  int(data['dps_limit']),
                                                  int(data['healer_limit']),
                                                  int(data['tank_limit']), int(data['role_limit']), data['memo'], data['pingable'])
        return all_rosters

    @staticmethod
    def get_roster(channel_id, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'channelID': {'S': str(channel_id)}}
        db_data = db_instance.get(query)
        if db_data is not None and 'Item' in db_data:
            data = deserialize(db_data['Item'])['data']
            return Roster(data['trial'], data['date'], data['leader'], data['dps'], data['healers'], data['tanks'],
                          data['backup_dps'], data['backup_healers'], data['backup_tanks'], int(data['dps_limit']),
                          int(data['healer_limit']),
                          int(data['tank_limit']), int(data['role_limit']), data['memo'], data['pingable'])
        else:
            return None

    @staticmethod
    def put_roster(channel_id, data, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        item = {
            'channelID': {'S': str(channel_id)},
            'data': {'M': serialize(data)}
        }
        db_instance.put(item)

    @staticmethod
    def delete_roster(channel_id, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'channelID': {'S': str(channel_id)}}
        db_instance.delete(query)

    @staticmethod
    def get_default(user_id, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'userID': {'S': str(user_id)}}
        db_data = db_instance.get(query)
        if db_data is not None and 'Item' in db_data:
            return deserialize(db_data['Item'])['default']
        else:
            return None

    @staticmethod
    def put_default(user_id, default, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        item = {
            'userID': {'S': str(user_id)},
            'default': {'S': default}
        }
        db_instance.put(item)
        return

    @staticmethod
    def get_count(user_id, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'userID': {'S': str(user_id)}}
        db_data = db_instance.get(query)
        if db_data is not None and 'Item' in db_data:
            data = deserialize(db_data['Item'])['data']
            return Count(runs=int(data['count']), trial=data['lastTrial'], date=data['lastDate'], dps=int(data['dpsRuns']),
                         tank=int(data['tankRuns']), healer=int(data['healerRuns']))
        else:
            return None

    @staticmethod
    def put_count(user_id, count, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        data = count.get_count_data()
        item = {
            'userID': {'S': str(user_id)},
            'data': {'M': serialize(data)}
        }
        db_instance.put(item)
        return

    @staticmethod
    def get_progs(table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'key': {'S': 'progs'}}
        db_data = db_instance.get(query)
        if db_data is not None and 'Item' in db_data:
            return deserialize(db_data['Item'])['data']
        else:
            return None

    @staticmethod
    def put_progs(data, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        item = {
            'key': {'S': 'progs'},
            'data': {'L': serialize(data)}
        }
        db_instance.put(item)
        return

    @staticmethod
    def get_rank(user_id, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        query = {'userID': {'S': str(user_id)}}
        db_data = db_instance.get(query)
        if db_data is not None and 'Item' in db_data:
            data = deserialize(db_data['Item'])['data']
            return Rank(count=int(data['count']), last_called=data['last_called'], lowest=int(data['lowest']), highest=int(data['highest']),
                        doubles=int(data['doubles']), singles=int(data['singles']), six_nine=int(data['six_nine']),
                        four_twenty=int(data['four_twenty']), boob=int(data['boob']), pie=int(data['pie']), samsies=int(data['samsies']))
        else:
            return None

    @staticmethod
    def put_rank(user_id, rank_data: Rank, table_config, credentials):
        db_instance = create_instance(table_config, credentials)
        data = rank_data.get_data()
        item = {
            'userID': {'S': str(user_id)},
            'data': {'M': serialize(data)}
        }
        db_instance.put(item)
        return

    @staticmethod
    def get_role_channel(table_config, credentials):
        pass

    @staticmethod
    def put_role_channel(data, table_config, credentials):
        pass
