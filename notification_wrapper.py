#!/usr/bin/env python3.6
import logging
from subprocess import Popen, check_output
from sys import argv
from typing import List
from datetime import timedelta

from notify2 import Notification, EXPIRES_NEVER

from notify2_component import Notify2Component
from config import ALLOWED_NETWORKS, IGNORED_NETWORKS

from kython import get_networks

logging.basicConfig(level=logging.INFO)

COMMAND_TIMEOUT_MILLIS = timedelta(days=1).total_seconds()

class WrapperComponent(Notify2Component):
    def __init__(self, command: List[str]) -> None:
        super().__init__('WrapperComponent')
        self.command = command
        self.logger = logging.getLogger('NotificationWrapper')

    def _run_command(self, n=None): # TODO notification type?
        self.logger.info("Running command \"%s\"", str(self.command))
        command = Popen(self.command)
        command.wait(timeout=COMMAND_TIMEOUT_MILLIS)
        if command.returncode != 0:
            self.logger.critical("Exit code: %d", command.returncode)
        else:
            self.logger.info("Exit code: 0")
        if n is not None:
            n.close()

    def _should_run(self) -> bool:
        networks = get_networks()
        networks = set(networks).difference(IGNORED_NETWORKS)

        if len(networks) != 1:
            self.logger.warning(f"Multiple networks: {networks}, not running")
            return False

        [name] = networks
        if name in ALLOWED_NETWORKS:
            self.logger.info(f"Network {name} is whitelisted")
            return True
        else:
            self.logger.info(f"Network {name} is not whitelisted")
            return False

    def on_start(self):
        if self._should_run():
            self._run_command()
            self.finish_async()
        else:
            n = Notification(
                summary=str(self.command),
                message="Run now?",  # TODO include command name
                icon='dialog-question',
            )
            n.set_timeout(EXPIRES_NEVER)
            n.add_action("error", "<b>Run</b>", lambda n, action: self._run_command(n))
            n.add_action("close", "Close", lambda n, action: n.close())
            n.connect('closed', lambda n: self.finish_async())
            n.show()

    def on_stop(self):
        pass


def main():
    command = argv[1:]  # type: List[str]
    WrapperComponent(command).start()


if __name__ == '__main__':
    main()
