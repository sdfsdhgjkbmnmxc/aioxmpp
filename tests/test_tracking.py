import unittest
import unittest.mock

from enum import Enum

import aioxmpp.stanza
import aioxmpp.statemachine
import aioxmpp.stream as stream
import aioxmpp.tracking as tracking


class TestMessageState(unittest.TestCase):
    def test_is_enum(self):
        self.assertTrue(issubclass(
            tracking.MessageState,
            Enum
        ))

    def test_order(self):
        self.assertLess(
            tracking.MessageState.IN_TRANSIT,
            tracking.MessageState.ABORTED
        )

        self.assertLess(
            tracking.MessageState.ABORTED,
            tracking.MessageState.DELIVERED_TO_SERVER,
        )
        self.assertLess(
            tracking.MessageState.ABORTED,
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
        )
        self.assertLess(
            tracking.MessageState.ABORTED,
            tracking.MessageState.SEEN_BY_RECIPIENT,
        )

        self.assertLess(
            tracking.MessageState.DELIVERED_TO_SERVER,
            tracking.MessageState.ABORTED,
        )
        self.assertLess(
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
            tracking.MessageState.ABORTED,
        )
        self.assertLess(
            tracking.MessageState.SEEN_BY_RECIPIENT,
            tracking.MessageState.ABORTED,
        )

        self.assertLess(
            tracking.MessageState.TIMED_OUT,
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
        )
        self.assertLess(
            tracking.MessageState.TIMED_OUT,
            tracking.MessageState.SEEN_BY_RECIPIENT,
        )

        self.assertLess(
            tracking.MessageState.DELIVERED_TO_SERVER,
            tracking.MessageState.TIMED_OUT,
        )
        self.assertLess(
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
            tracking.MessageState.TIMED_OUT,
        )
        self.assertLess(
            tracking.MessageState.SEEN_BY_RECIPIENT,
            tracking.MessageState.TIMED_OUT,
        )

        self.assertLess(
            tracking.MessageState.UNKNOWN,
            tracking.MessageState.DELIVERED_TO_SERVER,
        )
        self.assertLess(
            tracking.MessageState.UNKNOWN,
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
        )
        self.assertLess(
            tracking.MessageState.UNKNOWN,
            tracking.MessageState.SEEN_BY_RECIPIENT,
        )

        self.assertLess(
            tracking.MessageState.DELIVERED_TO_SERVER,
            tracking.MessageState.UNKNOWN,
        )
        self.assertLess(
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
            tracking.MessageState.UNKNOWN,
        )
        self.assertLess(
            tracking.MessageState.SEEN_BY_RECIPIENT,
            tracking.MessageState.UNKNOWN,
        )

        self.assertLess(
            tracking.MessageState.TIMED_OUT,
            tracking.MessageState.ABORTED,
        )

        self.assertLess(
            tracking.MessageState.ABORTED,
            tracking.MessageState.TIMED_OUT,
        )

        self.assertLess(
            tracking.MessageState.UNKNOWN,
            tracking.MessageState.ABORTED,
        )

        self.assertLess(
            tracking.MessageState.ABORTED,
            tracking.MessageState.UNKNOWN,
        )

        self.assertLess(
            tracking.MessageState.TIMED_OUT,
            tracking.MessageState.UNKNOWN,
        )

        self.assertLess(
            tracking.MessageState.UNKNOWN,
            tracking.MessageState.TIMED_OUT,
        )

        self.assertFalse(
            tracking.MessageState.ABORTED <
            tracking.MessageState.IN_TRANSIT
        )

        self.assertFalse(
            tracking.MessageState.TIMED_OUT <
            tracking.MessageState.IN_TRANSIT
        )

        self.assertLess(
            tracking.MessageState.IN_TRANSIT,
            tracking.MessageState.DELIVERED_TO_SERVER,
        )
        self.assertLess(
            tracking.MessageState.DELIVERED_TO_SERVER,
            tracking.MessageState.DELIVERED_TO_RECIPIENT
        )
        self.assertLess(
            tracking.MessageState.DELIVERED_TO_RECIPIENT,
            tracking.MessageState.SEEN_BY_RECIPIENT
        )


class TestMessageTracker(unittest.TestCase):
    def test_is_statemachine(self):
        self.assertTrue(issubclass(
            tracking.MessageTracker,
            aioxmpp.statemachine.OrderedStateMachine
        ))

    def setUp(self):
        self.stanza = aioxmpp.stanza.Message(type_="chat")
        self.token = stream.StanzaToken(self.stanza)
        self.tr = tracking.MessageTracker(self.token)

    def test_init(self):
        self.assertIs(self.tr.token, self.token)

    def test_setting_state_emits_on_state_change(self):
        mock = unittest.mock.Mock()
        mock.return_value = None
        self.tr.on_state_change.connect(mock)

        self.tr.state = tracking.MessageState.DELIVERED_TO_SERVER
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_SERVER)
        mock.assert_called_with(
            tracking.MessageState.DELIVERED_TO_SERVER
        )

        self.tr.state = tracking.MessageState.DELIVERED_TO_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_RECIPIENT)
        mock.assert_called_with(
            tracking.MessageState.DELIVERED_TO_RECIPIENT
        )

        self.tr.state = tracking.MessageState.SEEN_BY_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.SEEN_BY_RECIPIENT)
        mock.assert_called_with(
            tracking.MessageState.SEEN_BY_RECIPIENT
        )

    def test_aborting_after_delivered_to_server_not_possible(self):
        mock = unittest.mock.Mock()
        mock.return_value = None
        self.tr.on_state_change.connect(mock)

        self.tr.state = tracking.MessageState.DELIVERED_TO_SERVER
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_SERVER)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.ABORTED

        self.tr.state = tracking.MessageState.DELIVERED_TO_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_RECIPIENT)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.ABORTED

        self.tr.state = tracking.MessageState.SEEN_BY_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.SEEN_BY_RECIPIENT)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.ABORTED

        self.assertSequenceEqual(
            mock.mock_calls,
            [
                unittest.mock.call(tracking.MessageState.DELIVERED_TO_SERVER),
                unittest.mock.call(
                    tracking.MessageState.DELIVERED_TO_RECIPIENT),
                unittest.mock.call(tracking.MessageState.SEEN_BY_RECIPIENT),
            ]
        )

    def test_timeout_is_possible_after_delivered_to_server(self):
        mock = unittest.mock.Mock()
        mock.return_value = None
        self.tr.on_state_change.connect(mock)

        self.tr.state = tracking.MessageState.DELIVERED_TO_SERVER
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_SERVER)

        self.tr.state = tracking.MessageState.TIMED_OUT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.TIMED_OUT)

    def test_timeout_is_not_possible_after_delivered_to_recipient(self):
        mock = unittest.mock.Mock()
        mock.return_value = None
        self.tr.on_state_change.connect(mock)

        self.tr.state = tracking.MessageState.DELIVERED_TO_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_RECIPIENT)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.TIMED_OUT

        self.tr.state = tracking.MessageState.SEEN_BY_RECIPIENT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.SEEN_BY_RECIPIENT)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.TIMED_OUT

    def test_delivery_is_not_possible_after_timeout(self):
        mock = unittest.mock.Mock()
        mock.return_value = None
        self.tr.on_state_change.connect(mock)

        self.tr.state = tracking.MessageState.TIMED_OUT
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.TIMED_OUT)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.DELIVERED_TO_RECIPIENT

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.SEEN_BY_RECIPIENT

    def test_delivered_to_server_after_aborting_not_possible(self):
        self.tr.state = tracking.MessageState.ABORTED
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.ABORTED)

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.DELIVERED_TO_SERVER

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.IN_TRANSIT

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.DELIVERED_TO_RECIPIENT

        with self.assertRaises(ValueError):
            self.tr.state = tracking.MessageState.SEEN_BY_RECIPIENT

    def test_on_stanza_state_change_to_aborted(self):
        self.tr.on_stanza_state_change(stream.StanzaState.ABORTED)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.ABORTED
        )

    def test_on_stanza_state_change_to_acked(self):
        self.tr.on_stanza_state_change(stream.StanzaState.ACKED)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_SERVER
        )

    def test_on_stanza_state_change_to_sent_without_sm(self):
        self.tr.on_stanza_state_change(stream.StanzaState.SENT_WITHOUT_SM)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.IN_TRANSIT
        )

    def test_on_stanza_state_change_to_sent(self):
        self.tr.on_stanza_state_change(stream.StanzaState.SENT)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.IN_TRANSIT
        )

    def test_on_stanza_state_change_to_dropped(self):
        self.tr.on_stanza_state_change(stream.StanzaState.DROPPED)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.ABORTED
        )

    def test_on_stanza_state_change_does_not_fail_on_state_errors(self):
        self.tr.state = tracking.MessageState.DELIVERED_TO_SERVER
        self.tr.on_stanza_state_change(stream.StanzaState.ABORTED)
        self.assertEqual(
            self.tr.state,
            tracking.MessageState.DELIVERED_TO_SERVER
        )

    def tearDown(self):
        del self.tr
