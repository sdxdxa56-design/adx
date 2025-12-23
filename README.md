# adx — منصة المُحكم الرقمي

مشروع تجريبي لواجهة مساعدة قانونية ذكية (Streamlit). يوفّر اختيار الدولة، مؤسسات دولية، وتحليل مبدئي للقضايا بتوجيه نموذج لغوي.

تشغيل محلي (بيئة افتراضية موصى بها):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run main.py
```

ملاحظات مهمة:
- ضع مفتاح API الخاص بمزود النماذج في المتغير البيئي `GROQ_API_KEY` قبل التشغيل.
- الواجهة الحالية تعطي استجابات بمساعدة نموذج لغوي ولا تُعد بديلاً عن استشارة محامٍ مرخّص.

خطوات مقترحة لتدريب/تحسين المنصة على قوانين دول ومؤسسات:
1. اجمع النصوص القانونية الرسمية لكل دولة (قوانين، لوائح، أحكام محكمة) واحفظها في `data/` بصيغة نصية أو JSON.
2. أنشئ فهرس بحث (مثل FAISS أو Elasticsearch) لأجزاء النصوص (chunks) لاستخدامها مع RAG.
3. حضّر prompts وأمثلة استجابة (Q/A) لتدريب السلوك المرجو (fine-tuning أو instruction tuning) إن أمكن مع مزود يدعم ذلك.
4. اضبط نظام الاستدعاء لضم مقتطفات من القوانين ذات الصلة إلى prompt قبل طلب الإجابة من النموذج.

هل تريد أن أتابع وأضيف مجلد `data/` مع مثال مجموعات بيانات وقالب فهرسة (FAISS)؟

---

FAISS index - تعليمات سريعة (تجريبي)

1) ضع ملفات النصوص القانونية داخل مجلد `data/` بصيغة `.txt`.
2) قم بتثبيت المتطلبات: `pip install -r requirements.txt` (يشمل `sentence-transformers` و`faiss-cpu`).
3) أنشئ الفهرس عبر:

```bash
python scripts/index_faiss.py --data-dir data --index-file faiss.index --meta-file metadata.json
```

4) يمكنك اختبار الاسترجاع سريعاً عبر REPL:

```python
from retrieval import Retriever
r = Retriever('faiss.index', 'metadata.json')
print(r.query('استعلامك هنا', top_k=3))
```

5) لتضمين نتائج الاسترجاع في الـ prompt قبل استدعاء النموذج: اقرأ المصادر وأدرج مقتطفات قصيرة (chunks) أعلى الـ prompt.

# adx
adx
