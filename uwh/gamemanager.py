import time
import math

class GameState(object):
    game_over = 0
    first_half = 1
    half_time = 2
    second_half = 3


class TimeoutState(object):
    none = 0
    ref = 1
    white = 2
    black = 3


class TeamColor(object):
    black = 0
    white = 1


class PoolLayout(object):
    white_on_right = 0
    white_on_left = 1


def now():
    return math.floor(time.time())

class GameManager(object):

    def __init__(self, observers=None):
        self._white_score = 0
        self._black_score = 0
        self._duration = 0
        self._time_at_start = None
        self._game_state = GameState.first_half
        self._timeout_state = TimeoutState.none
        self._penalties = [[],[]]
        self._observers = observers or []
        self._is_passive = False
        self._layout = PoolLayout.white_on_right

    def gameClock(self):
        if not self.gameClockRunning() or self._is_passive:
            return self._duration

        game_clock = self._duration - (now() - self._time_at_start)
        return game_clock

    def setGameClock(self, n):
        self._duration = n

        if self.gameClockRunning():
            self._time_at_start = now()

        for mgr in self._observers:
            mgr.setGameClock(n)

    def whiteScore(self):
        return self._white_score

    def setWhiteScore(self, n):
        self._white_score = n

        for mgr in self._observers:
            mgr.setWhiteScore(n)

    def blackScore(self):
        return self._black_score

    def setBlackScore(self, n):
        self._black_score = n

        for mgr in self._observers:
            mgr.setBlackScore(n)

    def gameClockRunning(self):
        return bool(self._time_at_start)

    def setGameClockRunning(self, b):
        if b == self.gameClockRunning():
            return

        if b:
            self._time_at_start = now()
            if self._game_state != GameState.half_time:
                self._start_unstarted_penalties(self.gameClock())
        else:
            self._duration -= now() - self._time_at_start
            self._time_at_start = None

        for mgr in self._observers:
            mgr.setGameClockRunning(b)

    def gameState(self):
        return self._game_state

    def setGameState(self, state):
        self._game_state = state

        for mgr in self._observers:
            mgr.setGameState(state)

    def timeoutState(self):
        return self._timeout_state

    def setTimeoutState(self, state):
        self._timeout_state = state

        for mgr in self._observers:
            mgr.setTimeoutState(state)

    def gameStateFirstHalf(self):
        return self._game_state == GameState.first_half

    def setGameStateFirstHalf(self):
        self.setGameState(GameState.first_half)

        for mgr in self._observers:
            mgr.setGameStateFirstHalf()

    def gameStateHalfTime(self):
        return self._game_state == GameState.half_time

    def setGameStateHalfTime(self):
        self.setGameState(GameState.half_time)

        for mgr in self._observers:
            mgr.setGameStateHalfTime()

    def gameStateSecondHalf(self):
        return self._game_state == GameState.second_half

    def setGameStateSecondHalf(self):
        self.setGameState(GameState.second_half)

        for mgr in self._observers:
            mgr.setGameStateSecondHalf()

    def gameStateGameOver(self):
        return self._game_state == GameState.game_over

    def setGameStateGameOver(self):
        self.setGameState(GameState.game_over)

        for mgr in self._observers:
            mgr.setGameStateGameOver()

    def timeoutStateNone(self):
        return self._timeout_state == TimeoutState.none

    def setTimeoutStateNone(self):
        self._timeout_state = TimeoutState.none

        for mgr in self._observers:
            mgr.setTimeoutStateNone()

    def timeoutStateRef(self):
        return self._timeout_state == TimeoutState.ref

    def setTimeoutStateRef(self):
        self._timeout_state = TimeoutState.ref
        for mgr in self._observers:
            mgr.setTimeoutStateRef()

    def timeoutStateWhite(self):
        return self._timeout_state == TimeoutState.white

    def setTimeoutStateWhite(self):
        self._timeout_state = TimeoutState.white
        for mgr in self._observers:
            mgr.setTimeoutStateWhite()

    def timeoutStateBlack(self):
        return self._timeout_state == TimeoutState.black

    def setTimeoutStateBlack(self):
        self._timeout_state = TimeoutState.black
        for mgr in self._observers:
            mgr.setTimeoutStateBlack()

    def addPenalty(self, p):
        self._penalties[p.team()].append(p)
        if self.gameClockRunning():
            p.setStartTime(self.gameClock())
        for mgr in self._observers:
            mgr.addPenalty(p)

    def delPenalty(self, p):
        if p in self._penalties[p.team()]:
            self._penalties[p.team()].remove(p)
        for mgr in self._observers:
            mgr.delPenalty(p)

    def penalties(self, team_color):
        return self._penalties[team_color]

    def deleteAllPenalties(self):
        self._penalties = [[],[]]
        for mgr in self._observers:
            mgr.deleteAllPenalties()

    def _start_unstarted_penalties(self, game_clock):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.startTime():
                p.setStartTime(game_clock)

    def pauseOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(self):
                p.pause(self)
        for mgr in self._observers:
            mgr.pauseOutstandingPenalties()

    def restartOutstandingPenalties(self):
        for p in self._penalties[TeamColor.white] + self._penalties[TeamColor.black]:
            if not p.servedCompletely(self):
                p.restart(self)
        for mgr in self._observers:
            mgr.restartOutstandingPenalties()

    def deleteServedPenalties(self):
        print("removing {}".format([p for p in self._penalties[TeamColor.white] if p.servedCompletely(self)]))
        print("removing {}".format([p for p in self._penalties[TeamColor.black] if p.servedCompletely(self)]))

        self._penalties[TeamColor.white] = [p for p in self._penalties[TeamColor.white] if not p.servedCompletely(self)]
        self._penalties[TeamColor.black] = [p for p in self._penalties[TeamColor.black] if not p.servedCompletely(self)]
        for mgr in self._observers:
            mgr.deleteServedPenalties()

    def setPassive(self):
        self._is_passive = True

    def passive(self):
        return self._is_passive

    def setLayout(self, layout):
        self._layout = layout
        for mgr in self._observers:
            mgr.setLayout(layout)

    def layout(self):
        return self._layout

class Penalty(object):

    def __init__(self, player, team, duration, start_time = None):
        self._player = player
        self._team = team

        # Game time when the penalty started
        self._start_time = start_time

        # Total time of the penalty
        self._duration = duration

        # Amount left to be served (might be less than duration if partially
        # served in the first half)
        self._duration_remaining = duration

    def setStartTime(self, start_time):
        self._start_time = start_time

    def startTime(self):
        return self._start_time

    def timeRemaining(self, mgr):
        game_clock = mgr.gameClock()
        if not self._start_time:
            return self._duration_remaining
        remaining = self._duration_remaining - (self._start_time - game_clock)
        return max(remaining, 0)

    def servedCompletely(self, mgr):
        return self.timeRemaining(mgr) <= 0

    def player(self):
        return self._player

    def setPlayer(self, player):
        self._player = player

    def team(self):
        return self._team

    def duration(self):
        return self._duration

    def setDuration(self, duration):
        self._duration = duration
        self._duration_remaining = duration

    def dismissed(self):
        return self._duration == -1

    def pause(self, mgr):
        self._duration_remaining = self.timeRemaining(mgr)
        self._start_time = None

    def restart(self, mgr):
        self._start_time = self._duration

