import os
import uuid
import io

from flask import Flask, request, render_template_string, send_file
from google.cloud import storage

app = Flask(__name__)

storage_client = storage.Client()

BUCKET_NAME = os.environ.get("BUCKET_NAME")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Community Photo Gallery</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1000px;
            margin: 40px auto;
            padding: 20px;
            background: #f5f7fa;
        }

        h1 {
            text-align: center;
        }

        .upload-box {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }

        input[type="file"] {
            margin: 15px 0;
        }

        button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .gallery {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
        }

        .photo {
            background: white;
            padding: 10px;
            border-radius: 10px;
        }

        .photo img {
            width: 100%;
            height: 220px;
            object-fit: cover;
            border-radius: 8px;
        }
    </style>
</head>

<body>

<h1>📸 Community Photo Gallery</h1>

<div class="upload-box">

    <h2>Upload a photo</h2>

    <form method="POST" enctype="multipart/form-data">

        <input
            type="file"
            name="photo"
            accept="image/*"
            required
        >

        <br>

        <button type="submit">
            Upload Photo
        </button>

    </form>

</div>

<h2>Gallery</h2>

<div class="gallery">

{% for photo in photos %}

    <div class="photo">

        <img src="/image/{{ photo }}">

    </div>

{% endfor %}

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def gallery():

    bucket = storage_client.bucket(BUCKET_NAME)

    if request.method == "POST":

        photo = request.files.get("photo")

        if photo and photo.filename:

            extension = os.path.splitext(
                photo.filename
            )[1].lower()

            filename = f"{uuid.uuid4()}{extension}"

            blob = bucket.blob(filename)

            blob.upload_from_file(
                photo,
                content_type=photo.content_type
            )

    photos = [
        blob.name
        for blob in storage_client.list_blobs(
            BUCKET_NAME
        )
    ]

    return render_template_string(
        HTML,
        photos=photos
    )


@app.route("/image/<filename>")
def image(filename):

    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob(filename)

    image_data = blob.download_as_bytes()

    return send_file(
        io.BytesIO(image_data),
        mimetype=blob.content_type
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8080))
    )

