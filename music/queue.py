from collections import deque
import random
from typing import List, Optional
from music.song import Song

class MusicQueue:
    def __init__(self):
        self.upcoming: deque[Song] = deque()
        self.history: List[Song] = []
        self.current: Optional[Song] = None

    def add(self, song: Song) -> None:
        self.upcoming.append(song)

    def add_multiple(self, songs: List[Song]) -> None:
        self.upcoming.extend(songs)

    def get_next(self) -> Optional[Song]:
        if self.current:
            self.history.append(self.current)
            self.current = None

        if not self.upcoming:
            return None

        self.current = self.upcoming.popleft()
        return self.current

    def get_previous(self) -> Optional[Song]:
        if not self.history:
            return None

        # Re-queue current song at the beginning of upcoming if it exists
        if self.current:
            self.upcoming.appendleft(self.current)
            self.current = None

        # Retrieve last played song from history
        self.current = self.history.pop()
        return self.current

    def shuffle(self) -> None:
        items = list(self.upcoming)
        random.shuffle(items)
        self.upcoming = deque(items)

    def clear(self) -> None:
        self.upcoming.clear()
        self.history.clear()
        self.current = None

    @property
    def is_empty(self) -> bool:
        return self.current is None and len(self.upcoming) == 0

    @property
    def total_count(self) -> int:
        count = len(self.upcoming)
        if self.current:
            count += 1
        return count
