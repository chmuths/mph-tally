from threading import Timer


class Scheduler:

    def __init__(self, tallies):

        self.tallies = tallies
        self.run = True
        self.trigger_timer()

    def trigger_timer(self):
        if self.run:
            t = Timer(1, self.blink)
            t.start()

    def blink(self):
        """
        Set circuits on or off depending on several criteria
        """
        if self.run:
            try:
                for tally_ID in range(len(self.tallies.tallies)):
                    self.tallies.blink_tally(tally_ID)
                self.trigger_timer()
            except Exception:
                print(f"Unhandled exception happened in scheduler")
                self.trigger_timer()

    def stop_blinker(self):
        self.run = False
