import cv2
import numpy as np
import time
import key_press
import mss

from typing import Tuple, List


class OsuManiaBot(object):
    """ A simple bot for playing Osu mania. Success rate near 100% using the provided skin.

    Instance Attributes:
      - bbox: coordinates in the form (x1, y1, x2, y2) of where the bot will look.
              this should ideally have a height of 1-5 pixels as close to the line where
              notes disappear as possible and width of the exact play area.
      - columns: the number of columns of the map
      - _col_states: the current state of each column: pressed or released
      - _codes: mapping of column number to keyboard key. Keybinds should be set
                     to 1, 2, 3, 4... for columns, otherwise change the codes. Can
                     be found here: https://gist.github.com/dretax/fe37b8baf55bc30e9d63
      - _inplay: whether the bot is currently active

    """

    def __init__(self, bbox: Tuple[int, int, int, int], columns=4):
        self.bbox = bbox
        self.columns = columns
        self._col_states = self._initialize_states()
        self._codes = {0: 0x02,
                       1: 0x03,
                       2: 0x04,
                       3: 0x05,
                       4: 0x06,
                       5: 0x07,
                       6: 0x08,
                       7: 0x09,
                       8: 0x10,
                       9: 0x11}
        self._inplay = False

    def _initialize_states(self):
        """Return a list of length columns with default values set to
         False representing key not pressed.
         """

        return [False for _ in range(self.columns)]

    def _slice_columns(self, screen: np.array):
        """Takes in a 2d array of pixels and slices by column. Returns a list of the
        columns.
        A tolerance value is added to account for self.bbox not being perfect width.

        Preconditions:
          - screen should have same number of elements on every row
        """

        width = len(screen[0]) // self.columns
        tolerance = round(width * 0.2)

        cols = [[] for _ in range(self.columns)]

        for row in screen:
            for i in range(len(cols)):
                cols[i].extend(row[i * width + tolerance: (i + 1) * width - tolerance])

        return cols

    def _handle_press(self, cols: List[np.array]):
        """Takes in list of pixel sliced by column and handles keypresses based on pixel data.

        If all pixels in the column are white and the key is not currently pressed, it will press
        the key corresponding to the column.

        If there is one pixel in a column that is not white and they key is currently pressed, it
        will release the corresponding key.

        Preconditions:
          - columns pixel data is binary
        """

        for i, col in enumerate(cols):
            if np.all(col) and not self._col_states[i]:
                key_press.PressKey(self._codes[i])
                self._col_states[i] = True
            elif not np.all(col) and self._col_states[i]:
                key_press.ReleaseKey(self._codes[i])
                self._col_states[i] = False

    def test_region(self, bbox: Tuple[int, int, int, int]):
        """Displays the screen based on given bbox.

        Use this to find the correct bbox before using the bot. Ideally, the bbox should be
        1-5 pixels tall as close to the horizontal line where notes disappear as possible
         and exact width of play area.
        """

        with mss.mss() as sct:

            while True:
                screen = np.array(sct.grab(bbox))
                gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                retv, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

                cv2.imshow('Find the region', binary)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    break

    def run(self):
        """Runs the bot.

        """

        self._inplay = True
        last = time.time()

        with mss.mss() as snap:

            while self._inplay:

                screen = np.array(snap.grab(self.bbox))
                gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
                retv, binary = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)

                columns = self._slice_columns(binary)

                self._handle_press(columns)

                print(time.time() - last)
                last = time.time()

                if cv2.waitKey(3) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break

# if __name__ == '__main__':

time.sleep(2)
bbox4 = (250, 574, 510, 575)
bbox7 = (225, 574, 575, 575)
bot = OsuManiaBot(bbox7, columns=7)
# bot.test_region(bbox7)
bot.run()
