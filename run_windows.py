from app import app


if __name__ == '__main__':
    app.secret_key = 'asdfpoiuwelkrj123ñ53543'
    app.run(port=80, debug=True)
