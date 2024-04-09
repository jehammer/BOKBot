class Schema:
    """Handles creating Item Schema for individual DynamoDB Calls. Static Methods."""

    @staticmethod
    def generate_roster_schema(channel_id, roster):
        item = {
            "channelID": channel_id,
            "data": roster.get_roster_data()
        }
        return item

