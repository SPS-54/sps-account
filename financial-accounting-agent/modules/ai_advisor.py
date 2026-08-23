class AIAdvisor:
    """
    AI Accounting & Tax Knowledge Assistant for Thai SMEs and Businesses.
    Provides expert advice on VAT 7%, Withholding Tax (ภ.ง.ด.3/53), Financial Ratios, and Tax Calendar.
    """

    def ask(self, query: str, context_metrics: dict = None) -> str:
        """
        Answers user questions with Thai accounting knowledge & contextual financial data.
        """
        q = query.lower()

        if "ภ.พ.30" in query or "vat" in q or "ภาษีซื้อ" in query or "ภาษีขาย" in query:
            vat_net = context_metrics.get("vat_net", 0) if context_metrics else 0
            status_text = f"ภาษีมูลค่าเพิ่มสุทธิเดือนนี้: {abs(vat_net):,.2f} บาท ({'ต้องนำส่งกรมสรรพากร' if vat_net > 0 else 'ขอคืนภาษีหรือใช้ชำระเดือนถัดไปได้'})"
            return f"""💡 **คำแนะนำด้านภาษีมูลค่าเพิ่ม (ภ.พ. 30):**
            
- **สถานะปัจจุบัน**: {status_text}
- **กำหนดการยื่น**: ยื่นแบบ ภ.พ. 30 ภายในวันที่ 15 ของเดือนถัดไป (หรือยื่นผ่านอินเทอร์เน็ตภายในวันที่ 23)
- **ข้อควรระวัง**: 
  1. ใบกำกับภาษีซื้อต้องเป็นใบกำกับภาษีแบบเต็มรูป มีชื่อ Address และ เลขประจำตัวผู้เสียภาษีถูกต้อง
  2. ภาษีซื้อต้องห้าม (เช่น ค่าบริการรับรอง, ค่าซื้อรถยนต์นั่ง) ไม่สามารถนำมาเครดิตภาษีขายได้"""

        elif "หัก ณ ที่จ่าย" in query or "ภ.ง.ด" in query or "wht" in q:
            return """💡 **อัตราภาษีหัก ณ ที่จ่าย (Withholding Tax - WHT) ที่ใช้บ่อย:**

1. **ค่าเช่าอสังหาริมทรัพย์ / สถานที่**: หัก **5%** (ยื่น ภ.ง.ด. 53 กรณีผู้เช่าเป็นนิติบุคคล)
2. **ค่าบริการวิชาชีพ / ค่าจ้างทำของ / ค่าที่ปรึกษา**: หัก **3%** (ยื่น ภ.ง.ด. 3 กรณีผู้รับเป็นบุคคลธรรมดา / ภ.ง.ด. 53 กรณีนิติบุคคล)
3. **ค่าโฆษณา**: หัก **2%**
4. **ค่าขนส่ง (นิติบุคคล)**: หัก **1%**
5. **เงินปันผล**: หัก **10%**

📅 **กำหนดการนำส่ง**: นำส่งสรรพากรภายในวันที่ 7 ของเดือนถัดไป (ยื่นออนไลน์ภายในวันที่ 15)"""

        elif "กำไร" in query or "profit" in q or "สุขภาพการเงิน" in query:
            net_profit = context_metrics.get("net_profit", 0) if context_metrics else 0
            margin = context_metrics.get("profit_margin", 0) if context_metrics else 0
            return f"""📊 **การวิเคราะห์กำไรและสุขภาพการเงินปัจจุบัน:**

- **กำไรสุทธิ (Net Profit)**: `{net_profit:,.2f} บาท`
- **อัตรากำไรสุทธิ (Net Profit Margin)**: `{margin:.2f}%`

🎯 **ข้อแนะนำจาก AI Agent**:
1. {'อัตรากำไรสุทธิอยู่ในเกณฑ์ดีเยี่ยม (> 20%)' if margin >= 20 else 'ควรบริหารจัดการค่าใช้จ่ายดำเนินงานเพื่อเพิ่มอัตรากำไร'}
2. แนะนำให้รักษาสำรองเงินสดหมุนเวียน (Cash Runway) ไม่น้อยกว่า 3-6 เดือนของค่าใช้จ่ายประจำคงที่ (Fixed Costs)
3. ตรวจสอบลูกหนี้การค้า (AR) ที่ค้างชำระเกิน 30 วันเพื่อป้องกันปัญหาหนี้เสีย"""

        elif "กระแสเงินสด" in query or "cashflow" in q or "สภาพคล่อง" in query:
            return """📈 **กลยุทธ์การบริหารกระแสเงินสด (Cash Flow Management):**

1. **เร่งรัดการเก็บเงิน (DSO)**: เสนอส่วนลดเงินสด (Early Payment Discount) สำหรับลูกค้าที่ชำระเงินภายใน 7 วัน
2. **ขยายระยะเวลาจ่ายเจ้าหนี้ (DPO)**: เจรจาขอ Credit Term กับคู่ค้าอย่างน้อย 30-45 วัน
3. **ลดสินค้าคงคลังสำรอง (Inventory)**: ใช้หลักการ JIT (Just-In-Time) เพื่อลดเงินจมในสต็อก
4. **การตั้งสำรองภาษี**: สำรองเงินสดสำหรับจ่ายภาษี VAT และภาษีเงินได้นิติบุคคลครึ่งปี (ภ.ง.ด. 51) ไว้แยกต่างหาก"""

        else:
            return f"""🤖 **AI Financial Agent Assistant:**
            
คำถามของคุณคือ: "{query}"

📌 **สรุปสถานะการเงินย่อ**:
- รายได้รวม: `{context_metrics.get('total_income', 0):,.2f} บาท`
- รายจ่ายรวม: `{context_metrics.get('total_expense', 0):,.2f} บาท`
- กำไรสุทธิ: `{context_metrics.get('net_profit', 0):,.2f} บาท`

คุณสามารถสอบถามเพิ่มเติมเกี่ยวกับ:
1. "ยื่น ภ.พ. 30 เมื่อไหร่ และต้องจ่าย VAT เท่าไหร่?"
2. "หัก ณ ที่จ่าย ค่าเช่า หรือ ค่าบริการ คิดกี่ %?"
3. "วิเคราะห์อัตรากำไรและสุขภาพการเงินบริษัท"
4. "คำแนะนำการบริหารกระแสเงินสด" """
