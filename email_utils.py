import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

class EmailService:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = None
        self.sender_password = None
        self.is_configured = False
        self.currency_symbol = "₱"
        
        # Load credentials
        self._load_credentials()
    
    def _load_credentials(self):
        """Load email credentials with multiple fallback options"""
        try:
            print("🔧 Attempting to load email credentials...")
            
            # Option 1: Direct hardcoded credentials (for quick testing)
            self.sender_email = "jakeyshin127@gmail.com"
            self.sender_password = "wvto sxpd glze yoqx"
            
            if self.sender_email and self.sender_password:
                self.is_configured = True
                print("✅ Email credentials loaded from hardcoded values")
                print(f"📧 Sender email: {self.sender_email}")
                print(f"🔐 Password: {'*' * len(self.sender_password)}")
                return
            
            # Option 2: Streamlit secrets (for deployment)
            try:
                if hasattr(st, 'secrets') and 'email' in st.secrets:
                    self.sender_email = st.secrets['email']['username']
                    self.sender_password = st.secrets['email']['password']
                    if self.sender_email and self.sender_password:
                        self.is_configured = True
                        print("✅ Email credentials loaded from Streamlit secrets")
                        return
            except Exception as e:
                print(f"❌ Streamlit secrets error: {e}")
            
            # Option 3: Environment variables
            self.sender_email = os.getenv('GMAIL_USERNAME')
            self.sender_password = os.getenv('GMAIL_PASSWORD')
            
            if self.sender_email and self.sender_password:
                self.is_configured = True
                print("✅ Email credentials loaded from environment variables")
                return
                
            print("❌ No email credentials found in any source")
            self.is_configured = False
            
        except Exception as e:
            print(f"❌ Error loading email credentials: {e}")
            self.is_configured = False
    
    def set_currency_symbol(self, symbol):
        """Set currency symbol"""
        self.currency_symbol = symbol
        print(f"💰 Currency symbol set to: {symbol}")
    
    def test_connection(self):
        """Test SMTP connection"""
        if not self.is_configured:
            print("❌ Email service not configured")
            return False
        
        try:
            print("🔧 Testing SMTP connection...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                print("✅ SMTP connection successful!")
                return True
        except Exception as e:
            print(f"❌ SMTP connection failed: {e}")
            return False
    
    def send_otp_email(self, recipient_email, customer_name, otp_code, transaction_type, amount, description, due_date=None):
        """Send OTP email to customer"""
        if not self.is_configured:
            print("❌ Email service not configured - cannot send OTP")
            return False
        
        # Test connection first
        if not self.test_connection():
            print("❌ Cannot send email - connection test failed")
            return False
        
        try:
            print(f"📧 Attempting to send OTP email to: {recipient_email}")
            
            # Create message
            subject = f"IUMS - OTP Verification for {transaction_type.title()}"
            
            # Build email body
            if transaction_type == "utang":
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2c5aa0; text-align: center;">IUMS - Utang Verification</h2>
                        
                        <p>Dear <strong>{customer_name}</strong>,</p>
                        
                        <p>A new utang transaction requires your verification:</p>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <h3 style="color: #d9534f; margin-top: 0;">Transaction Details:</h3>
                            <p><strong>Description:</strong> {description}</p>
                            <p><strong>Amount:</strong> {self.currency_symbol} {amount:,.2f}</p>
                            {f'<p><strong>Due Date:</strong> {due_date}</p>' if due_date else ''}
                            <p><strong>Transaction Type:</strong> New Utang</p>
                        </div>
                        
                        <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                            <h3 style="color: #856404; margin-top: 0;">Your Verification Code</h3>
                            <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #d9534f; background: #fff; padding: 10px; border-radius: 5px; border: 2px dashed #d9534f;">
                                {otp_code}
                            </div>
                            <p style="color: #856404; margin-top: 10px;">
                                <strong>Please provide this OTP to the owner to confirm the transaction.</strong>
                            </p>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                            <p style="color: #666; font-size: 12px;">
                                <strong>Security Notice:</strong> Never share this OTP with anyone except the authorized owner/staff. 
                                This code will expire after use.
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """
            else:  # payment
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                        <h2 style="color: #2c5aa0; text-align: center;">IUMS - Payment Verification</h2>
                        
                        <p>Dear <strong>{customer_name}</strong>,</p>
                        
                        <p>A payment transaction requires your verification:</p>
                        
                        <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                            <h3 style="color: #28a745; margin-top: 0;">Transaction Details:</h3>
                            <p><strong>Description:</strong> {description}</p>
                            <p><strong>Amount:</strong> {self.currency_symbol} {amount:,.2f}</p>
                            <p><strong>Transaction Type:</strong> Payment</p>
                        </div>
                        
                        <div style="background: #d4edda; padding: 15px; border-radius: 5px; margin: 20px 0; text-align: center;">
                            <h3 style="color: #155724; margin-top: 0;">Your Verification Code</h3>
                            <div style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #155724; background: #fff; padding: 10px; border-radius: 5px; border: 2px dashed #28a745;">
                                {otp_code}
                            </div>
                            <p style="color: #155724; margin-top: 10px;">
                                <strong>Please provide this OTP to the owner to confirm the payment.</strong>
                            </p>
                        </div>
                        
                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd;">
                            <p style="color: #666; font-size: 12px;">
                                <strong>Security Notice:</strong> Never share this OTP with anyone except the authorized owner/staff. 
                                This code will expire after use.
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"IUMS System <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ OTP email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending OTP email: {e}")
            return False
    
    def send_due_date_reminder(self, recipient_email, customer_name, description, amount, due_date, days_until_due):
        """Send due date reminder email"""
        if not self.is_configured:
            print("❌ Email service not configured")
            return False
        
        try:
            subject = f"IUMS - Due Date Reminder"
            
            if days_until_due < 0:
                status = "OVERDUE"
                color = "#dc3545"
            elif days_until_due == 0:
                status = "DUE TODAY"
                color = "#dc3545"
            elif days_until_due <= 3:
                status = "DUE SOON"
                color = "#fd7e14"
            else:
                status = "UPCOMING"
                color = "#ffc107"
            
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #2c5aa0; text-align: center;">IUMS - Due Date Reminder</h2>
                    
                    <p>Dear <strong>{customer_name}</strong>,</p>
                    
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid {color};">
                        <h3 style="color: {color}; margin-top: 0;">{status}</h3>
                        <p><strong>Description:</strong> {description}</p>
                        <p><strong>Amount:</strong> {self.currency_symbol} {amount:,.2f}</p>
                        <p><strong>Due Date:</strong> {due_date}</p>
                        <p><strong>Status:</strong> 
                            <span style="color: {color}; font-weight: bold;">
                                {f"{abs(days_until_due)} days overdue" if days_until_due < 0 else f"Due in {days_until_due} days"}
                            </span>
                        </p>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h4 style="color: #856404; margin-top: 0;">Action Required</h4>
                        <p>Please coordinate with the owner to settle this utang.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart()
            msg['From'] = f"IUMS System <{self.sender_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Due date reminder sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending due date reminder: {e}")
            return False

# Create global instance
email_service = EmailService()

# Test on import
print("🔧 Initializing Email Service...")
print(f"📧 Email service configured: {email_service.is_configured}")
if email_service.is_configured:
    email_service.test_connection()