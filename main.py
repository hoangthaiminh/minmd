from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import httpx

app = FastAPI()

# # Cho phép gọi từ bất kỳ domain nào
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCKAPI_URL = "https://68077c21e81df7060eba7c78.mockapi.io/api/v1/viewerCounter/2"

# # Hàm tạo ảnh từ text
def create_text_image(text="", font_size=40, height=80):
    font_path = os.path.join(os.path.dirname(__file__), "Roboto-Regular.ttf")
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)
    text_bbox = dummy_draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    total_width = text_width + 20

    image = Image.new("RGB", (total_width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    y_pos = (height - font_size) // 2
    draw.text((10, y_pos), text, font=font, fill=(0, 0, 0))
    return image

# # Lấy dữ liệu hiện tại từ mockapi
async def fetch_data():
    async with httpx.AsyncClient() as client:
        res = await client.get(MOCKAPI_URL)
        return res.json()

# # Gửi dữ liệu cập nhật lên mockapi
async def update_data(data):
    async with httpx.AsyncClient() as client:
        await client.put(MOCKAPI_URL, json=data)

# # / → tăng view và trả ảnh
@app.get("/")
async def view_counter():
    data = await fetch_data()
    data["view_cnt"] = int(data.get("view_cnt", 0)) + 1
    await update_data(data)

    img = create_text_image(f"Lượt xem: {data['view_cnt']}")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="image/jpeg")

# # /like → chỉ trả ảnh số like hiện tại
@app.get("/like")
async def like_image():
    data = await fetch_data()
    img = create_text_image(f"Lượt thích: {data['like_cnt']}")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="image/jpeg")

# # /likebtn → tăng like, trả HTML cảm ơn
@app.get("/likebtn")
async def like_button():
    data = await fetch_data()
    data["like_cnt"] = int(data.get("like_cnt", 0)) + 1
    await update_data(data)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Like thành công</title>
    </head>
    <body>
        <strong>Cảm ơn bạn đã thích, hãy quay lại và reload lại trang bạn nhé</strong>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/load")
async def reloadbtn():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Start thành công</title>
    </head>
    <body>
        <h2><b>Khởi động thành công</b></h2>
        <strong>Khởi động máy chủ thành công!</strong>
        <strong>Hãy quay lại trang thông tin của mình và reload lại bạn nhé!</strong>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
