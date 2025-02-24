class Rank:
    """A class object to store and manage ranking information"""

    def __init__(self, count=0, last_called=None, lowest=1000000, highest=0, doubles=0,
                 singles=0, six_nine=0, four_twenty=0, boob=0, pie=0, samsies=0):
        self.count = count
        self.last_called = last_called
        self.lowest = lowest
        self.highest = highest
        self.doubles = doubles
        self.singles = singles
        self.six_nine = six_nine
        self.four_twenty = four_twenty
        self.boob = boob
        self.pie = pie
        self.samsies = samsies

    def get_data(self):
        all_data = {
            "count": self.count,
            "last_called": self.last_called,
            "lowest": self.lowest,
            "highest": self.highest,
            "doubles": self.doubles,
            "singles": self.singles,
            "six_nine": self.six_nine,
            "four_twenty": self.four_twenty,
            "boob": self.boob,
            "pie": self.pie,
            "samsies": self.samsies
        }
        return all_data
