import sys
import types
import unittest
from unittest.mock import Mock, patch


fake_itchat = types.ModuleType("itchat")
fake_itchat.send = Mock()
fake_itchat.search_chatrooms = Mock(return_value=[])
fake_itchat.delete_member_from_chatroom = Mock()
sys.modules["itchat"] = fake_itchat

fake_ad = types.ModuleType("untils.ad")
fake_ad.QRcode_detection = Mock(return_value=False)
sys.modules["untils.ad"] = fake_ad

fake_nlp = types.ModuleType("untils.qq_nlpchat")
fake_nlp.get_auto_reply = Mock(return_value="reply text")
sys.modules["untils.qq_nlpchat"] = fake_nlp

from chat import message


class FakeGroupMessage(dict):
    def __init__(
        self,
        text="hello",
        group_id="room-1",
        sender_id="user-1",
        sender_name="Alice",
        is_at=False,
    ):
        super().__init__(Text=text)
        self.fromUserName = group_id
        self.actualUserName = sender_id
        self.actualNickName = sender_name
        self.isAt = is_at


class HandleGroupMessageTests(unittest.TestCase):
    def setUp(self):
        fake_itchat.send.reset_mock()
        fake_itchat.search_chatrooms.reset_mock()
        fake_itchat.search_chatrooms.return_value = []
        fake_itchat.delete_member_from_chatroom.reset_mock()

    def _config_get(self, key, default=None):
        config_map = {
            "wechat_uuid": "self",
            "group_helper_conf": {
                "is_open": True,
                "is_at": False,
                "is_all": True,
                "group_admin": [],
                "group_name_white_list": ["unused"],
                "group_name_black_list": ["blocked-group"],
            },
        }
        return config_map.get(key, default)

    def test_all_groups_mode_processes_non_blacklisted_groups(self):
        with patch.object(message.config, "get", side_effect=self._config_get), \
            patch.object(message, "is_white_group", return_value=False), \
            patch.object(message, "get_auto_reply", return_value="reply text"):
            message.handle_groups_message(FakeGroupMessage())

        self.assertEqual(fake_itchat.send.call_count, 1)
        sent_text, sent_group = fake_itchat.send.call_args.args
        self.assertIn("reply text", sent_text)
        self.assertEqual(sent_group, "room-1")

    def test_all_groups_mode_skips_blacklisted_groups(self):
        def config_get(key, default=None):
            config_map = {
                "wechat_uuid": "self",
                "group_helper_conf": {
                    "is_open": True,
                    "is_at": False,
                    "is_all": True,
                    "group_admin": [],
                    "group_name_white_list": ["unused"],
                    "group_name_black_list": ["blocked-group"],
                },
            }
            return config_map.get(key, default)

        fake_itchat.search_chatrooms.return_value = [{"UserName": "room-1"}]

        with patch.object(message.config, "get", side_effect=config_get), \
            patch.object(message, "is_white_group", return_value=False), \
            patch.object(message, "get_auto_reply", return_value="reply text"):
            message.handle_groups_message(FakeGroupMessage())

        fake_itchat.send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
