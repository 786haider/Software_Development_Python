from fpdf import FPDF
import pandas as pd
from datetime import datetime
import io

class PDFGenerator:
    def __init__(self):
        self.company_name = "Hussain Construction"
        self.company_address = "Karachi, Sindh, Pakistan"
        self.company_phone = "+92-XXX-XXXXXXX"
        self.company_email = "info@hussainconstruction.com"
    
    def create_order_pdf(self, order_data, order_id):
        """Generate PDF for a single order"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=self.company_name, ln=1, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=self.company_address, ln=1, align='C')
        pdf.cell(200, 8, txt=f"Tel: {self.company_phone} | Email: {self.company_email}", ln=1, align='C')
        
        pdf.ln(10)
        
        # Title
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt=f"ORDER RECEIPT #{order_id}", ln=1, align='C')
        pdf.ln(5)
        
        # Order details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 8, txt="ORDER DETAILS", ln=1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", size=10)
        
        # Client information
        pdf.cell(50, 8, txt="Client Name:", border=0)
        pdf.cell(100, 8, txt=str(order_data[0]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Contact No:", border=0)
        pdf.cell(100, 8, txt=str(order_data[1]), border=0, ln=1)
        
        pdf.ln(3)
        
        # Order information
        pdf.cell(50, 8, txt="Item Type:", border=0)
        pdf.cell(100, 8, txt=str(order_data[2]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Quantity:", border=0)
        pdf.cell(100, 8, txt=str(order_data[3]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Quality:", border=0)
        pdf.cell(100, 8, txt=str(order_data[4]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Color:", border=0)
        pdf.cell(100, 8, txt=str(order_data[5]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Price:", border=0)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(100, 8, txt=str(order_data[6]), border=0, ln=1)
        pdf.set_font("Arial", size=10)
        
        pdf.cell(50, 8, txt="Provider:", border=0)
        pdf.cell(100, 8, txt=str(order_data[7]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Order Date:", border=0)
        pdf.cell(100, 8, txt=str(order_data[8]), border=0, ln=1)
        
        pdf.cell(50, 8, txt="Order Time:", border=0)
        pdf.cell(100, 8, txt=str(order_data[9]), border=0, ln=1)
        
        # Notes if available
        if len(order_data) > 10 and order_data[10]:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 10)
            pdf.cell(200, 8, txt="NOTES:", ln=1)
            pdf.set_font("Arial", size=10)
            # Handle long notes by splitting them
            notes = str(order_data[10])
            if len(notes) > 80:
                words = notes.split(' ')
                line = ""
                for word in words:
                    if len(line + word) > 80:
                        pdf.cell(200, 6, txt=line, ln=1)
                        line = word + " "
                    else:
                        line += word + " "
                if line:
                    pdf.cell(200, 6, txt=line, ln=1)
            else:
                pdf.cell(200, 8, txt=notes, ln=1)
        
        # Footer
        pdf.ln(20)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(200, 8, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
        pdf.cell(200, 8, txt="Thank you for choosing Hussain Construction!", ln=1, align='C')
        
        # Convert to bytes - FIXED VERSION
        try:
            # Use output() with 'S' destination to get bytes
            pdf_output = pdf.output(dest='S')
            
            # Handle different return types from fpdf2
            if isinstance(pdf_output, bytes):
                return pdf_output
            elif isinstance(pdf_output, bytearray):
                return bytes(pdf_output)  # Convert bytearray to bytes
            elif isinstance(pdf_output, str):
                return pdf_output.encode('latin1')  # Convert string to bytes
            else:
                # If it's some other type, try to convert to bytes
                return bytes(pdf_output)
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Alternative method using BytesIO
            try:
                buffer = io.BytesIO()
                pdf_str = pdf.output(dest='S')
                if isinstance(pdf_str, str):
                    buffer.write(pdf_str.encode('latin1'))
                elif isinstance(pdf_str, (bytes, bytearray)):
                    buffer.write(bytes(pdf_str))
                buffer.seek(0)
                return buffer.getvalue()
            except Exception as e2:
                print(f"Fallback PDF generation also failed: {e2}")
                return b"PDF generation failed"
    
    def create_summary_report(self, df):
        """Generate summary report PDF"""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=f"{self.company_name} - Summary Report", ln=1, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 8, txt=f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
        
        pdf.ln(10)
        
        # Statistics
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, txt="SUMMARY STATISTICS", ln=1)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        pdf.set_font("Arial", size=10)
        
        # Basic stats
        total_orders = len(df)
        unique_clients = df['client_name'].nunique() if not df.empty else 0
        
        pdf.cell(60, 8, txt="Total Orders:", border=0)
        pdf.cell(40, 8, txt=str(total_orders), border=0, ln=1)
        
        pdf.cell(60, 8, txt="Unique Clients:", border=0)
        pdf.cell(40, 8, txt=str(unique_clients), border=0, ln=1)
        
        if not df.empty:
            # Most common item type
            most_common_item = df['item_type'].mode().iloc[0] if not df['item_type'].mode().empty else "N/A"
            pdf.cell(60, 8, txt="Most Common Item:", border=0)
            pdf.cell(40, 8, txt=str(most_common_item), border=0, ln=1)
            
            # Date range
            min_date = df['order_date'].min()
            max_date = df['order_date'].max()
            pdf.cell(60, 8, txt="Date Range:", border=0)
            pdf.cell(40, 8, txt=f"{min_date} to {max_date}", border=0, ln=1)
        
        pdf.ln(10)
        
        # Top 10 clients
        if not df.empty:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 8, txt="TOP 10 CLIENTS", ln=1)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
            
            client_counts = df['client_name'].value_counts().head(10)
            
            pdf.set_font("Arial", "B", 10)
            pdf.cell(100, 8, txt="Client Name", border=1)
            pdf.cell(40, 8, txt="Orders", border=1, ln=1)
            
            pdf.set_font("Arial", size=9)
            for client, count in client_counts.items():
                pdf.cell(100, 6, txt=str(client)[:40], border=1)  # Truncate long names
                pdf.cell(40, 6, txt=str(count), border=1, ln=1)
        
        # Convert to bytes - FIXED VERSION
        try:
            # Use output() with 'S' destination to get bytes
            pdf_output = pdf.output(dest='S')
            
            # Handle different return types from fpdf2
            if isinstance(pdf_output, bytes):
                return pdf_output
            elif isinstance(pdf_output, bytearray):
                return bytes(pdf_output)  # Convert bytearray to bytes
            elif isinstance(pdf_output, str):
                return pdf_output.encode('latin1')  # Convert string to bytes
            else:
                # If it's some other type, try to convert to bytes
                return bytes(pdf_output)
        except Exception as e:
            print(f"Error generating PDF: {e}")
            # Alternative method using BytesIO
            try:
                buffer = io.BytesIO()
                pdf_str = pdf.output(dest='S')
                if isinstance(pdf_str, str):
                    buffer.write(pdf_str.encode('latin1'))
                elif isinstance(pdf_str, (bytes, bytearray)):
                    buffer.write(bytes(pdf_str))
                buffer.seek(0)
                return buffer.getvalue()
            except Exception as e2:
                print(f"Fallback PDF generation also failed: {e2}")
                return b"PDF generation failed"