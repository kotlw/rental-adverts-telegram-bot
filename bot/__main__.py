from bot import app

from .handler import start
from .handler import post
from .handler import search


# this is to handle unused import warning
__all__ = ["start", "post", "search"]


if __name__ == "__main__":
    app.run_polling()
