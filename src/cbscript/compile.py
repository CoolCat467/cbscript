# Python dependencies:
# * ply
# * pyyaml

import os
import sys
import time

from cbscript import cb_script, scriptparse, source_file


def run(script):
	while True:
		script.check_for_update()

		time.sleep(1)


def cli_run():
        if len(sys.argv) != 2:
                print("You must include a script filename.")
                exit()

        source = source_file.source_file(sys.argv[1])

        os.chdir(source.get_directory())

        script = cb_script.cbscript(source, scriptparse.parse)
        script.try_to_compile()

        run(script)


if __name__ == "__main__":
        cli_run()
