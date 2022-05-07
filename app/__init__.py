import os
from flask import Flask, render_template

import pulumi.automation as auto


def ensure_plugins():
    ws = auto.LocalWorkspace()
    ws.install_plugin("aws", "v4.0.0")

# create application factory function
# https://flask.palletsprojects.com/en/2.1.x/tutorial/factory/
def create_app():
    # create and configure the app
    ensure_plugins()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="secret",
        PROJECT_NAME="self-service-s3",
        PULUMI_ORG=os.environ.get("PULUMI_ORG"),
    )
    
    # handler for landing page
    @app.route("/", methods=["GET"])
    def index():
        """index page"""
        return render_template("index.html")

    from . import sites

    app.register_blueprint(sites.bp)
    
    return app