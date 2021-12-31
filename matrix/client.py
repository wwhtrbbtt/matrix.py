from .API import Bot
from time import sleep, time
from .discord_like_classes import *
from threading import Thread


class Client:
    def __init__(self):
        """Initialize client."""
        self.loop = None
        self.client = Bot
        self.is_running = False

    def _handle_messages(self) -> None:
        """Handle messages."""
        answered_commands = []
        initial = True
        while self.is_running:
            sleep(self.client.sync_delay)
            # for every room
            for i, room in enumerate(self.client.state.joined_rooms):
                # get all messages
                for m in self.client.state.joined_rooms[i].timeline:
                    # if it's a message
                    if m.event_id not in answered_commands and m.type == "m.room.message":
                        # Mark as read, so we don't get it again
                        answered_commands.append(m.event_id)
                        if not initial:
                            r = Room(
                                id=room.id,
                                topic=None,
                                last_message=room.timeline[-1],
                                last_message_id=room.timeline[-1].event_id,
                            )

                            msg = Message(
                                type=m.type,
                                content=m.parsed_message.body,
                                author=m.sender,
                                id=m.event_id,
                                room=r,
                                created_at=m.timestamp,
                                edited_at=None,
                            )
                            self.on_message(msg)
            if initial:
                print(f"[+] {len(answered_commands)} messages answered so far.")
                initial = False
            initial = False

    def _handle_invites(self) -> None:
        """Handle invites."""
        handled_invites = []
        initial = True
        while self.is_running:
            sleep(self.client.sync_delay)
            for invite in self.client.state.invited_rooms:
                if hash(invite.room_id + invite.invitee) not in handled_invites:
                    handled_invites.append(hash(invite.room_id + invite.invitee))
                    if not initial:
                        i = Invite(
                            room_id=invite.room_id,
                            inviter=invite.invitee,
                            created_at=time(),
                            _invite_state=invite.invite_state,
                        )
                        self.on_invite(i)
            if initial:
                print(f"[+] {len(handled_invites)} invites handled so far.")
                initial = False


    def run(self, username: str, password: str, homeserver: str, device_id: str = "") -> None:
        """
        Run client.
        :param username: username of the user
        :param password: password of the user
        :param homeserver: homeserver of the user
        :param device_id: device id of the user (optional)
        """
        self.client = Bot(homeserver=homeserver, username=username, password=password, device_id=device_id)
        self.auth = self.client.login(device_id=device_id)
        self.user = self.auth.user_id
        self.is_running = True

        self.client.start_sync()
        Thread(target=self._handle_messages).start()
        Thread(target=self._handle_invites).start()
        self.on_ready()
        self.client.run_forever()
