from bot import app

from .handler import start
from .handler import post_advert


# this is to handle unused import warning
__all__ = ["start", "post_advert"]


if __name__ == "__main__":
    app.run_polling()
