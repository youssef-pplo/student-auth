import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_student_code():
    return "STU" + str(random.randint(100000, 999999))

def send_verification_email(to_email: str, generatedOtp: str):
    from_email = "noreply@easybio.com"
    subject = "رمز التحقق الخاص بك"

    html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
      <meta charset="UTF-8">
      <title>رمز التحقق</title>
    </head>
    <body style="margin:0; padding:0; font-family:'Arial', sans-serif; background:#f9f9f9;">
      <div style="max-width:600px; margin:30px auto; background:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.1);">
        <div style="background:linear-gradient(90deg, #E93B81, #6C63FF); padding:20px; text-align:center; color:white;">
          <h1 style="margin:0; font-size:28px;">رمز التحقق الخاص بك</h1>
        </div>
        <div style="padding:30px; text-align:center;">
          <p style="font-size:18px; margin-bottom:20px;">شكرًا لتسجيلك في <strong>Easy Bio</strong></p>
          <p style="font-size:16px; margin-bottom:20px;">رمز التحقق الخاص بك هو:</p>
          <div style="font-size:40px; font-weight:bold; letter-spacing:10px; color:#6C63FF;">{generatedOtp}</div>
          <p style="margin-top:30px; font-size:14px; color:#555;">إذا لم تطلب هذا الرمز، يمكنك تجاهل هذه الرسالة.</p>
        </div>
        <div style="background:#f0f0f0; padding:20px; text-align:center; font-size:13px; color:#888;">
          &copy; 2025 Easy Bio — جميع الحقوق محفوظة
        </div>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    msg.attach(MIMEText(html, "html"))

    try:
        server = smtplib.SMTP("mail.easybio.com", 587)
        server.starttls()
        server.login(from_email, "your_email_password")
        server.sendmail(from_email, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email sending failed:", e)
