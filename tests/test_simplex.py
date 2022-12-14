import numpy as np
import numpy.testing as npt
import pytest
from auxiliar_lp import AuxiliarLP

from Utils.linear_algebra import LinearAlgebra
from exceptions import UnboundedError, UnfeasibleError
from simplex import Simplex
from pytest import input_test_data


class TestSimplex:

    # @pytest.mark.parametrize("entrada", input)
    def test_simplex_end_tableau(self):
        """
        Test if the linear programming was correctly solved
        """
        entrada = input_test_data[1]

        simplex = Simplex(entrada.M_variaveis, entrada.N_restricoes, entrada.FullTableau)
        end = simplex.solve()
        end_without_vero = LinearAlgebra.drop_vero(end)
        expected = entrada.EndTableau

        orderedColumns = np.sort(end_without_vero, axis=0)
        orderedExpected = np.sort(expected, axis=0)

        npt.assert_allclose(orderedColumns, orderedExpected)

    def test_simplex_end_solution(self):
        """
        Test if the linear programming solution is right
        """
        entrada = input_test_data[1]

        simplex = Simplex(entrada.M_variaveis, entrada.N_restricoes, entrada.FullTableau)
        end = simplex.solve()
        x_solution = LinearAlgebra.get_solution(end)

        expected = [3, 2, 0, 1, 0]

        npt.assert_allclose(x_solution, expected)

    def test_basic_tableau_pivoting(self):
        """
        Pivot the tableau to given pivot
        """
        baseTableau = np.array([
            [-2, -3, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 6],
            [2, 1, 0, 1, 0, 10],
            [-1, 1, 0, 0, 1, 4],
        ],
            dtype=float)

        # o 2, abaixo do c=-2, vai ser o pivo
        row = 2
        column = 0

        resultC = Simplex.pivotTableau(baseTableau, column, row)

        # largura 2m + n + 1
        expectedC = [
            [0, -2, 0, 1, 0, 10],
            [0, 0.5, 1, -0.5, 0, 1],
            [1, 0.5, 0, 0.5, 0, 5],
            [0, 1.5, 0, 0.5, 1, 9],
        ]

        npt.assert_allclose(resultC, expectedC)

    def test_cumulative_pivoting(self):
        """
        Pivot given tableau with two different pivots
        """
        baseTableau = np.array([
            [-2, -3, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 6],
            [2, 1, 0, 1, 0, 10],
            [-1, 1, 0, 0, 1, 4],
        ],
            dtype=float)

        # o 2, abaixo do c=-2, vai ser o pivo
        row = 2
        column = 0

        resultC = Simplex.pivotTableau(baseTableau, column, row)

        row_2 = 1
        column_2 = 1

        resultC = Simplex.pivotTableau(resultC, column_2, row_2)

        # largura 2m + n + 1
        expectedC = [
            [0, 0, 4, -1, 0, 14],
            [0, 1, 2, -1, 0, 2],
            [1, 0, -1, 1, 0, 4],
            [0, 0, -3, 2, 1, 6],
        ]

        npt.assert_allclose(resultC, expectedC)

    def test_canonical_form_creation(self):
        baseTableau = [
            [0, 0, 0, 0, 0, 1, 1, 1, 0],
            [1, 0, 0, 2, 1, 1, 0, 0, 8],
            [0, 1, 0, 1, 2, 0, 1, 0, 8],
            [0, 0, 1, 1, 1, 0, 0, 1, 5],
        ]

        baseColumns = [5, 6, 7]

        tableau = Simplex.putInCanonicalForm(np.array(baseTableau))

        expectedTableau = [
            [-1, -1, -1, -4, -4, 0, 0, 0, -21],
            [1, 0, 0, 2, 1, 1, 0, 0, 8],
            [0, 1, 0, 1, 2, 0, 1, 0, 8],
            [0, 0, 1, 1, 1, 0, 0, 1, 5],
        ]

        npt.assert_almost_equal(tableau, expectedTableau)

    def test_returns_is_unbounded(self):
        """
        Tableau with a column with negative values is unbounded
        """
        baseTableau = np.array([
            [-1, -1, -1, -4, -4, 0, 0, -1, -21],
            [1, 0, 0, 2, 1, 1, 0, -1, 8],
            [0, 1, 0, 1, 2, 0, 1, -1, 8],
            [0, 0, 1, 1, 1, 0, 0, -1, 5],
        ])

        result = Simplex.isUnbounded(baseTableau)

        npt.assert_equal(result, True)

    def test_returns_is_not_unbounded(self):
        baseTableau = np.array([
            [-1, -1, -1, -4, -4, -2, -2, -1, -21],
            [1, 0, 0, 2, 1, 1, 0, 1, 8],
            [0, 1, 0, 1, 2, 0, 1, -1, 8],
            [0, 0, 1, 1, 1, 0, 0, -1, 5],
        ])

        result = Simplex.isUnbounded(baseTableau)

        npt.assert_equal(result, False)

    def test_raises_unbounded_exception_for_larger_lp(self):
        """
        An exception should be raised if the lp is unbounded
        """
        baseTableau = np.array([
            [-1, -1, -1, -4, -4, -2, -2, -1, -21],
            [1, 0, 0, 2, 1, 1, 0, -1, 8],
            [0, 1, 0, 1, 2, 0, 1, -1, 8],
            [0, 0, 1, 1, 1, 0, 0, -1, 5],
        ])

        simplexObj = Simplex(m=3, n=8, tableau=baseTableau)

        with pytest.raises(UnboundedError):
            simplexObj.solve()

    def test_raises_unbounded_exception_in_trivial_lp(self):
        """
        An exception should be raised if the lp is unbounded
        """
        baseTableau = np.array([
            [0, 0, -1, 0, 0, 0, 0, 0],
            [1, 0, -1, 1, 0, 1, 0, 5],
            [0, 1, -1, 0, 1, 0, 1, 7],
        ])

        simplexObj = Simplex(m=3, n=2, tableau=baseTableau)

        with pytest.raises(UnboundedError):
            simplexObj.solve()

    def test_raises_unbounded_exception_and_certificate(self):
        """
        The certificate should be given when the exception is thrown
        """
        baseTableau = np.array([
            [0, 0, -1, 0, 0, 0, 0, 0],
            [1, 0, -1, 1, 0, 1, 0, 5],
            [0, 1, -1, 0, 1, 0, 1, 7],
        ])

        simplexObj = Simplex(m=3, n=2, tableau=baseTableau)

        with pytest.raises(UnboundedError) as exc:
            simplexObj.solve()

        npt.assert_allclose(exc.value.certificate, [0, 0], err_msg="Certificate should be instantly unbounded")

    def test_is_simplex_not_done(self):
        """
        We are not done when there is still a pivotable column, ie, negative value in first row
        """
        baseTableau = np.array([
            [0, 0, -1, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 5],
            [0, 1, 0, 0, 1, 0, 1, 7],
        ])

        m = LinearAlgebra.get_number_of_m_variables(baseTableau)
        n = LinearAlgebra.get_number_of_n_restrictions(baseTableau)

        simplexObj = Simplex(m=m, n=n, tableau=baseTableau)
        done = simplexObj.isSimplexDone()
        assert not done

    def test_is_simplex_done(self):
        """
        There are no more pivotable columns, ie, no negative value in first row and the objective value is 0
        """

        baseTableau = np.array([
            [0, 0, 1, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 0, 1, 0, 5],
            [0, 1, 0, 0, 1, 0, 1, 7],
        ])

        m = LinearAlgebra.get_number_of_m_variables(baseTableau, has_vero=False)
        n = LinearAlgebra.get_number_of_n_restrictions(baseTableau)

        simplexObj = Simplex(m=m, n=n, tableau=baseTableau)

        assert simplexObj.isSimplexDone()
