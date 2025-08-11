import streamlit as st
import pandas as pd
from datetime import datetime, date, time
import base64
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Import custom modules
from database import DatabaseManager
from pdf_generator import PDFGenerator
from config import *

# Set page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="collapsed"
)

# Initialize components
# NO caching - direct initialization
def get_db_manager():
    return DatabaseManager()

def get_pdf_generator():
    return PDFGenerator()

# Initialize without caching
db = get_db_manager()
pdf_gen = get_pdf_generator()

# Custom CSS for enhanced styling
st.markdown(f"""
<style>
    .main-header {{
        text-align: center;
        color: {COLORS['primary']};
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }}
    .sub-header {{
        text-align: center;
        color: {COLORS['secondary']};
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }}
    .login-container {{
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background-color: #f8f9fa;
    }}
    .dashboard-card {{
        background: linear-gradient(135deg, {COLORS['gradient_start']} 0%, {COLORS['gradient_end']} 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        cursor: pointer;
        transition: transform 0.3s ease;
    }}
    .dashboard-card:hover {{
        transform: translateY(-5px);
    }}
    .stats-card {{
        background: linear-gradient(135deg, {COLORS['info']} 0%, {COLORS['primary']} 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }}
    .form-container {{
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }}
    .success-message {{
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }}
    .warning-message {{
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }}
    .error-message {{
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }}
    .metric-card {{
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {COLORS['primary']};
    }}
</style>
""", unsafe_allow_html=True)

def login_page():
    """Enhanced login page with better UX"""
    st.markdown(f'<h1 class="main-header">{APP_ICON} {COMPANY_NAME}</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">{COMPANY_TAGLINE}</p>', unsafe_allow_html=True)
    
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            st.markdown("### 🔐 Admin Login")
            
            with st.form("login_form"):
                username = st.text_input("👤 Username", value="admin", disabled=True)
                password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
                
                col_login, col_forgot = st.columns(2)
                
                with col_login:
                    login_clicked = st.form_submit_button("🚀 Login", use_container_width=True)
                
                with col_forgot:
                    forgot_clicked = st.form_submit_button("😥 Forgot Password", use_container_width=True)
            
            if login_clicked:
                if password:
                    user = db.verify_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_info = {
                            'id': user[0],
                            'username': user[1],
                            'email': user[2],
                            'full_name': user[3] if len(user) > 3 else 'Admin',
                            'role': user[4] if len(user) > 4 else 'admin'
                        }
                        st.session_state.page = "dashboard"
                        st.success(MESSAGES['login_success'])
                        st.rerun()
                    else:
                        st.error(MESSAGES['login_failed'])
                else:
                    st.error("Please enter a password")
            
            if forgot_clicked:
                st.session_state.page = "forgot_password"
                st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

def forgot_password_page():
    """Enhanced forgot password page"""
    st.markdown('<h1 class="main-header">🔐 Password Recovery</h1>', unsafe_allow_html=True)
    
    st.info("📧 Password recovery information will be sent to the registered email addresses:")
    
    for email in RECOVERY_EMAILS:
        st.write(f"• {email}")
    
    st.warning("⚠️ Please contact the system administrator for password reset assistance.")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col2:
            if st.button("🔙 Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

def dashboard_page():
    """Enhanced dashboard with statistics and analytics"""
    st.markdown(f'<h1 class="main-header">{APP_ICON} {COMPANY_NAME}</h1>', unsafe_allow_html=True)
    
    # Welcome message
    user_name = st.session_state.user_info.get('full_name', 'Admin')
    st.markdown(f'<p class="sub-header">Welcome back, {user_name}! 👋</p>', unsafe_allow_html=True)
    
    # Get dashboard statistics
    stats = db.get_dashboard_stats()
    
    # Display statistics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📊 Total Orders</h3>
            <h2>{stats.get('total_orders', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📅 Today's Orders</h3>
            <h2>{stats.get('orders_today', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>📈 This Month</h3>
            <h2>{stats.get('orders_this_month', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>👥 Total Clients</h3>
            <h2>{stats.get('total_clients', 0)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Navigation cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📝 Create New Order", key="create_order", use_container_width=True):
            st.session_state.page = "admin_panel"
            st.rerun()
    
    with col2:
        if st.button("📊 View All Orders", key="view_orders", use_container_width=True):
            st.session_state.page = "previous_data"
            st.rerun()
    
    with col3:
        if st.button("📈 Analytics", key="analytics", use_container_width=True):
            st.session_state.page = "analytics"
            st.rerun()
    
    # Recent orders preview
    st.markdown("### 🕒 Recent Orders")
    recent_orders = db.get_all_orders().head(5)
    
    if not recent_orders.empty:
        st.dataframe(
            recent_orders[['id', 'client_name', 'item_type', 'quantity', 'prize', 'order_date']],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(MESSAGES['no_data'])
    
    # Logout section
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def admin_panel_page():
    """Enhanced admin panel with better form handling"""
    st.markdown('<h1 class="main-header">📝 Create New Order</h1>', unsafe_allow_html=True)
    
    with st.form("order_form", clear_on_submit=True):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("👤 Client Name *", placeholder="Enter client name")
            contact_no = st.text_input("📞 Contact No *", placeholder="Enter contact number")
            
            # Use selectbox for item type with custom option
            item_type_options = ITEM_TYPES + ["Custom"]
            item_type_selected = st.selectbox("📦 Item Type *", item_type_options)
            if item_type_selected == "Custom":
                item_type = st.text_input("Enter custom item type", placeholder="Specify item type")
            else:
                item_type = item_type_selected
            
            quantity = st.text_input("📊 Quantity *", placeholder="Enter quantity with unit")
            
            # Use selectbox for quality
            quality = st.selectbox("⭐ Quality *", QUALITY_OPTIONS)
        
        with col2:
            # Use selectbox for color with custom option
            color_options = COLOR_OPTIONS + ["Custom"]
            color_selected = st.selectbox("🎨 Color *", color_options)
            if color_selected == "Custom":
                color = st.text_input("Enter custom color", placeholder="Specify color")
            else:
                color = color_selected
            
            prize = st.text_input("💰 Price *", placeholder="Enter price (e.g., Rs. 5000)")
            provider = st.text_input("🏢 Provider *", placeholder="Enter provider/supplier name")
            order_date = st.date_input("📅 Date *", value=date.today())
            order_time = st.time_input("🕐 Time *", value=datetime.now().time())
        
        # Additional notes
        notes = st.text_area("📝 Notes (Optional)", placeholder="Additional notes or specifications")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_submit, col_back = st.columns(2)
        
        with col_submit:
            submitted = st.form_submit_button("✅ Create Order", use_container_width=True)
        
        with col_back:
            if st.form_submit_button("🔙 Back to Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
    
    if submitted:
        # Validate required fields
        required_fields = [client_name, contact_no, item_type, quantity, quality, color, prize, provider]
        if all(field for field in required_fields):
            order_data = (
                client_name, contact_no, item_type, quantity, quality,
                color, prize, provider, str(order_date), str(order_time), notes
            )
            
            order_id = db.save_order(order_data)
            if order_id:
                st.session_state.current_order = {
                    'id': order_id,
                    'data': order_data
                }
                st.session_state.page = "order_preview"
                st.rerun()
            else:
                st.error("❌ Error creating order. Please try again.")
        else:
            st.error(MESSAGES['fields_required'])

def order_preview_page():
    """Enhanced order preview with better formatting"""
    st.markdown('<h1 class="main-header">📋 Order Preview</h1>', unsafe_allow_html=True)
    
    if 'current_order' in st.session_state:
        order = st.session_state.current_order
        order_data = order['data']
        order_id = order['id']
        
        # Success message
        st.markdown(f'<div class="success-message">{MESSAGES["order_created"]} Order ID: #{order_id}</div>', 
                   unsafe_allow_html=True)
        
        # Display order details in a nice format
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 👤 Client Information")
            st.write(f"**Name:** {order_data[0]}")
            st.write(f"**Contact:** {order_data[1]}")
            
            st.markdown("#### 📦 Order Details")
            st.write(f"**Item Type:** {order_data[2]}")
            st.write(f"**Quantity:** {order_data[3]}")
            st.write(f"**Quality:** {order_data[4]}")
        
        with col2:
            st.markdown("#### 💰 Pricing & Provider")
            st.write(f"**Color:** {order_data[5]}")
            st.write(f"**Price:** {order_data[6]}")
            st.write(f"**Provider:** {order_data[7]}")
            
            st.markdown("#### 📅 Timing")
            st.write(f"**Date:** {order_data[8]}")
            st.write(f"**Time:** {order_data[9]}")
        
        if len(order_data) > 10 and order_data[10]:
            st.markdown("#### 📝 Notes")
            st.write(order_data[10])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Generate PDF
            pdf_bytes = pdf_gen.create_order_pdf(order_data, order_id)
            st.download_button(
                label="🖨️ Download PDF",
                data=pdf_bytes,
                file_name=f"Order_{order_id}_{order_data[0].replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with col2:
            if st.button("📝 Create Another Order", use_container_width=True):
                st.session_state.page = "admin_panel"
                st.rerun()
        
        with col3:
            if st.button("🔙 Back to Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()

def previous_data_page():
    """Enhanced data view with search and filtering"""
    st.markdown('<h1 class="main-header">📊 Orders Management</h1>', unsafe_allow_html=True)
    
    # Search and filter section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search Orders", placeholder="Search by client, contact, or item...")
    
    with col2:
        status_filter = st.selectbox("📋 Filter by Status", ["All", "Active", "Deleted"])
    
    with col3:
        if st.button("🔙 Back to Dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Get orders based on filters
    if search_term:
        df = db.search_orders(search_term)
    else:
        status = None if status_filter == "All" else status_filter
        df = db.get_all_orders(status)
    
    if not df.empty:
        st.markdown(f"**Found {len(df)} orders**")
        
        # Display orders with action buttons
        for idx, row in df.iterrows():
            with st.expander(f"Order #{row['id']} - {row['client_name']} ({row['order_date']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Client:** {row['client_name']}")
                    st.write(f"**Contact:** {row['contact_no']}")
                    st.write(f"**Item:** {row['item_type']}")
                    st.write(f"**Quantity:** {row['quantity']}")
                
                with col2:
                    st.write(f"**Quality:** {row['quality']}")
                    st.write(f"**Color:** {row['color']}")
                    st.write(f"**Price:** {row['prize']}")
                    st.write(f"**Provider:** {row['provider']}")
                
                with col3:
                    st.write(f"**Date:** {row['order_date']}")
                    st.write(f"**Time:** {row['order_time']}")
                    st.write(f"**Status:** {row.get('status', 'Active')}")
                    
                    # Action buttons
                    col_pdf, col_edit, col_delete = st.columns(3)
                    
                    with col_pdf:
                        order_data = (row['client_name'], row['contact_no'], row['item_type'], 
                                    row['quantity'], row['quality'], row['color'], row['prize'], 
                                    row['provider'], row['order_date'], row['order_time'], 
                                    row.get('notes', ''))
                        pdf_bytes = pdf_gen.create_order_pdf(order_data, row['id'])
                        st.download_button(
                            label="📄 PDF",
                            data=pdf_bytes,
                            file_name=f"Order_{row['id']}.pdf",
                            mime="application/pdf",
                            key=f"pdf_{row['id']}"
                        )
                    
                    with col_edit:
                        if st.button("✏️ Edit", key=f"edit_{row['id']}"):
                            st.session_state.edit_order_id = row['id']
                            st.session_state.page = "edit_order"
                            st.rerun()
                    
                    with col_delete:
                        if row.get('status', 'Active') != 'Deleted':
                            if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                                if db.delete_order(row['id']):
                                    st.success("Order deleted successfully!")
                                    st.rerun()
        
        # Bulk operations
        st.markdown("---")
        st.markdown("### 📥 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV export
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv,
                file_name=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # Summary report
            if st.button("📈 Generate Summary Report"):
                pdf_bytes = pdf_gen.create_summary_report(df)
                st.download_button(
                    label="📄 Download Report",
                    data=pdf_bytes,
                    file_name=f"summary_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        
        with col3:
            # Database backup
            if st.button("💾 Backup Database"):
                backup_path = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                if db.backup_database(backup_path):
                    st.success(f"Database backed up to {backup_path}")
                else:
                    st.error("Backup failed!")
    
    else:
        st.info(MESSAGES['no_data'])

def analytics_page():
    """Analytics dashboard with charts and insights"""
    st.markdown('<h1 class="main-header">📈 Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    if st.button("🔙 Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Get all orders for analytics
    df = db.get_all_orders()
    
    if not df.empty:
        # Convert date columns for better plotting
        df['order_date'] = pd.to_datetime(df['order_date'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_orders = len(df)
            st.metric("Total Orders", total_orders)
        
        with col2:
            total_revenue = df['prize'].str.replace(r'[^\d.]', '', regex=True).astype(float).sum()
            st.metric("Total Revenue", f"Rs. {total_revenue:,.0f}")
        
        with col3:
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            st.metric("Avg Order Value", f"Rs. {avg_order_value:,.0f}")
        
        with col4:
            unique_clients = df['client_name'].nunique()
            st.metric("Unique Clients", unique_clients)
        
        st.markdown("---")
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Orders by Item Type")
            item_counts = df['item_type'].value_counts()
            fig_pie = px.pie(
                values=item_counts.values,
                names=item_counts.index,
                title="Distribution of Item Types"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Orders Over Time")
            daily_orders = df.groupby(df['order_date'].dt.date).size().reset_index()
            daily_orders.columns = ['Date', 'Orders']
            
            fig_line = px.line(
                daily_orders,
                x='Date',
                y='Orders',
                title="Daily Order Trend"
            )
            st.plotly_chart(fig_line, use_container_width=True)
        
        # Quality and Provider analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⭐ Quality Distribution")
            quality_counts = df['quality'].value_counts()
            fig_bar = px.bar(
                x=quality_counts.index,
                y=quality_counts.values,
                title="Orders by Quality",
                labels={'x': 'Quality', 'y': 'Number of Orders'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            st.markdown("### 🏢 Top Providers")
            provider_counts = df['provider'].value_counts().head(10)
            fig_bar2 = px.bar(
                x=provider_counts.values,
                y=provider_counts.index,
                orientation='h',
                title="Top 10 Providers",
                labels={'x': 'Number of Orders', 'y': 'Provider'}
            )
            st.plotly_chart(fig_bar2, use_container_width=True)
        
        # Monthly trends
        st.markdown("### 📅 Monthly Analysis")
        df['month_year'] = df['order_date'].dt.to_period('M')
        monthly_stats = df.groupby('month_year').agg({
            'id': 'count',
            'client_name': 'nunique',
            'prize': lambda x: x.str.replace(r'[^\d.]', '', regex=True).astype(float).sum()
        }).reset_index()
        monthly_stats.columns = ['Month', 'Orders', 'Unique Clients', 'Revenue']
        monthly_stats['Month'] = monthly_stats['Month'].astype(str)
        
        fig_multi = go.Figure()
        fig_multi.add_trace(go.Scatter(
            x=monthly_stats['Month'],
            y=monthly_stats['Orders'],
            mode='lines+markers',
            name='Orders',
            yaxis='y'
        ))
        fig_multi.add_trace(go.Scatter(
            x=monthly_stats['Month'],
            y=monthly_stats['Revenue'],
            mode='lines+markers',
            name='Revenue',
            yaxis='y2'
        ))
        
        fig_multi.update_layout(
            title="Monthly Orders and Revenue Trends",
            yaxis=dict(title="Number of Orders"),
            yaxis2=dict(title="Revenue (Rs.)", overlaying='y', side='right'),
            xaxis=dict(title="Month")
        )
        st.plotly_chart(fig_multi, use_container_width=True)
        
        # Top clients
        st.markdown("### 👥 Top Clients")
        client_stats = df.groupby('client_name').agg({
            'id': 'count',
            'prize': lambda x: x.str.replace(r'[^\d.]', '', regex=True).astype(float).sum()
        }).reset_index()
        client_stats.columns = ['Client', 'Total Orders', 'Total Spent']
        client_stats = client_stats.sort_values('Total Orders', ascending=False).head(10)
        
        st.dataframe(client_stats, use_container_width=True, hide_index=True)
        
    else:
        st.info("No data available for analytics. Create some orders first!")

def edit_order_page():
    """Edit existing order"""
    st.markdown('<h1 class="main-header">✏️ Edit Order</h1>', unsafe_allow_html=True)
    
    order_id = st.session_state.get('edit_order_id')
    if not order_id:
        st.error("No order selected for editing!")
        if st.button("🔙 Back to Orders"):
            st.session_state.page = "previous_data"
            st.rerun()
        return
    
    # Get current order data
    current_order = db.get_order_by_id(order_id)
    if not current_order:
        st.error("Order not found!")
        if st.button("🔙 Back to Orders"):
            st.session_state.page = "previous_data"
            st.rerun()
        return
    
    st.info(f"Editing Order #{order_id}")
    
    with st.form("edit_order_form"):
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            client_name = st.text_input("👤 Client Name *", value=current_order[1])
            contact_no = st.text_input("📞 Contact No *", value=current_order[2])
            
            # Item type with current value
            item_type_options = ITEM_TYPES + ["Custom"]
            current_item = current_order[3]
            if current_item in ITEM_TYPES:
                item_type_idx = ITEM_TYPES.index(current_item)
            else:
                item_type_idx = len(ITEM_TYPES)  # Custom option
            
            item_type_selected = st.selectbox("📦 Item Type *", item_type_options, index=item_type_idx)
            if item_type_selected == "Custom":
                item_type = st.text_input("Enter custom item type", value=current_item if current_item not in ITEM_TYPES else "")
            else:
                item_type = item_type_selected
            
            quantity = st.text_input("📊 Quantity *", value=current_order[4])
            
            # Quality with current value
            current_quality = current_order[5]
            quality_idx = QUALITY_OPTIONS.index(current_quality) if current_quality in QUALITY_OPTIONS else 0
            quality = st.selectbox("⭐ Quality *", QUALITY_OPTIONS, index=quality_idx)
        
        with col2:
            # Color with current value
            current_color = current_order[6]
            color_options = COLOR_OPTIONS + ["Custom"]
            if current_color in COLOR_OPTIONS:
                color_idx = COLOR_OPTIONS.index(current_color)
            else:
                color_idx = len(COLOR_OPTIONS)  # Custom option
            
            color_selected = st.selectbox("🎨 Color *", color_options, index=color_idx)
            if color_selected == "Custom":
                color = st.text_input("Enter custom color", value=current_color if current_color not in COLOR_OPTIONS else "")
            else:
                color = color_selected
            
            prize = st.text_input("💰 Price *", value=current_order[7])
            provider = st.text_input("🏢 Provider *", value=current_order[8])
            
            # Parse current date and time
            try:
                current_date = datetime.strptime(current_order[9], "%Y-%m-%d").date()
            except:
                current_date = date.today()
            
            try:
                current_time = datetime.strptime(current_order[10], "%H:%M:%S").time()
            except:
                current_time = datetime.now().time()
            
            order_date = st.date_input("📅 Date *", value=current_date)
            order_time = st.time_input("🕐 Time *", value=current_time)
        
        # Notes
        current_notes = current_order[12] if len(current_order) > 12 else ""
        notes = st.text_area("📝 Notes (Optional)", value=current_notes)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_update, col_cancel = st.columns(2)
        
        with col_update:
            updated = st.form_submit_button("✅ Update Order", use_container_width=True)
        
        with col_cancel:
            if st.form_submit_button("❌ Cancel", use_container_width=True):
                st.session_state.page = "previous_data"
                st.rerun()
    
    if updated:
        # Validate required fields
        required_fields = [client_name, contact_no, item_type, quantity, quality, color, prize, provider]
        if all(field for field in required_fields):
            order_data = (
                client_name, contact_no, item_type, quantity, quality,
                color, prize, provider, str(order_date), str(order_time), notes
            )
            
            if db.update_order(order_id, order_data):
                st.success(MESSAGES['order_updated'])
                st.session_state.page = "previous_data"
                st.rerun()
            else:
                st.error("❌ Error updating order. Please try again.")
        else:
            st.error(MESSAGES['fields_required'])

# Main application logic
def main():
    """Main application controller"""
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'page' not in st.session_state:
        st.session_state.page = "login"
    if 'user_info' not in st.session_state:
        st.session_state.user_info = {}
    
    # Route to appropriate page
    if not st.session_state.logged_in:
        if st.session_state.page == "forgot_password":
            forgot_password_page()
        else:
            login_page()
    else:
        # Main application pages
        if st.session_state.page == "dashboard":
            dashboard_page()
        elif st.session_state.page == "admin_panel":
            admin_panel_page()
        elif st.session_state.page == "order_preview":
            order_preview_page()
        elif st.session_state.page == "previous_data":
            previous_data_page()
        elif st.session_state.page == "analytics":
            analytics_page()
        elif st.session_state.page == "edit_order":
            edit_order_page()
        else:
            dashboard_page()

if __name__ == "__main__":
    main()