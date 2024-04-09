class Roster:
    """Class for handling roster and related information"""

    def __init__(self, trial, date, leader, dps={}, healers={}, tanks={}, backup_dps={}, backup_healers={},
                 backup_tanks={}, dps_limit=0, healer_limit=0, tank_limit=0, role_limit=0, memo="delete"):
        self.trial = trial
        self.date = date
        self.leader = leader
        self.dps = dps
        self.tanks = tanks
        self.healers = healers
        self.backup_dps = backup_dps
        self.backup_tanks = backup_tanks
        self.backup_healers = backup_healers
        self.dps_limit = dps_limit
        self.tank_limit = tank_limit
        self.healer_limit = healer_limit
        self.role_limit = role_limit
        self.memo = memo

    def get_roster_data(self): # TODO: review this for DynamoDB
        all_data = {
            "trial": self.trial,
            "date": self.date,
            "leader": self.leader,
            "dps": self.dps,
            "healers": self.healers,
            "tanks": self.tanks,
            "backup_dps": self.backup_dps,
            "backup_healers": self.backup_healers,
            "backup_tanks": self.backup_tanks,
            "dps_limit": self.dps_limit,
            "healer_limit": self.healer_limit,
            "tank_limit": self.tank_limit,
            "role_limit": self.role_limit,
            "memo": self.memo
        }
        return all_data

    # Add people into the right spots
    def add_dps(self, n_dps, p_class=""):
        if len(self.dps) < self.dps_limit:
            self.dps[n_dps] = p_class
            return "Added as DPS"
        else:
            self.backup_dps[n_dps] = p_class
            return "DPS spots full, slotted for Backup"

    def add_healer(self, n_healer, p_class=""):
        if len(self.healers) < self.healer_limit:
            self.healers[n_healer] = p_class
            return "Added as Healer"
        else:
            self.backup_healers[n_healer] = p_class
            return "Healer spots full, slotted for Backup"

    def add_tank(self, n_tank, p_class=""):
        if len(self.tanks) < self.tank_limit:
            self.tanks[n_tank] = p_class
            return "Added as Tank"
        else:
            self.backup_tanks[n_tank] = p_class
            return "Tank spots full, slotted for Backup"

    def add_backup_dps(self, n_dps, p_class=""):
        self.backup_dps[n_dps] = p_class
        return "Added for backup as DPS"

    def add_backup_healer(self, n_healer, p_class=""):
        self.backup_healers[n_healer] = p_class
        return "Added for backup as Healer"

    def add_backup_tank(self, n_tank, p_class=""):
        self.backup_tanks[n_tank] = p_class
        return "Added for backup as Tank"

    # remove people from right spots
    def remove_dps(self, n_dps):
        if n_dps in self.dps:
            del self.dps[n_dps]
        else:
            del self.backup_dps[n_dps]

    def remove_healer(self, n_healer):
        if n_healer in self.healers:
            del self.healers[n_healer]
        else:
            del self.backup_healers[n_healer]

    def remove_tank(self, n_tank):
        if n_tank in self.tanks:
            del self.tanks[n_tank]
        else:
            del self.backup_tanks[n_tank]

    def fill_spots(self, num):
        try:
            loop = True
            while loop:
                if len(self.dps) < self.dps_limit and len(self.backup_dps) > 0:
                    first = list(self.backup_dps.keys())[0]
                    self.dps[first] = self.backup_dps.get(first)
                    del self.backup_dps[first]
                else:
                    loop = False
            loop = True
            while loop:
                if len(self.healers) < self.healer_limit and len(self.backup_healers) > 0:
                    first = list(self.backup_healers.keys())[0]
                    self.healers[first] = self.backup_healers.get(first)
                    del self.backup_healers[first]
                else:
                    loop = False
            loop = True
            while loop:
                if len(self.tanks) < self.tank_limit and len(self.backup_tanks) > 0:
                    first = list(self.backup_tanks.keys())[0]
                    self.tanks[first] = self.backup_tanks.get(first)
                    del self.backup_tanks[first]
                else:
                    loop = False
            logging.info(f"Spots filled in roster id {str(num)}")
        except Exception as e:
            logging.error(f"Fill Spots error: {str(e)}")