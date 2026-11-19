from app.topsis import topsis


def test_empty_input_gives_empty_list():
    assert topsis([], [1], [True]) == []


def test_one_benefit_criterion_best_gets_1_and_worst_gets_0():
    # 3 and 4 become 0.6 and 0.8 after scaling, so 4 is the best and 3 the worst
    assert topsis([[3], [4]], [1], [True]) == [0.0, 1.0]


def test_a_cost_criterion_prefers_the_smaller_value():
    assert topsis([[3], [4]], [1], [False]) == [1.0, 0.0]


def test_option_that_wins_every_criterion_ranks_first():
    scores = topsis([[0.2, 30], [0.9, 5], [0.5, 15]], [0.6, 0.4], [True, False])
    assert scores[1] == max(scores) == 1.0
    assert scores[0] == min(scores) == 0.0


def test_weights_change_the_winner():
    rows = [[0.9, 60], [0.3, 5]]
    interest_matters = topsis(rows, [0.9, 0.1], [True, False])
    time_matters = topsis(rows, [0.1, 0.9], [True, False])
    assert interest_matters[0] > interest_matters[1]
    assert time_matters[1] > time_matters[0]


def test_identical_options_get_equal_scores():
    assert topsis([[1, 2], [1, 2]], [0.5, 0.5], [True, False]) == [0.5, 0.5]


def test_column_of_zeros_does_not_crash():
    scores = topsis([[0, 5], [0, 9]], [0.5, 0.5], [True, True])
    assert scores == [0.0, 1.0]


def test_scores_stay_between_0_and_1():
    scores = topsis([[1, 9, 4], [7, 2, 8], [5, 5, 5]], [0.3, 0.3, 0.4], [True, False, True])
    assert all(0.0 <= s <= 1.0 for s in scores)
    