from pymongo import MongoClient
from bot.models import Roster, Count, Rank, EventRoster
import logging

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s: %(message)s',
    handlers=[
        logging.FileHandler('log.log', mode='a'),
        logging.StreamHandler()
    ])  # , datefmt="%Y-%m-%d %H:%M:%S")


class Librarian:

    def __init__(self, config_uri: str):

        self._client = MongoClient(config_uri)
        self._database = self._client["bot"]

    # Roster methods
    def get_all_rosters(self):
        db_data = self._database.raids.find()
        if db_data is None:
            return None

        all_rosters = {}
        for i in db_data:
            channel_id = i['channelID']
            if i['type'] == 'Trial':
                data = i['data']
                all_rosters[int(channel_id)] = Roster(
                    data['trial'], data['date'], data['leader'], data['dps'],
                    data['healers'], data['tanks'], data['backup_dps'],
                    data['backup_healers'], data['backup_tanks'],
                    int(data['dps_limit']), int(data['healer_limit']),
                    int(data['tank_limit']), int(data['role_limit']),
                    data['memo'], data['pingable']
                )
            elif i['type'] == 'Event':
                data = i['data']
                all_rosters[int(channel_id)] = EventRoster(event=data['event'], date=data['date'], leader=data['leader'],
                                                           memo=data['memo'], pingable=data['pingable'], members=data['members'])
        return all_rosters

    def get_roster(self, channel_id):
        query = {"channelID": str(channel_id)}
        db_data = self._database.raids.find_one(query)
        if db_data:
            data = db_data["data"]
            return Roster(
                data["trial"], data["date"], data["leader"], data["dps"],
                data["healers"], data["tanks"], data["backup_dps"],
                data["backup_healers"], data["backup_tanks"],
                int(data["dps_limit"]), int(data["healer_limit"]),
                int(data["tank_limit"]), int(data["role_limit"]),
                data["memo"], data["pingable"]
            )
        return None

    def put_roster(self, channel_id, data: Roster | EventRoster):
        roster_type = ''
        if isinstance(data, Roster):
            roster_type = 'Trial'
        elif isinstance(data, EventRoster):
            roster_type = 'Event'
            
        item = {
            "channelID": str(channel_id),
            'type': roster_type,
            "data": data.get_roster_data()
        }

        logging.info(f"Saving roster {roster_type} channel: {channel_id}")
        self._database.raids.replace_one(
            {"channelID": str(channel_id)},
            item,
            upsert=True
        )

    def delete_roster(self, channel_id):
        query = {"channelID": str(channel_id)}
        self._database.raids.delete_one(query)

    # Default settings
    def get_default(self, user_id):
        db_data = self._database.defaults.find_one({"userID": int(user_id)})
        return db_data["default"] if db_data else None

    def put_default(self, user_id, default):
        item = {
            "userID": int(user_id),
            "default": default
        }
        self._database.defaults.replace_one(
            {"userID": int(user_id)},
            item,
            upsert=True
        )

    def delete_default(self, user_id):
        query = {"userID": int(user_id)}
        self._database.defaults.delete_one(query)

    # Count tracking
    def get_count(self, user_id):
        db_data = self._database.count.find_one({"userID": int(user_id)})
        if db_data:
            data = db_data["data"]
            return Count(
                runs=int(data["count"]),
                trial=data["lastTrial"],
                date=data["lastDate"],
                dps=int(data["dpsRuns"]),
                tank=int(data["tankRuns"]),
                healer=int(data["healerRuns"])
            )
        return None

    def put_count(self, user_id, count):
        item = {
            "userID": int(user_id),
            "data": count.get_count_data()
        }
        self._database.count.replace_one(
            {"userID": int(user_id)},
            item,
            upsert=True
        )

    def delete_count(self, user_id):
        query = {"userID": int(user_id)}
        self._database.count.delete_one(query)

    # Progs
    def get_progs(self):
        db_data = self._database.misc.find_one({"key": "progs"})
        return db_data["data"] if db_data else None

    def put_progs(self, data):
        self._database.misc.replace_one(
            {"key": "progs"},
            {"key": "progs", "data": data},
            upsert=True
        )

    # Rank tracking
    def get_rank(self, user_id):
        db_data = self._database.ranks.find_one({"userID": int(user_id)})
        if db_data:
            data = db_data["data"]
            return Rank(
                count=int(data["count"]),
                last_called=data["last_called"],
                lowest=int(data["lowest"]),
                highest=int(data["highest"]),
                doubles=int(data["doubles"]),
                singles=int(data["singles"]),
                six_nine=int(data["six_nine"]),
                four_twenty=int(data["four_twenty"]),
                boob=int(data["boob"]),
                pie=int(data["pie"]),
                samsies=int(data["samsies"]),
                palindrome=int(data['palindrome']))
        return None

    def put_rank(self, user_id, rank_data: Rank):
        self._database.ranks.replace_one(
            {"userID": int(user_id)},
            {
                "userID": int(user_id),
                "data": rank_data.get_data()
            },
            upsert=True
        )

    def delete_rank(self, user_id):
        query = {"userID": int(user_id)}
        self._database.ranks.delete_one(query)

    # Role channel
    def get_role_channel(self, collection_name):
        pass

    def put_role_channel(self, data, collection_name):
        pass

    def close(self):
        self._client.close()


# Initialize the singleton with config passed in
def init_librarian(config_uri: str) -> Librarian:
    return Librarian(config_uri)
