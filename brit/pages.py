from collections import defaultdict
from datetime import datetime, timezone
from http import HTTPStatus

from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette_login.decorator import login_required
from tinydb import Query

from .models import ShoppingList, ShoppingListItem
from .templates import templates

SHOPPING_TABLE = "shopping"


class SingleList(HTTPEndpoint):
    async def get(self, request: Request):
        db_table = request.app.state.db.table("shopping")
        ListQuery = Query()
        shopping_lists = db_table.search(
            (ListQuery.user_email == request.user.email)
            & (ListQuery.timestamp == request.path_params["timestamp"])
        )
        if not shopping_lists:
            return Response(status_code=HTTPStatus.NOT_FOUND)
        shopping_list = ShoppingList(**shopping_lists[0])
        return templates.TemplateResponse(
            request, "list.html.jinja", {"shopping_list": shopping_list}
        )


class NewList(HTTPEndpoint):
    async def get(self, request: Request):
        return templates.TemplateResponse(request, "new.html.jinja")

    async def post(self, request: Request):
        items_dict: dict = defaultdict(dict)
        async with request.form() as form:
            for field, value in form.items():
                field_name, index = field.split("_")
                if field_name == "item":
                    items_dict[index]["description"] = value
                else:
                    items_dict[index]["price"] = value
        items_list = [
            ShoppingListItem(**item)
            for index, item in items_dict.items()
            if item["description"]
        ]
        if items_list:
            shopping_list = ShoppingList(
                user_email=request.user.email,
                timestamp=datetime.now(tz=timezone.utc).timestamp(),
                items=items_list,
            )
            db_table = request.app.state.db.table("shopping")
            db_table.insert(shopping_list.model_dump())
            return RedirectResponse(
                request.url_for("shopping-list", timestamp=shopping_list.timestamp),
                HTTPStatus.SEE_OTHER,
            )
        else:
            return templates.TemplateResponse(
                request,
                "new.html.jinja",
                {"error_message": "The list must include at least one item."},
            )


class AllLists(HTTPEndpoint):
    @login_required
    async def get(self, request: Request):
        db_table = request.app.state.db.table("shopping")
        shopping_lists = sorted(
            (
                ShoppingList(**slist)
                for slist in db_table.search(Query().user_email == request.user.email)
            ),
            key=lambda slist: slist.timestamp,
        )
        return templates.TemplateResponse(
            request, "all.html.jinja", {"shopping_lists": shopping_lists}
        )
