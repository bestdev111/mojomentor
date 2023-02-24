import io
from datetime import datetime
from django.http import FileResponse
from reportlab.pdfgen import canvas
from mentor.settings import BASE_DIR


# common setting for creating pdf
logo = str(BASE_DIR) + "/static/images/logo-pic.png"
LEFT_MAR = 30


def generate_invoice():
     # Create a file-like buffer to receive PDF data.
     buffer = io.BytesIO()

     # Create the PDF object, using the buffer as its "file."
     p = canvas.Canvas(buffer)

     # Draw things on the PDF.
     # ------------------------------------------------
     # for testing boundaries
     # p.drawString(0, 0, "*")
     # p.drawString(0, 830, "*")
     # p.drawString(590, 0, "*")
     # p.drawString(590, 830, "*")
     # for document title
     p.setTitle("Invoce - MojoMentors")
     # p.drawInlineImage(logo, 251.564, 795, width=86.872, height=50)

     # brand logo
     p.drawInlineImage(logo, LEFT_MAR, 795, width=159.375, height=30)
     # right corner text
     p.setFontSize(14)
     p.drawRightString(565, 812, "Sonu Sah")
     p.setFontSize(11)
     p.drawRightString(565, 800, "rsonukumar154@gmail.com")

     # drawing ribbons
     p.setFillColorRGB(0.972, 0.462, 0.070)
     p.rect(0, 765, 400, 20, stroke=0, fill=1)
     p.setFillColorRGB(0.572, 0.192, 0.855)
     p.rect(520, 765, 75, 20, stroke=0, fill=1)

     p.setFillColorRGB(0, 0, 0)
     p.setFontSize(27)
     p.drawString(405, 765, "INVOICE")

     p.setFontSize(20)
     p.drawString(LEFT_MAR, 740, "Invoice to: ")

     p.setFontSize(16)
     p.drawString(LEFT_MAR, 715, "Sonu Sah")

     p.drawString(380, 715, "Invoice#")
     p.drawString(380, 695, "Date")

     p.setFontSize(14)
     p.setFillColorRGB(0.31, 0.31, 0.31)
     p.drawString(LEFT_MAR, 700, "rsonukumar154@gmail.com")

     p.drawRightString(565, 715, "01")
     p.drawRightString(565, 695, "25/12/2022")

     p.setFontSize(20)
     p.setFillColorRGB(0, 0, 0)
     p.drawString(LEFT_MAR, 640, "Product details: ")

     p.setFontSize(16)
     p.setFillColorRGB(0.31, 0.31, 0.31)
     p.drawString(LEFT_MAR, 620, "Testing Course")

     p.setFillColorRGB(0.972, 0.462, 0.070)
     p.rect(340, 500, 255, 30, stroke=0, fill=1)

     p.setFontSize(16)
     p.setFillColorRGB(0, 0, 0)
     p.drawString(350, 560, "Price: ")
     p.drawString(350, 540, "Coupon Discount: ")
     p.setFillColorRGB(1, 1, 1)
     p.drawString(350, 510, "Amount Paid")

     p.setFontSize(14)
     p.setFillColorRGB(0.31, 0.31, 0.31)
     p.drawRightString(565, 560, "$50")
     p.drawRightString(565, 540, "$5")
     p.setFillColorRGB(1, 1, 1)
     p.drawRightString(565, 510, "$42")

     p.setFillColorRGB(0.31, 0.31, 0.31)
     p.drawString(LEFT_MAR, 560, "Thank you so much for shopping.")
     p.drawString(LEFT_MAR, 545, "Have a great day.")

     # p.showPage()
     # p.roundRect(15, 625, 250, 125, 4, stroke=1, fill=1)

     # ------------------------------------------------

     # Close the PDF object cleanly, and we're done.
     p.showPage()
     p.save()

     # FileResponse sets the Content-Disposition header so that browsers
     # present the option to save the file.
     buffer.seek(0)
     return FileResponse(buffer, as_attachment=True, filename='invoice.pdf')
