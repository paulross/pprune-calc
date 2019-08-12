"""
Some common data structures.
"""
import typing


class FrameComment(typing.NamedTuple):
    """A frame of a video with a comment."""
    frame: int
    comment: str


class TimeComment(typing.NamedTuple):
    """A time on a video with a comment."""
    time: float
    comment: str


class MidPlusMinus(typing.NamedTuple):
    """Mid value with a tolerance/error of a maximum value and minimum value."""
    mid: float
    max: float
    min: float

    @property
    def plus(self) -> float:
        return self.max - self.mid

    @property
    def minus(self) -> float:
        return self.min - self.mid

    @property
    def tolerance(self) -> float:
        return (self.max - self.min) / 2.0

    def __str__(self) -> str:
        return '{:f} +{:f}/-{:f}'.format(self.mid, self.plus, self.minus)

    def __format__(self, format_spec: str) -> str:
        # if format_spec:
        #     return 'mid={:{format_spec}} max={:{format_spec}} min={:{format_spec}}'.format(
        #         self.mid, self.max, self.min, format_spec=format_spec
        #     )
        # return 'mid={} max={} min={}'.format(self. mid, self.max, self.min)
        if format_spec:
            return 'mid={:{format_spec}} +: {:{format_spec}} -: {:{format_spec}}'.format(
                self.mid, self.plus, self.minus, format_spec=format_spec
            )
        return 'mid={} +:{} -: {}'.format(self. mid, self.plus, self.minus)
