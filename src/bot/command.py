from typing import Optional
from dataclasses import replace
from aiogram import Bot
from aiogram.filters import Command, CommandObject
from aiogram.utils.deep_linking import decode_payload
from magic_filter import MagicFilter


class BaseCommand(Command):
    def __str__(self) -> str:
        return self._signature_to_string(
            ignore_case=self.ignore_case,
            ignore_mention=self.ignore_mention,
            magic=self.magic,
            deep_link=self.deep_link,
            deep_link_encoded=self.deep_link_encoded,
        )

    async def parse_command(self, text: str, bot: Bot) -> CommandObject:
        """
        Extract command from the text and validate

        :param text:
        :param bot:
        :return:
        """
        command = self.extract_command(text)
        self.validate_prefix(command=command)
        await self.validate_mention(bot=bot, command=command)
        command = self.validate_command(command)
        command = self.validate_deeplink(command=command)
        command = self.do_magic(command=command)
        return command  # noqa: RET504

    def validate_deeplink(self, command: CommandObject) -> CommandObject:
        if not self.deep_link:
            return command
        if not command.args:
            raise Exception("Deep-link was missing")
        args = command.args
        if self.deep_link_encoded:
            try:
                args = decode_payload(args)
            except UnicodeDecodeError as e:
                raise Exception(f"Failed to decode Base64: {e}")
            return replace(command, args=args)
        return command


class CommandLogin(BaseCommand):
    def __init__(
        self,
        deep_link: bool = False,
        deep_link_encoded: bool = False,
        ignore_case: bool = False,
        ignore_mention: bool = False,
        magic: Optional[MagicFilter] = None,
    ):
        super().__init__(
            "login",
            prefix="/",
            ignore_case=ignore_case,
            ignore_mention=ignore_mention,
            magic=magic,
        )
        self.deep_link = deep_link
        self.deep_link_encoded = deep_link_encoded
