from sqlmodel import SQLModel
from typing import List
def get_ordered_values(model:SQLModel, item):
    schema = model.schema()
    fields = schema['properties']
    field_ids = list(fields.keys())
    item_dict = item.dict()
    ordered_values = []
    for key in field_ids:
        ordered_values.append(item_dict[key])
    return ordered_values