#!/usr/bin/env python3
import logging
from subprocess import Popen, check_output
from sys import argv

from notify2 import Notification, EXPIRES_NEVER

from notify2_component import Notify2Component

logging.basicConfig(level=logging.INFO)

ALLOWED_NETWORKS = {

}


def get_wifi_name():
    output = check_output(['/sbin/iwgetid', '-r']).decode()
    name = output.strip()
    return name


class WrapperComponent(Notify2Component):
    def __init__(self, command: str):
        super().__init__('WrapperComponent')
        self.command = command
        self.logger = logging.getLogger('NotificationWrapper')

    def _run_command(self):
        self.logger.info("Running command \"%s\"", self.command)
        command = Popen(self.command, shell=True)
        command.communicate()
        self.logger.info("Exit code: %d", command.returncode)

    def _should_run(self) -> bool:
        wifi = get_wifi_name()
        if wifi in ALLOWED_NETWORKS:
            self.logger.info("Network %s is whitelisted", wifi)
            return True
        else:
            self.logger.info("Network %s is not whitelisted", wifi)
            return False

    def on_start(self):
        if self._should_run():
            self._run_command()
            self.finish_async()
        else:
            n = Notification(
                summary="Trees dumper",
                message="Run now?",  # TODO include command name
                icon='dialog-question',
            )
            n.set_timeout(EXPIRES_NEVER)
            n.add_action("error", "<b>Run</b>", lambda n, action: self._run_command())
            n.add_action("close", "Close", lambda n, action: None)
            n.connect('closed', lambda n: self.finish_async())
            n.show()

    def on_stop(self):
        pass


def main():
    # TODO get from arguments?
    COMMAND = argv[1]  # type: str
    WrapperComponent(COMMAND).start()


if __name__ == '__main__':
    main()
