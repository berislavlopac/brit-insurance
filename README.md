# Shopping Lists

A simple app for shopping lists, based on the task by Brit Insurance.

## Assumptions

The task is not clear whether the lists need to be saved. Since the task requires a database, as well as authentication, it was assumed that each user's lists should be saved once entered.

## Shortcuts

The auth system is very basic, and does not include a few functionalities which would be expected in a production system, such as email verification, password reset and the like.

Individual lists don't have a custom ID attribute; instead they are identified only by their creation timestamp. Since timestamps are Python `float` values, and a new list can only be created manually via the Web form, there is no chance of collision.

## Technical Choices

* Programming language: Python 3.11
* Application framework: [Starlette](https://www.starlette.io/)
* Authentication framework: [Starlette-Login](https://starlette-login.readthedocs.io)
* Business logic models: [Pydantic](https://docs.pydantic.dev)
* Database: [TinyDB](https://tinydb.readthedocs.io)
* Deployment: [Fly.io](https://fly.io/)
