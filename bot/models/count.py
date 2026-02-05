class Count:
    """Class to manage Count information for Run History"""

    def __init__(
        self,
        runs=None,
        trial=None,
        date=None,
        dps=None,
        tank=None,
        healer=None,
        event=None,
    ):
        self.count = runs if runs is not None else 0
        self.lastTrial = trial if trial is not None else "None"
        self.lastDate = date if date is not None else "<t:0:f>"
        self.dpsRuns = dps if dps is not None else 0
        self.tankRuns = tank if tank is not None else 0
        self.healerRuns = healer if healer is not None else 0
        self.eventRuns = event if event is not None else 0

    def get_count_data(self):
        """Return Object of Count Data for DB"""
        all_data = {
            "count": self.count,
            "lastTrial": self.lastTrial,
            "lastDate": self.lastDate,
            "dpsRuns": self.dpsRuns,
            "tankRuns": self.tankRuns,
            "healerRuns": self.healerRuns,
            "eventRuns": self.eventRuns,
        }

        return all_data

    def increase_data(
        self, runs=0, trial=None, date=None, dps=0, tank=0, healer=0, event=0
    ):
        self.count += runs
        self.lastTrial = trial if trial is not None else "None"
        self.lastDate = date if date is not None else "<t:0:f>"
        self.dpsRuns += dps
        self.tankRuns += tank
        self.healerRuns += healer
        self.eventRuns += event

    def decrease_data(
        self, runs=0, trial=None, date=None, dps=0, tank=0, healer=0, event=0
    ):
        self.count -= runs
        self.lastTrial = trial if trial is not None else "None"
        self.lastDate = date if date is not None else "<t:0:f>"
        self.dpsRuns -= dps
        self.tankRuns -= tank
        self.healerRuns -= healer
        self.eventRuns -= event
