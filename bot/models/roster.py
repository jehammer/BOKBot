class Roster:
    """Class for handling roster and related information"""

    def __init__(self, trial, date, leader, dps={}, healers={}, tanks={}, backup_dps={}, backup_healers={},
                 backup_tanks={}, dps_limit=0, healer_limit=0, tank_limit=0, role_limit=0, memo="delete", pingable="None"):
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
        self.pingable = pingable

    def get_roster_data(self):
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
            "memo": self.memo,
            "pingable": self.pingable
        }
        return all_data

    # Add people into the right spots
    # True for Main, False of Backup
    def add_dps(self, user_id, msg=""):
        if len(self.dps) < self.dps_limit:
            self.dps[user_id] = msg
            return True
        else:
            self.backup_dps[user_id] = msg
            return False

    def add_healer(self, user_id, msg=""):
        if len(self.healers) < self.healer_limit:
            self.healers[user_id] = msg
            return True
        else:
            self.backup_healers[user_id] = msg
            return False

    def add_tank(self, user_id, msg=""):
        if len(self.tanks) < self.tank_limit:
            self.tanks[user_id] = msg
            return True
        else:
            self.backup_tanks[user_id] = msg
            return False

    def add_backup_dps(self, user_id, msg=""):
        self.backup_dps[user_id] = msg
        return False

    def add_backup_healer(self, user_id, msg=""):
        self.backup_healers[user_id] = msg
        return False

    def add_backup_tank(self, user_id, msg=""):
        self.backup_tanks[user_id] = msg
        return False

    # remove people from right spots
    def remove_dps(self, user_id):
        if user_id in self.dps:
            del self.dps[user_id]
        else:
            del self.backup_dps[user_id]

    def remove_healer(self, user_id):
        if user_id in self.healers:
            del self.healers[user_id]
        else:
            del self.backup_healers[user_id]

    def remove_tank(self, user_id):
        if user_id in self.tanks:
            del self.tanks[user_id]
        else:
            del self.backup_tanks[user_id]

    def remove_member(self, user_id, need_vals=False):
        check = True  # If True, user was found and removed. If False, they were not found in the roster.
        og_msg = ''
        slotted = ''
        user_id = str(user_id)
        if user_id in self.dps.keys():
            og_msg = self.dps.get(user_id)
            slotted = 'dps'
            self.remove_dps(user_id)

        elif user_id in self.backup_dps.keys():
            og_msg = self.backup_dps.get(user_id)
            self.remove_dps(user_id)
            slotted = 'dps'

        elif user_id in self.healers.keys():
            og_msg = self.healers.get(user_id)
            self.remove_healer(user_id)
            slotted = 'healer'

        elif user_id in self.backup_healers.keys():
            og_msg = self.backup_healers.get(user_id)
            self.remove_healer(user_id)
            slotted = 'healer'

        elif user_id in self.tanks.keys():
            og_msg = self.tanks.get(user_id)
            self.remove_tank(user_id)
            slotted = 'tank'

        elif user_id in self.backup_tanks.keys():
            og_msg = self.backup_tanks.get(user_id)
            self.remove_tank(user_id)
            slotted = 'tank'
        else:
            check = False

        # need_vals is true: add_member called this function so return og_msg and slotted, otherwise if found or not.
        if need_vals:
            return og_msg, slotted
        return check

    def add_member(self, user_id, role, which, msg=''):
        check = None
        user_id = str(user_id)
        og_msg, slotted = self.remove_member(user_id, need_vals=True)

        if slotted == role:  # If they are swapping to the same role, copy the message between rosters.
            if msg == '' and og_msg != '':
                msg = og_msg

        # return code: 0 = added in slot, 1 = added in backup, 2 = unable to find role.

        if role == 'dps':
            if which == 'su':
                check = self.add_dps(user_id, msg)
            else:
                check = self.add_backup_dps(user_id, msg)
        elif role == 'tank':
            if which == 'su':
                check = self.add_tank(user_id, msg)
            else:
                check = self.add_backup_tank(user_id, msg)
        elif role == 'healer':
            if which == 'su':
                check = self.add_healer(user_id, msg)
            else:
                check = self.add_backup_healer(user_id, msg)
        else:
            return 2
        if check:
            return 0
        return 1

    def update_message(self, user_id, new_message):
        check = True
        if user_id in self.dps.keys():
            self.dps[user_id] = new_message

        elif user_id in self.backup_dps.keys():
            self.backup_dps[user_id] = new_message

        elif user_id in self.healers.keys():
            self.healers[user_id] = new_message

        elif user_id in self.backup_healers.keys():
            self.backup_healers[user_id] = new_message

        elif user_id in self.tanks.keys():
            self.tanks[user_id] = new_message

        elif user_id in self.backup_tanks.keys():
            self.backup_tanks[user_id] = new_message
        else:
            check = False

        return check

    def fill_spots(self):
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
            return True
        except Exception as e:
            logging.error(f"Fill Spots error: {str(e)}")
            return False

    def did_values_change(self, old_roster):
        for key, value in vars(self).items():
            if value != getattr(old_roster, key, None):
                return True
        return False
