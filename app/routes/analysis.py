from flask import Blueprint, request, jsonify
from ..models import Device, Measurement, Analysis, db
from sqlalchemy import desc
from datetime import datetime

bp = Blueprint('analysis', __name__)


@bp.route('', methods=['GET'])
def get_analysis():
    return "working in progress"



@bp.route('', methods=['POST'])
def create_analysis():
    """
    lấy thông tin ngày nào cần tạo phân tích từ args
    lấy thông tin clientid nào cần phân tích từ args
    lấy thông tin slope, che phủ, tọa độm ... của client thông qua Device class
    lấy thông tin measurement từ Measurement (xem cách query)
    => phân tích nguy cơ sạt lở 
    => lưu lại vào trong Analysis db (xem create_device)
    """
    return