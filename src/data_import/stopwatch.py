import time
from typing import Literal

SegmentName = Literal["lap", "pause", "stop"]

TimeUnits = Literal["ms", "s"]


def scale(result: float, units: TimeUnits) -> int | float:
    match units:
        case "ms":
            return int(result * 1000)
        case "s":
            return round(result, 1)
    raise ValueError("Only supporting 'ms' or 's'")


class Segment:
    def __init__(self, name: SegmentName, duration: float, *, units: TimeUnits = "ms"):
        self.name = name
        self.duration = duration
        self._units = units

    def json(self) -> dict:
        return {self.name: self.duration}

    def __str__(self):
        return f"{self.name.upper().ljust(7, ' ')} {scale(self.duration, self._units)}{self._units}"


class Stopwatch:
    def __init__(self, *, units: TimeUnits = "ms"):
        now = time.time()
        self._units = units
        self._start_time = now
        self._last_lap = now
        self._pause_time = 0
        self._resume_time = 0
        self._paused = False
        self._segments: list[Segment] = []

    def pause(self):
        if not self._paused:
            self._paused = True
            self._pause_time = time.time()

    def resume(self):
        if self._paused:
            self._paused = False
            self._resume_time = time.time()
            self._create_segment("pause", self._resume_time - self._pause_time)

    def lap(self) -> int | float:
        if self._paused:
            raise Exception("Cannot take lap while paused")

        pause_duration = 0
        for s in self._segments[::-1]:
            if s.name == "pause":
                pause_duration += s.duration
            else:
                break

        now = time.time()
        lap_duration = now - self._last_lap - pause_duration

        self._last_lap = now
        self._pause_time = 0
        self._resume_time = 0
        self._create_segment("lap", lap_duration)

        return scale(lap_duration, self._units)

    def stop(self) -> int | float:
        now = time.time()
        total_duration = now - self._start_time

        self._start_time = now
        self._last_lap = now
        self._pause_time = 0
        self._resume_time = 0
        self._paused = False
        self._create_segment("stop", total_duration)

        return scale(total_duration, self._units)

    def isolate(self, func, *args, **kwargs):
        self.pause()
        result = func(*args, **kwargs)
        self.resume()
        return result

    def print_segments(self):
        print("Stopwatch Segments")
        print(f"┌{'-' * 17}")
        for i, segment in enumerate(self._segments):
            if segment.name == "pause":
                print("│", end="")
            else:
                print("├", end="")
            print(f" {segment}")
        print(f"└{'-' * 17}")

    def json(self) -> dict:
        return {
            "stopwatch_stats": {
                "units": self._units,
                "runtime": self.stop(),
                "segments": [segment.json() for segment in self._segments]
            }
        }

    def _create_segment(self, name: SegmentName, duration: float):
        self._segments.append(Segment(name, duration, units=self._units))

    def _change_units(self, units: TimeUnits):
        if self._segments:
            raise Exception("Units can only be changed until segments are recorded")
        self._units = units

    def __str__(self):
        return f"{self.lap()}{self._units}"


global_stopwatch = Stopwatch()


def global_stopwatch_config(units: TimeUnits):
    global_stopwatch._change_units(units)


if __name__ == '__main__':
    watch = Stopwatch()

    time.sleep(2)
    assert round(watch.lap() / 1000, 1) == 2.0

    time.sleep(1)
    assert round(watch.lap() / 1000, 1) == 1.0

    watch.pause()
    time.sleep(2)
    watch.resume()
    time.sleep(1.5)
    assert round(watch.lap() / 1000, 1) == 1.5

    watch.isolate(time.sleep, 0.5)
    watch.isolate(time.sleep, 0.5)
    time.sleep(0.5)
    assert round(watch.lap() / 1000, 1) == 0.5

    assert 7.9 <= round(watch.stop() / 1000, 1) <= 8.1

    watch.print_segments()
