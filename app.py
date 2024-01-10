from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import io
import zipfile

app = Flask(__name__)

def compress_image(image, quality=85):
    img = Image.open(image.stream)
    img_io = io.BytesIO()

    if img.mode == "RGBA":
        rgb_img = img.convert("RGB")
        rgb_img.save(img_io, format="JPEG", quality=quality, optimize=True)
    else:
        img.save(img_io, format="JPEG", quality=quality, optimize=True)

    img_io.seek(0)
    return img_io

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("images")

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                filename = secure_filename(file.filename)
                if filename != "":
                    img_io = compress_image(file)
                    zipf.writestr(f"compressed_{filename}", img_io.getvalue())

        memory_file.seek(0)
        return send_file(
            memory_file,
            mimetype="application/zip",
            as_attachment=True,
            download_name="compressed_images.zip",
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
