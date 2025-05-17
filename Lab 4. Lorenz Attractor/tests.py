import unittest
import numpy as np
from main import lorenz_equation, solve_lorenz

class TestLorenzSystem(unittest.TestCase):

    def test_lorenz_equation_output(self):
        vector = [1.0, 1.0, 1.0]
        t = 0.0
        sigma = 10.0
        beta = 8.0 / 3.0
        rho = 28.0

        result = lorenz_equation(vector, t, sigma, beta, rho)

        expected = [
            sigma * (1.0 - 1.0),
            rho * 1.0 - 1.0 - 1.0 * 1.0,
            1.0 * 1.0 - beta * 1.0
        ]

        self.assertAlmostEqual(result[0], expected[0])
        self.assertAlmostEqual(result[1], expected[1])
        self.assertAlmostEqual(result[2], expected[2])

    def test_solve_lorenz_shape(self):
        position_0 = [0.0, 1.0, 1.0]
        time_points = np.linspace(0, 10, 500)
        sigma = 10.0
        beta = 8.0 / 3.0
        rho = 28.0

        result = solve_lorenz(position_0, time_points, sigma, beta, rho)

        self.assertEqual(result.shape, (500, 3))

    def test_zero_initial_conditions(self):
        position_0 = [0.0, 0.0, 0.0]
        time_points = np.linspace(0, 1, 10)
        sigma = 10.0
        beta = 8.0 / 3.0
        rho = 28.0

        result = solve_lorenz(position_0, time_points, sigma, beta, rho)

        np.testing.assert_array_almost_equal(result, np.zeros((10, 3)))

    def test_sensitivity_to_parameters(self):
        position_0 = [0.0, 1.0, 1.0]
        time_points = np.linspace(0, 10, 1000)

        sigma = 10.0
        beta = 8.0 / 3.0
        rho = 28.0

        result1 = solve_lorenz(position_0, time_points, sigma, beta, rho)

        sigma = 12.0
        result2 = solve_lorenz(position_0, time_points, sigma, beta, rho)

        self.assertFalse(np.array_equal(result1, result2))

if __name__ == '__main__':
    unittest.main()
