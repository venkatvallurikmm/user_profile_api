from app.routes import app

app.config.from_pyfile('config.cfg')
app.run(debug=True)
