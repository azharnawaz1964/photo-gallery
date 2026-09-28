import os
import uuid
import io

from flask import Flask, request, render_template_string, send_file, redirect
from google.cloud import storage
from google.cloud import firestore

app = Flask(__name__)

storage_client = storage.Client()
firestore_client = firestore.Client()

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
cd phot*
            cursor: pointer;
        }

        /* Lightbox Modal */
        .modal { display: none; position: fixed; z-index: 1000; padding-top: 100px; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.9); }
        .modal-content { margin: auto; display: block; max-width: 80%; max-height: 80%; border-radius: 10px; }
        .close { position: absolute; top: 15px; right: 35px; color: #fff; font-size: 40px; font-weight: bold; cursor: pointer; }
    </style>
</head>

<body>

<h1>📸 Community Photo Gallery</h1>

<div class="upload-box">

    <h2>Upload a photo</h2>

    <form method="POST" enctype="multipart/form-data">

        <!-- Unique ID for this upload attempt -->
        <input
            type="hidden"
            name="upload_id"
            value="{{ upload_id }}"
        >

        <input
            type="text"
            name="uploader"
            placeholder="Your name"
            required
        >

        <br><br>

        <input
            type="text"
            name="caption"
            placeholder="Photo caption"
            required
        >

        <br><br>

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

        <img src="/image/{{ photo.filename }}" onclick="openModal(this.src)">

        <h3>{{ photo.caption }}</h3>

        <p>
            Uploaded by: {{ photo.uploader }}
        </p>

    </div>

{% endfor %}

</div>

<div id="imageModal" class="modal" onclick="this.style.display='none'">
    <span class="close">&times;</span>
    <img class="modal-content" id="fullImage">
</div>

<script>
function openModal(src) {
    const modal = document.getElementById("imageModal");
    const modalImg = document.getElementById("fullImage");
    modal.style.display = "block";
    modalImg.src = src;
}
</script>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def gallery():

    bucket = storage_client.bucket(BUCKET_NAME)

    if request.method == "POST":

        photo = request.files.get("photo")

        uploader = request.form.get(
            "uploader", ""
        ).strip()

        caption = request.form.get(
            "caption", ""
        ).strip()

        upload_id = request.form.get(
            "upload_id", ""
        ).strip()

        if photo and photo.filename and upload_id:

            # Use the upload ID as the Firestore document ID.
            photo_ref = firestore_client.collection(
                "photos"
            ).document(upload_id)

            # Check whether this upload has already
            # been processed.
            existing = photo_ref.get()

            if not existing.exists:

                extension = os.path.splitext(
                    photo.filename
                )[1].lower()

                filename = f"{upload_id}{extension}"

                blob = bucket.blob(filename)

                blob.upload_from_file(
                    photo,
                    content_type=photo.content_type
                )

                photo_ref.set({
                    "filename": filename,
                    "caption": caption,
                    "uploader": uploader,
                    "bucket": BUCKET_NAME,
                    "content_type": photo.content_type,
                    "uploaded_at":
                        firestore.SERVER_TIMESTAMP
                })

            # IMPORTANT:
            # Always redirect after POST.
            return redirect("/")

    photos = []

    photos_ref = (
        firestore_client
        .collection("photos")
        .order_by(
            "uploaded_at",
            direction=firestore.Query.DESCENDING
        )
    )

    for doc in photos_ref.stream():

        data = doc.to_dict()

        photos.append(data)

    return render_template_string(
        HTML,
        photos=photos,
        upload_id=str(uuid.uuid4())
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
