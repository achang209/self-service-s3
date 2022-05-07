import json
import requests
from flask import (
    current_app,
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    render_template,
)

import pulumi
import pulumi.automation as auto
from pulumi_aws import s3

bp = Blueprint("sites", __name__, url_prefix="/sites")


# This function defines our pulumi s3 static website in terms of the content that the caller passes in.
# This allows us to dynamically deploy websites based on user defined values from the POST body.
def create_pulumi_program(content: str):
    # Create a bucket and expose a website index document
    site_bucket = s3.Bucket(
        "s3-website-bucket", website=s3.BucketWebsiteArgs(index_document="index.html")
    )
    index_content = content

    # Write our index.html into the site bucket
    s3.BucketObject(
        "index",
        bucket=site_bucket.id,
        content=index_content,
        key="index.html",
        content_type="text/html; charset=utf-8",
    )

    # Set the access policy for the bucket so all objects are readable
    s3.BucketPolicy(
        "bucket-policy",
        bucket=site_bucket.id,
        policy=site_bucket.id.apply(
            lambda id: json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": ["s3:GetObject"],
                        # Policy refers to bucket explicitly
                        "Resource": [f"arn:aws:s3:::{id}/*"],
                    },
                }
            )
        ),
    )

    # Export the website URL
    pulumi.export("website_url", site_bucket.website_endpoint)
    pulumi.export("website_content", index_content)
    pulumi.export("s3_bucket_resourece", site_bucket)


@bp.route("/new", methods=["GET"])
def create_site():

    return render_template("sites/create.html")