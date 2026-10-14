"""شاشة المساعدة ودليل الاستخدام."""

from __future__ import annotations

from PySide6.QtCore import Qt

from ..widgets import Card, body_label
from .base import BaseScreen


class HelpScreen(BaseScreen):
    def __init__(self, context, window) -> None:
        super().__init__(context, window, title="المساعدة ودليل الاستخدام")
        self.setLayoutDirection(Qt.RightToLeft)

        card = Card("كيف تبدأ")
        card.add(body_label(
            "1. ابدأ من الدروس: انتقل إلى الدروس والمستويات ثم اختر أول درس.\n"
            "2. اقرأ التعريف، ثم أجِب على التدريبات باستخدام خلية برايل التفاعلية.\n"
            "3. يمكنك الضغط على الأرقام 1-6 أو الفأرة لتحديد النقاط، ثم تأكيد الإجابة.\n"
            "4. بعد الانتهاء، احفظ الجلسة ليرتفع التقدّم ويُفتح المستوى التالي عند تحقيق 85%."
        ))
        self.layout.addWidget(card)

        card2 = Card("إمكانية الوصول وقارئات الشاشة")
        card2.add(body_label(
            "يدعم التطبيق NVDA وWindows Narrator قدر الإمكان. جميع الأزرار لها أسماء واضحة، "
            "وعند تغيير حالة خلية برايل يُعلن وصف النص تلقائيًا. إذا لم يتوفّر صوت عربي، "
            "يبقى التطبيق قابلاً للاستخدام بالكامل."
        ))
        self.layout.addWidget(card2)

        card3 = Card("الصوت والإعدادات")
        card3.add(body_label(
            "في الإعدادات يمكنك تغيير حجم الخط، حجم خلايا برايل، الوضع الفاتح/الداكن، "
            "التباين المرتفع، ألوان النقاط، وتشغيل/إيقاف النطق ومستوى الصوت وسرعته. "
            "كل الإعدادات تُحفظ محليًا ولا تؤثّر على إعدادات النظام."
        ))
        self.layout.addWidget(card3)

        self.layout.addStretch(1)
