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
