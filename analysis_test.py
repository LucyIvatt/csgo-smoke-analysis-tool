import unittest
from analysis import Doorway, Smoke


class TestSmokeCoverage(unittest.TestCase):
    """Tests the doorway/smoke coverage cases as shown in 5.5.3 calculating coverage
    """
    @staticmethod
    def setup(s, d1, d2):
        """Creates a test smoke and test doorway and sets their coordinates as required by the specific test.
        All other parameters for the constructor are set to dummy values (None or "Test")
        """
        smoke = Smoke(x=s[0],
                      y=s[1],
                      z=0,

                      demo_id=None,
                      thrower=None,
                      team=None,
                      side=None,
                      round_num=None,
                      time_thrown=None,
                      round_won=None)

        doorway = Doorway(name="Test",
                          x1=d1[0],
                          y1=d1[1],
                          x2=d2[0],
                          y2=d2[1],
                          z=0,
                          adjust_pw=False)

        smoke.doorway = doorway
        smoke.calculate_coverage()
        return smoke

    def test_case1_fully_covered(self):
        """Case1: Tests the case where the doorway completely inside of the smoke
        """
        s = (200, 200, 0)
        d1 = (125, 250)
        d2 = (275, 150)
        smoke = self.setup(s, d1, d2)
        self.assertEqual(smoke.coverage, 100)

    def test_case2_no_collision(self):
        """Case 2: Test the case where the doorway is completely outside of the smoke.
        Line would NOT intersect the circle at any point if it was extended to infinity
        """
        s = (200, 200, 0)
        d1 = (150, 10)
        d2 = (400, 110)
        smoke = self.setup(s, d1, d2)
        self.assertEqual(smoke.coverage, 0)

    def test_case3_no_collision_unless_extended(self):
        """Case 3: Test the case where the doorway is completely outside of the smoke.
        Line WOULD intersect the circle if it was extended to infinity
        """
        s = (200, 200, 0)
        d1 = (100, 300)
        d2 = (25, 400)
        smoke = self.setup(s, d1, d2)
        self.assertEqual(smoke.coverage, 0)

    def test_case4_tangent(self):
        """Case 4: Doorway is at a tangent to the smoke
        """
        s = (200, 200, 0)
        d1 = (50, 72)
        d2 = (350, 72)
        smoke = self.setup(s, d1, d2)
        self.assertEqual(smoke.coverage, 0)

    def test_case5_collision_double_gap(self):
        """Case 5: The doorway collides with the smoke. There are gaps on either side of the smoke i.e. neither
        of the doorway coordinates are within the smoke.

        Assertion value calculated by drawing out the case and manually measuring the coverage
        [8cm Coverage, 10.7cm Doorway] - 2% error allowed.
        """
        s = (200, 200, 0)
        d1 = (75, 280)
        d2 = (300, 310)
        smoke = self.setup(s, d1, d2)

        doorway_measured_length = 10.7
        coverage_measured_length = 8
        measured_coverage = (coverage_measured_length / doorway_measured_length)*100
        self.assertAlmostEqual(smoke.coverage, measured_coverage, delta=2)

    def test_case6_collision_single_gap(self):
        """Case 6: The doorway collides with the smoke. There is one gap on the side of the smoke and one doorway
        coordinate within the smoke.

        Assertion value calculated by drawing out the case and measuring the coverage
        [8.65cm Coverage, 14cm Doorway] - 2% error allowed.
        """
        s = (200, 200, 0)
        d1 = (200, 200)
        d2 = (400, 250)
        smoke = self.setup(s, d1, d2)

        doorway_measured_length = 14
        coverage_measured_length = 8.65
        measured_coverage = (coverage_measured_length / doorway_measured_length)*100
        self.assertAlmostEqual(smoke.coverage, measured_coverage, delta=2)


if __name__ == '__main__':
    unittest.main()
