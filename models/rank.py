class Rank:
    """A class object to store and manage ranking information"""

    def __init__(self, count, last_called, lowest, highest, doubles, singles, six_nine, four_twenty, boob, pie):
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
            "pie": self.pie
        }
        return all_data
