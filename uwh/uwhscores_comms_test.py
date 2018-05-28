from .uwhscores_comms import UWHScores

REPEAT_COUNT = 500
REPEAT_DELAY = 0.01

USE_LOCAL_SERVER = False

if USE_LOCAL_SERVER:
    SERVER_ADDRESS = 'http://127.0.0.1:5000/api/v1/'
    USERNAME = 'test@jimlester.net'
    PASSWORD = 'temp123!@#'
else:
    SERVER_ADDRESS = 'https://uwhscores.com/api/v1/'

IMPOSSIBLE_SERVER_ADDRESS = 'http://127.0.0.1:83492/'

MOCK = True

def test_async_get_tournament_list():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(tournament_list):
        assert len(tournament_list) >= 13
        assert tournament_list[14]['name'] == 'Battle@Altitude 2018'
        assert tournament_list[14]['location'] == 'Denver, CO'
        assert tournament_list[14]['is_active'] == False

    uwhscores.get_tournament_list(success)

def test_get_tournament():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(tournament):
        assert tournament['tid'] == 14
        assert tournament['name'] == 'Battle@Altitude 2018'
        assert tournament['location'] == 'Denver, CO'
        assert tournament['is_active'] == False

    uwhscores.get_tournament(14, success)

def test_get_game_list():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(game_list):
        assert game_list[1]['black'] == 'LA'
        assert game_list[1]['black_id'] == 1
        assert game_list[1]['pool'] == '1'
        assert game_list[4]['white'] == 'Seattle'
        assert game_list[4]['white_id'] == 6
        assert game_list[4]['start_time'] == '2018-01-27T09:02:00'

    uwhscores.get_game_list(14, success)

def test_get_game():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(game):
        assert game['black'] == 'U19 Girls'
        assert game['black_id'] == 14
        assert game['day'] == 'Sat'
        assert game['start_time'] == '2018-01-27T09:34:00'
        assert game['white'] == 'US Elite Women'
        assert game['white_id'] == 17

    uwhscores.get_game(14, 6, success)

def test_get_team_list():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(team_list):
        assert team_list[1]['name'] == 'LA'
        assert team_list[3]['name'] == 'Rainbow Raptors'
        assert team_list[7]['name'] == 'Cupcake Crocodiles'
        assert team_list[11]['name'] == 'Chicago'
        assert team_list[13]['name'] == 'Colorado B'
        assert team_list[17]['name'] == 'US Elite Women'

    uwhscores.get_team_list(14, success)

def test_get_standings():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(standings):
        assert standings[0]['team'] == 'Team Sexy'
        assert standings[0]['team_id'] == 2
        assert standings[0]['stats']['points'] == 27
        assert standings[2]['team'] == 'UF'
        assert standings[4]['team'] == 'Hampton'
        assert standings[6]['team'] == 'Swordfish'
        assert standings[7]['team'] == 'George Mason'

    uwhscores.get_standings(12, success)

def test_get_roster():
    uwhscores = UWHScores(SERVER_ADDRESS, mock=MOCK)

    def success(roster):
        assert roster[1]['name'] == 'Schmoe, Joe'
        assert roster[1]['player_id'] == 1
        assert len(roster) == 12

    uwhscores.get_roster(15, 1, success)
