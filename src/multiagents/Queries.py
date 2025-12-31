from pydantic import BaseModel

class Queries(BaseModel):
    queries: list[str]