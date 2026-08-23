import os
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.accounting_engine import AccountingEngine
from modules.document_parser import DocumentParser
from modules.reconciliation import BankReconcilationEngine
from modules.forecasting import CashFlowForecaster
from modules.ai_advisor import AIAdvisor
from utils.helper import format_thb, format_thai_date

# Page Config
st.set_page_config(
    page_title="AI Agent สำหรับงานบัญชี-การเงิน",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSACTIONS_PATH = os.path.join(BASE_DIR, "data", "sample_transactions.json")
COA_PATH = os.path.join(BASE_DIR, "data", "chart_of_accounts.json")
BANK_CSV_PATH = os.path.join(BASE_DIR, "data", "sample_bank_statement.csv")

# Initialize Engine
@st.cache_resource
def load_accounting_engine():
    return AccountingEngine(COA_PATH, TRANSACTIONS_PATH)

engine = load_accounting_engine()
doc_parser = DocumentParser()
reconciler = BankReconcilationEngine()
forecaster = CashFlowForecaster()
advisor = AIAdvisor()

# Header Section
st.title("💼 AI Agent สำหรับงานบัญชี-การเงิน (Financial & Accounting Agent)")
st.caption("ระบบผู้ช่วยปัญญาประดิษฐ์สำหรับงานบัญชี การจัดทำเอกสาร สรุปรายซัพพลายเออร์ การวิเคราะห์งบ และพยากรณ์กระแสเงินสด")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/bot.png", width=70)
    st.header("⚙️ เมนูผู้ช่วย AI บัญชี")
    st.info("🟢 ระบบ AI พร้อมทำงาน\n📅 วันที่ปัจจุบัน: 22 สิงหาคม 2569")
    
    st.markdown("---")
    st.subheader("📌 สรุปด่วนทางการเงิน")
    pnl = engine.calculate_profit_loss()
    st.metric("รายได้รวม", format_thb(pnl["total_income"]))
    st.metric("รายจ่ายรวม", format_thb(pnl["total_expense"]))
    st.metric("กำไรสุทธิ", format_thb(pnl["net_profit"]), delta=f"{pnl['profit_margin']}% Margin")

    st.markdown("---")
    st.caption("พัฒนาด้วย Python, Streamlit & Gemini AI Architecture")

# Tabs Navigation
tab1, tab_supp, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 ภาพรวมการเงิน (Dashboard)",
    "🚚 แยกตามซัพพลายเออร์ (Supplier Ledger)",
    "📄 สแกนเอกสาร (Smart OCR)",
    "🏦 กระทบยอดธนาคาร (Bank Reconcile)",
    "📈 พยากรณ์กระแสเงินสด (Cash Flow)",
    "💬 ผู้ช่วย AI บัญชี & ภาษี (Tax Advisor)"
])

# ---------------------------------------------------------
# TAB 1: FINANCIAL DASHBOARD & KPIS
# ---------------------------------------------------------
with tab1:
    st.subheader("📊 สรุปภาพรวมผลการดำเนินงานทางการเงิน")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 รายได้รวม (Total Revenue)", format_thb(pnl["total_income"]))
    with col2:
        st.metric("💸 รายจ่ายรวม (Total Expenses)", format_thb(pnl["total_expense"]))
    with col3:
        st.metric("📈 กำไรสุทธิ (Net Profit)", format_thb(pnl["net_profit"]), f"{pnl['profit_margin']}%")
    with col4:
        vat_status = f"ต้องจ่าย {format_thb(pnl['vat_net'])}" if pnl['vat_net'] > 0 else f"ขอคืน {format_thb(abs(pnl['vat_net']))}"
        st.metric("🧾 ภาษีมูลค่าเพิ่มสุทธิ (VAT 7%)", vat_status)

    st.markdown("###")

    txs = engine.get_all_transactions()
    df_tx = pd.DataFrame(txs)

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("#### 📉 สัดส่วนค่าใช้จ่ายตามหมวดหมู่ (Expense Breakdown)")
        if not df_tx.empty:
            df_exp = df_tx[df_tx["type"] == "Expense"]
            fig_pie = px.pie(
                df_exp, 
                names="account_name", 
                values="amount_before_vat",
                color_discrete_sequence=px.colors.qualitative.Set3,
                hole=0.4
            )
            fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        st.markdown("#### 📅 รายรับ vs รายจ่าย รายธุรกรรม")
        if not df_tx.empty:
            fig_bar = px.bar(
                df_tx,
                x="date",
                y="amount_before_vat",
                color="type",
                barmode="group",
                labels={"amount_before_vat": "จำนวนเงิน (บาท)", "date": "วันที่"},
                color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"}
            )
            fig_bar.update_layout(margin=dict(t=20, b=20, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📋 รายการธุรกรรมทั้งหมด (Transaction Ledger)")
    if not df_tx.empty:
        st.dataframe(
            df_tx[["id", "date", "type", "description", "vendor_customer", "amount_before_vat", "vat_amount", "wht_amount", "total_amount", "status"]],
            use_container_width=True
        )

# ---------------------------------------------------------
# TAB SUPPLIER: SUPPLIER LEDGER (NEW FEATURE)
# ---------------------------------------------------------
with tab_supp:
    st.subheader("🚚 สมุดบัญชีแยกประเภทคู่ค้า & ซัพพลายเออร์ (Supplier & Vendor Ledger)")
    st.markdown("วิเคราะห์และสรุปยอดรายจ่าย ยอดภาษี VAT และภาษีหัก ณ ที่จ่าย แยกตามรายซัพพลายเออร์")

    if not df_tx.empty:
        df_exp = df_tx[df_tx["type"] == "Expense"].copy()
        
        if not df_exp.empty:
            # Group by Supplier/Vendor
            supp_summary = df_exp.groupby("vendor_customer").agg(
                จำนวนรายการ=("id", "count"),
                ยอดซื้อก่อนVAT=("amount_before_vat", "sum"),
                VAT7เปอร์เซ็นต์=("vat_amount", "sum"),
                ภาษีหักณที่จ่าย=("wht_amount", "sum"),
                ยอดจ่ายสุทธิ=("net_cash_paid", "sum")
            ).reset_index()

            supp_summary.rename(columns={"vendor_customer": "ชื่อซัพพลายเออร์/คู่ค้า"}, inplace=True)

            col_s1, col_s2 = st.columns([1, 2])
            
            with col_s1:
                st.markdown("#### 📊 กราฟสรุปยอดซื้อแยกตามซัพพลายเออร์")
                fig_supp = px.bar(
                    supp_summary,
                    x="ยอดซื้อก่อนVAT",
                    y="ชื่อซัพพลายเออร์/คู่ค้า",
                    orientation="h",
                    color="ยอดซื้อก่อนVAT",
                    color_continuous_scale="Viridis",
                    labels={"ยอดซื้อก่อนVAT": "ยอดซื้อรวม (บาท)"}
                )
                fig_supp.update_layout(margin=dict(t=10, b=10, l=10, r=10))
                st.plotly_chart(fig_supp, use_container_width=True)

            with col_s2:
                st.markdown("#### 📋 ตารางสรุปยอดรวมแยกรายซัพพลายเออร์")
                st.dataframe(
                    supp_summary.style.format({
                        "ยอดซื้อก่อนVAT": "฿{:,.2f}",
                        "VAT7เปอร์เซ็นต์": "฿{:,.2f}",
                        "ภาษีหักณที่จ่าย": "฿{:,.2f}",
                        "ยอดจ่ายสุทธิ": "฿{:,.2f}"
                    }),
                    use_container_width=True
                )

            st.markdown("---")
            selected_supplier = st.selectbox("🔍 เลือกซัพพลายเออร์เพื่อดูรายการใบเสร็จอย่างละเอียด:", ["-- แสดงทั้งหมด --"] + list(supp_summary["ชื่อซัพพลายเออร์/คู่ค้า"].unique()))

            if selected_supplier != "-- แสดงทั้งหมด --":
                df_filtered = df_exp[df_exp["vendor_customer"] == selected_supplier]
            else:
                df_filtered = df_exp

            st.markdown(f"#### 📄 รายการใบเสร็จของซัพพลายเออร์ ({len(df_filtered)} รายการ)")
            st.dataframe(
                df_filtered[["id", "date", "description", "vendor_customer", "amount_before_vat", "vat_amount", "wht_amount", "net_cash_paid", "doc_ref"]],
                use_container_width=True
            )

# ---------------------------------------------------------
# TAB 2: SMART OCR & DOCUMENT PROCESSOR
# ---------------------------------------------------------
with tab2:
    st.subheader("📄 ระบบอ่านและบันทึกเอกสารอัตโนมัติด้วย AI (Smart OCR Parser)")
    st.markdown("อัปโหลดใบเสร็จรับเงิน ใบแจ้งหนี้ หรือใบกำกับภาษี เพื่อให้ AI สกัดข้อมูลและสร้างรายการบันทึกบัญชีอัตโนมัติ")

    col_up, col_res = st.columns([1, 1])

    with col_up:
        uploaded_file = st.file_uploader("เลือกไฟล์รูปภาพใบเสร็จหรือ PDF (PNG, JPG, PDF)", type=["png", "jpg", "jpeg", "pdf"])
        sample_choice = st.selectbox(
            "หรือ เลือกเอกสารตัวอย่างสำหรับทดสอบ:",
            ["- เลือกตัวอย่างเอกสาร -", "ใบเสร็จค่าเช่าสำนักงาน (Rent Expense)", "ใบแจ้งหนี้ค่าบริการซอฟต์แวร์ (Software Income)", "ใบเสร็จค่าโฆษณา Facebook/Google (Ads Expense)"]
        )

        file_to_parse = None
        file_name = ""

        if uploaded_file:
            file_name = uploaded_file.name
            file_to_parse = uploaded_file.read()
        elif sample_choice != "- เลือกตัวอย่างเอกสาร -":
            file_name = sample_choice

        if st.button("🚀 ให้ AI สกัดข้อมูลและประมวลผล", type="primary", use_container_width=True):
            if file_name:
                with st.spinner("AI Agent กำลังอ่านโครงสร้างเอกสาร คำนวณ VAT 7% และภาษีหัก ณ ที่จ่าย..."):
                    parsed_result = doc_parser.parse_document(file_name, file_to_parse)
                    st.session_state["last_parsed"] = parsed_result
                    st.success("✅ AI สกัดข้อมูลเอกสารสำเร็จเรียบร้อย!")
            else:
                st.warning("กรุณาอัปโหลดไฟล์หรือเลือกเอกสารตัวอย่าง")

    with col_res:
        st.markdown("#### 🔍 ผลการสกัดข้อมูลและลงบัญชีโดย AI")
        if "last_parsed" in st.session_state:
            res = st.session_state["last_parsed"]
            st.json(res)

            st.markdown("#### 📖 รายการลงบัญชีเดบิต-เครดิต (Double-Entry Journal Entry)")
            journal_entries = engine.generate_journal_entry(res)
            st.table(pd.DataFrame(journal_entries))

            if st.button("💾 ยืนยันการบันทึกลงสมุดบัญชีทั่วไป (Save to Ledger)"):
                res["id"] = f"TX-2026-00{len(engine.get_all_transactions()) + 1}"
                engine.add_transaction(res)
                st.success(f"บันทึกรายการ {res['id']} ลงระบบเรียบร้อยแล้ว!")
                st.rerun()
        else:
            st.info("รอการอัปโหลดหรือประมวลผลเอกสาร...")

# ---------------------------------------------------------
# TAB 3: BANK RECONCILIATION
# ---------------------------------------------------------
with tab3:
    st.subheader("🏦 ระบบกระทบยอดธนาคารอัตโนมัติ (Automated Bank Reconciliation)")
    st.markdown("เปรียบเทียบรายการเดินบัญชีธนาคาร (Bank Statement) กับสมุดบัญชีรายวัน (General Ledger) เพื่อหาจุดคลาดเคลื่อน")

    col_b1, col_b2 = st.columns([1, 2])

    with col_b1:
        st.markdown("#### 📄 ข้อมูล Bank Statement")
        if os.path.exists(BANK_CSV_PATH):
            bank_df = pd.read_csv(BANK_CSV_PATH)
            st.dataframe(bank_df, use_container_width=True)

    with col_b2:
        st.markdown("#### 🎯 ผลการจับคู่และกระทบยอดโดย AI Agent")
        if st.button("⚡ เริ่มประมวลผลกระทบยอด (Run Bank Matching)", type="primary"):
            with st.spinner("กำลังเปรียบเทียบ ยอดเงิน วันที่ และเลขที่อ้างอิง..."):
                reconciled_df = reconciler.reconcile(bank_df, engine.get_all_transactions())
                st.dataframe(reconciled_df, use_container_width=True)
                
                exact_count = len(reconciled_df[reconciled_df["Confidence"] == 100.0])
                st.success(f"🎉 กระทบยอดสำเร็จ! จับคู่รายการตรงกันสมบูรณ์ 100%: {exact_count} รายการ")

# ---------------------------------------------------------
# TAB 4: CASH FLOW FORECASTING
# ---------------------------------------------------------
with tab4:
    st.subheader("📈 การพยากรณ์กระแสเงินสดและวิเคราะห์สภาพคล่อง (Cash Flow Forecasting)")
    st.markdown("ใช้โมเดล AI พยากรณ์กระแสเงินสดล่วงหน้า 90 วัน เพื่อวางแผนสภาพคล่องและป้องกันเงินสดขาดมือ")

    days_to_forecast = st.slider("เลือกจำนวนวันที่ต้องการพยากรณ์ (วัน):", min_value=30, max_value=180, value=90, step=30)
    
    df_forecast = forecaster.forecast_cash_flow(engine.get_all_transactions(), days=days_to_forecast)

    fig_fc = px.line(
        df_forecast,
        x="Date",
        y="Projected_Cash_Balance",
        title="📊 แนวโน้มประมาณการยอดเงินสดคงเหลือคงเหลือ (Projected Cash Balance)",
        labels={"Projected_Cash_Balance": "เงินสดคงเหลือ (บาท)", "Date": "วันที่"},
        line_shape="spline"
    )
    fig_fc.add_hline(y=100000, line_dash="dash", line_color="red", annotation_text="เกณฑ์เงินสดสำรองขั้นต่ำ (100,000 บาท)")
    st.plotly_chart(fig_fc, use_container_width=True)

    col_fc1, col_fc2 = st.columns(2)
    with col_fc1:
        st.markdown("#### 💡 การวิเคราะห์และข้อแนะนำสภาพคล่องจาก AI")
        min_balance = df_forecast["Projected_Cash_Balance"].min()
        if min_balance < 100000:
            st.error(f"⚠️ เตือนความเสี่ยง: เงินสดคงเหลือต่ำสุดอยู่ที่ {format_thb(min_balance)} ซึ่งต่ำกว่าเกณฑ์สำรอง")
        else:
            st.success(f"✅ สภาพคล่องอยู่ในเกณฑ์ดีเยี่ยม ยอดเงินสดคงเหลือต่ำสุดอยู่ที่ {format_thb(min_balance)}")
        st.info("📌 ในช่วงวันที่ 10 มีประมาณการเงินสดรับจากลูกหนี้การค้า 52,000 บาท ช่วยเพิ่มสภาพคล่องหมุนเวียน")

    with col_fc2:
        st.markdown("#### 📋 ตารางพยากรณ์รายวัน (Forecast Data Table)")
        st.dataframe(df_forecast.head(15), use_container_width=True)

# ---------------------------------------------------------
# TAB 5: AI FINANCIAL & TAX ADVISOR
# ---------------------------------------------------------
with tab5:
    st.subheader("💬 ผู้ช่วย AI ปรึกษาด้านบัญชี งบการเงิน และภาษีไทย (AI Advisor)")
    st.markdown("พิมพ์สอบถามข้อสงสัยเกี่ยวกับงบการเงิน อัตราส่วนทางการเงิน กฎหมายภาษีไทย (ภ.พ.30, ภ.ง.ด.3/53) ได้ตลอด 24 ชั่วโมง")

    sample_questions = [
        "ยื่น ภ.พ. 30 เมื่อไหร่ และต้องจ่าย VAT เดือนนี้เท่าไหร่?",
        "หัก ณ ที่จ่าย ค่าเช่า หรือ ค่าบริการ คิดกี่ %?",
        "วิเคราะห์อัตรากำไรและสุขภาพการเงินปัจจุบันของบริษัท",
        "ข้อแนะนำในการบริหารกระแสเงินสด"
    ]

    selected_q = st.selectbox("💡 เลือกคำถามยอดฮิต หรือ พิมพ์คำถามใหม่ด้านล่าง:", ["- เลือกคำถามแนะนำ -"] + sample_questions)
    
    user_query = st.text_input("💬 พิมพ์คำถามของคุณเกี่ยวกับบัญชีและการเงิน:", value="" if selected_q == "- เลือกคำถามแนะนำ -" else selected_q)

    if st.button("🤖 สอบถาม AI Agent", type="primary"):
        if user_query:
            with st.spinner("AI Agent กำลังวิเคราะห์ข้อมูลการเงินและข้อกฎหมายภาษี..."):
                answer = advisor.ask(user_query, context_metrics=pnl)
                st.markdown(answer)
        else:
            st.warning("กรุณากรอกคำถามที่ต้องการสอบถาม")
