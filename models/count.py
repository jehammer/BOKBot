class Count:
    """Class to manage Count information for Run History"""

    def __init__(self, runs=None, trial=None, date=None, dps=None, tank=None, healer=None):
        self.count = runs if runs is not None else "0",
        self.lastTrial = trial if trial is not None else "None",
        self.lastDate = date if date is not None else "<t:0:f>",
        self.dpsRuns = dps if dps is not None else 0,
        self.tankRuns = tank if tank is not None else 0,
        self.healerRuns = healer if healer is not None else 0

    def getCountData(self):
        """Return Object of Count Data for DB"""
        all_data = {
            "count": self.count,
            "lastTrial": self.lastTrial,
            "lastDate": self.lastDate,
            "dpsRuns": self.dpsRuns,
            "tankRuns": self.tankRuns,
            "healerRuns": self.healerRuns
        }

        return all_data