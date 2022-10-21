from api.models.team import UsersForTeamsSuggestion
from api.services.team_suggestion import get_all_user_permutations


def test_get_all_user_permutations():
    users = UsersForTeamsSuggestion(
        user_id_1=1,
        user_id_2=2,
        user_id_3=3,
        user_id_4=4,
    )
    all_user_combinations =  get_all_user_permutations(users)
    assert len(all_user_combinations) == 24, "There should be 24 possible combinations"

    # Test that all combinations are unique
    unique_user_combinationes = []
    for user_combination in all_user_combinations:
        if user_combination not in unique_user_combinationes:
            unique_user_combinationes.append(user_combination)
    assert len(unique_user_combinationes) == 24, "There should be 24 unique combinations"
