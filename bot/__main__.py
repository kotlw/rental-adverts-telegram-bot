from bot import app

from .handler import start
from .handler import post_edit_show_advert
from .handler import search
from .handler import review


# this is to handle unused import warning
__all__ = ["start", "post_edit_show_advert", "search", "review"]


if __name__ == "__main__":
    app.run_polling()
