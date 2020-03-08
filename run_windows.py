from app import app
from app.utils import gen_random_password


if __name__ == "__main__":
    app.secret_key = gen_random_password()
    app.run(port=80, debug=True)
