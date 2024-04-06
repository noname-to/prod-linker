from typing import List

from app.data import models


async def read_all_representatives() -> List[models.Representative]:
    return await models.Representative.all().to_list()
