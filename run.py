from app import create_app

app = create_app()

if __name__ == "__main__":
    # For local development only. For LAN deployment, configure the host
    # explicitly and use a production WSGI server before real-world use.
    app.run(debug=app.config["DEBUG"])
