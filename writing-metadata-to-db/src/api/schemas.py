from typing import List, Optional

from pydantic import BaseModel


class UserLikeSong(BaseModel):
    msno: str
    song_id: str


