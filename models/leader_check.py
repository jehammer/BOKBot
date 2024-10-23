from models import Roster


class LeaderCheck:
    """A class object to store and manage Raid Lead tracking information"""

    def __init__(self, user_id, last_ran, last_date, last_limit, total_runs=0):
        self.user_id = user_id
        self.last_ran = last_ran
        self.last_date = last_date
        self.last_limit = last_limit
        self.total_runs = total_runs

    def update(self, roster: Roster, runs):
        self.last_ran = roster.trial
        self.last_date = roster.date
        self.last_limit = roster.role_limit
        self.total_runs += runs

    def get_data(self):
        all_data = {
            "last_ran": self.last_ran,
            "last_date": self.last_date,
            "last_limit": self.last_limit,
            "total_runs": self.total_runs,
        }
        return all_data
