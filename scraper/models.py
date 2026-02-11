from dataclasses import dataclass


@dataclass
class Track:
    video_id: str
    title: str
    channel: str
    duration: int  # seconds

    @property
    def duration_str(self) -> str:
        """Format as M:SS or H:MM:SS."""
        if self.duration < 0:
            return "0:00"
        hours, remainder = divmod(self.duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"
