# Application Configuration

# App Settings
APP_TITLE = "Hussain Construction Point- Order Management System"
APP_ICON = "🏗️"
COMPANY_NAME = "Hussain Construction Point"
COMPANY_TAGLINE = "Building Dreams, Creating Reality"
PAGE_LAYOUT = "wide"

# Color Scheme
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'accent': '#F18F01',
    'success': '#C73E1D',
    'info': '#5DADE2',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'gradient_start': '#2E86AB',
    'gradient_end': '#A23B72',
    'other': 'any other color'
}

# Form Options
ITEM_TYPES = [
    "Cement Bags",
    "Steel Rods",
    "Bricks",
    "Sand",
    "Gravel",
    "Concrete Blocks",
    "Tiles",
    "Paint",
    "Pipes",
    "Electrical Wires",
    "Doors",
    "Windows",
    "Roofing Materials",
    "Insulation",
    "Tools & Equipment"
]

QUALITY_OPTIONS = [
    "Premium",
    "Standard", 
    "Basic",
    "Economy"
]

COLOR_OPTIONS = [
    "Natural",
    "White",
    "Grey", 
    "Brown",
    "Red",
    "Blue",
    "Green",
    "Yellow",
    "Black",
    "Mixed"
]

# Messages
MESSAGES = {
    'login_success': "✅ Login successful! Welcome to the dashboard.",
    'login_failed': "❌ Invalid username or password. Please try again.",
    'fields_required': "⚠️ Please fill in all required fields.",
    'order_created': "✅ Order created successfully!",
    'order_updated': "✅ Order updated successfully!",
    'no_data': "📋 No orders found. Create your first order to get started!"
}

# Recovery Emails (for password reset)
RECOVERY_EMAILS = [
    "haiderhussain536@gmail.com",
    "mutahirhussain619@gmail.com"
]

# Database Settings
DATABASE_NAME = "orders.db"

# PDF Settings
PDF_SETTINGS = {
    'company_name': COMPANY_NAME,
    'company_address': "Karachi, Sindh, Pakistan",
    'company_phone': "+92-XXX-XXXXXXX",
    'company_email': "info@hussainconstruction.com"
}