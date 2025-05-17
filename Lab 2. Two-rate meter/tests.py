import unittest
from db import Database
import datetime

class TestMeterDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.today = datetime.date.today().isoformat()

        self.db.update_tariffs(4.0, 2.0, 100, 80)

        self.db.save_meter("0001", 100, 100, self.today)

    def test_update_existing_meter(self):
        self.db.save_meter("0001", 150, 160, self.today)
        meter = self.db.get_meter("0001")
        self.assertEqual(meter[1], 150)
        self.assertEqual(meter[2], 160)

    def test_add_new_meter(self):
        self.db.save_meter("0002", 200, 250, self.today)
        meter = self.db.get_meter("0002")
        self.assertEqual(meter[1], 200)
        self.assertEqual(meter[2], 250)

    def test_night_usage_underreported(self):
        self.db.save_meter("0002", 150, 50, self.today)
        old = self.db.get_meter("0001")
        new = self.db.get_meter("0002")

        used_day = new[1] - old[1]
        used_night = new[2] - old[2]

        if used_night < 0:
            used_night = self.db.get_tariffs()[3]

        self.db.add_history("0002", self.today, 4.0, 2.0, used_day, used_night, used_day * 4.0 + used_night * 2.0)

        history = self.db.get_history()
        self.assertEqual(history[0][6], used_night)

    def test_day_usage_underreported(self):
        self.db.save_meter("0002", 50, 150, self.today)
        old = self.db.get_meter("0001")
        new = self.db.get_meter("0002")

        used_day = new[1] - old[1]
        used_night = new[2] - old[2]

        if used_day < 0:
            used_day = self.db.get_tariffs()[2]  # fake_day

        self.db.add_history("0002", self.today, 4.0, 2.0, used_day, used_night, used_day * 4.0 + used_night * 2.0)

        history = self.db.get_history()
        self.assertEqual(history[0][5], used_day)  # used_day

    def test_day_and_night_usage_underreported(self):
        self.db.save_meter("0002", 90, 90, self.today)
        old = self.db.get_meter("0001")
        new = self.db.get_meter("0002")

        used_day = new[1] - old[1]
        used_night = new[2] - old[2]

        tariffs = self.db.get_tariffs()
        if used_day < 0:
            used_day = tariffs[2]  # fake_day
        if used_night < 0:
            used_night = tariffs[3]  # fake_night

        bill = round(used_day * tariffs[0] + used_night * tariffs[1], 2)

        self.db.add_history("0002", self.today, tariffs[0], tariffs[1], used_day, used_night, bill)

        history = self.db.get_history()
        self.assertEqual(history[0][5], used_day)
        self.assertEqual(history[0][6], used_night)
        self.assertEqual(history[0][7], bill)

if __name__ == '__main__':
    unittest.main()
