from bot import app

from .handler import start
# from .handler import post_advert
from .handler import advert_user


# this is to handle unused import warning
__all__ = ["start", "advert_user"]


if __name__ == "__main__":
    app.run_polling()
