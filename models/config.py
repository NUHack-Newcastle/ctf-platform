from db import db


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Define your configuration parameters here
    orchestrator_ip = db.Column(db.String(16), nullable=True)
    orchestrator_port = db.Column(db.Integer(), nullable=False, default=5000)
    secret_key = db.Column(db.String(256), nullable=False, default='test')
    # Add more parameters as needed

    # Define a constant field that always holds the same value
    _constant_field = db.Column(db.Integer, nullable=False, default=1, unique=True)

    @staticmethod
    def get_config():
        config = Config.query.first()
        if not config:
            # If no row exists, create one with default values
            config = Config()
            db.session.add(config)
            db.session.commit()
        return config
