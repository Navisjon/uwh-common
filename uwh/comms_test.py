from .comms import UWHProtoHandler, gs_to_proto_enum, gs_from_proto_enum, ts_to_proto_enum, ts_from_proto_enum

from . import messages_pb2
from .gamemanager import GameManager, TimeoutState, GameState

def test_PingPong():
    class Client(UWHProtoHandler):
        def __init__(self, mgr, send_raw):
            UWHProtoHandler.__init__(self, mgr)
            self._send_raw = send_raw

        def send_raw(self, recipient, data):
            self._send_raw(self, data)

    class Server(UWHProtoHandler):
        def __init__(self, mgr):
            UWHProtoHandler.__init__(self, mgr)
            self.received = False

        def recv_message(self, sender, kind, msg):
            assert kind == messages_pb2.MessageType_Pong
            assert msg.Data == 42
            self.received = True

        def send_raw(self, recipient, data):
            self.client.recv_raw(self, data)

    s_mgr = GameManager()
    s = Server(s_mgr)
    c_mgr = GameManager()
    c = Client(c_mgr, lambda r, d: s.recv_raw(r, d))
    s.client = c

    msg = messages_pb2.Ping()
    msg.Data = 42
    s.send_message(c, messages_pb2.MessageType_Ping, msg)
    assert s.received


def test_GameKeyFrame():
    class Client(UWHProtoHandler):
        def __init__(self, mgr, send_raw):
            UWHProtoHandler.__init__(self, mgr)
            self._send_raw = send_raw

        def send_raw(self, recipient, data):
            self._send_raw(self, data)

    class Server(UWHProtoHandler):
        def __init__(self, mgr):
            UWHProtoHandler.__init__(self, mgr)
            self.received = False

        def send_raw(self, recipient, data):
            self.client.recv_raw(self, data)

    s_mgr = GameManager()
    s = Server(s_mgr)
    c_mgr = GameManager()
    c = Client(c_mgr, lambda r, d: s.recv_raw(r, d))
    s.client = c

    s_mgr.setGameClockRunning(False)
    s_mgr.setGameClock(42)
    s_mgr.setWhiteScore(15)
    s_mgr.setBlackScore(7)
    s_mgr.setGameStateFirstHalf()
    s_mgr.setTimeoutStateRef()

    s.send_GameKeyFrame(c)

    assert c_mgr.gameClockRunning() == False
    assert c_mgr.gameClock() == 42
    assert c_mgr.whiteScore() == 15
    assert c_mgr.blackScore() == 7
    assert c_mgr.gameStateFirstHalf()
    assert c_mgr.timeoutStateRef()


def test_pack_unpack():
    mgr = GameManager()
    handler = UWHProtoHandler(mgr)

    msg = messages_pb2.Ping()
    msg.Data = 37

    data = handler.pack_message(messages_pb2.MessageType_Ping, msg)
    data[1] = data[1] + 1

    threw = 0
    try:
        handler.unpack_message(data)
    except ValueError:
        threw += 1
    assert threw == 1

    try:
        handler.pack_message(256, None)
    except ValueError:
        threw += 1
    assert threw == 2


def test_enum_conversion():
    assert ts_from_proto_enum(messages_pb2.TimeoutState_None) == TimeoutState.none
    assert ts_to_proto_enum(TimeoutState.none) == messages_pb2.TimeoutState_None

    assert ts_from_proto_enum(messages_pb2.TimeoutState_None) == TimeoutState.none
    assert ts_from_proto_enum(messages_pb2.TimeoutState_RefTimeout) == TimeoutState.ref
    assert ts_from_proto_enum(messages_pb2.TimeoutState_BlackTimeout) == TimeoutState.ref
    assert ts_from_proto_enum(messages_pb2.TimeoutState_WhiteTimeout) == TimeoutState.ref

    assert ts_to_proto_enum(TimeoutState.none) == messages_pb2.TimeoutState_None
    assert ts_to_proto_enum(TimeoutState.ref) == messages_pb2.TimeoutState_RefTimeout

    assert gs_from_proto_enum(messages_pb2.GameState_GameOver) == GameState.game_over
    assert gs_from_proto_enum(messages_pb2.GameState_FirstHalf) == GameState.first_half
    assert gs_from_proto_enum(messages_pb2.GameState_HalfTime) == GameState.half_time
    assert gs_from_proto_enum(messages_pb2.GameState_SecondHalf) == GameState.second_half

    assert gs_to_proto_enum(GameState.game_over) == messages_pb2.GameState_GameOver
    assert gs_to_proto_enum(GameState.first_half) == messages_pb2.GameState_FirstHalf
    assert gs_to_proto_enum(GameState.half_time) == messages_pb2.GameState_HalfTime
    assert gs_to_proto_enum(GameState.second_half) == messages_pb2.GameState_SecondHalf
