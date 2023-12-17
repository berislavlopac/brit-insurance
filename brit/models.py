from typing import List

from pydantic import BaseModel, EmailStr


class ShoppingListItem(BaseModel):
    description: str
    price: float


class ShoppingList(BaseModel):
    user_email: EmailStr
    timestamp: float
    items: List[ShoppingListItem]

    @property
    def total(self) -> float:
        return sum(item.price for item in self.items)

    @property
    def description(self) -> str:
        return ", ".join(item.description for item in self.items)
