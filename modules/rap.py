from flask import Blueprint, render_template
import database

rap_bp = Blueprint('rap', __name__)

@rap_bp.route('/')
def index():
    query = "SELECT MaPhong, TenPhong, MaCumRap, SucChua FROM PhongChieu"
    results = database.fetch_all(query)
    
    return render_template('rap/index.html', title="Cơ Sở Vật Chất", ds_phong=results)
