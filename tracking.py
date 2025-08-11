# app.py
from flask import Flask, request, render_template, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PyPDF2 import PdfWriter, PdfReader
import io
from PIL import Image
from datetime import datetime

tracking = Flask(__name__)

@tracking.route('/')
def tack():
    return render_template('tracking.html')

if __name__ == '__main__':
    tracking.run(debug=True)
