"""
scripts/index_faiss.py - فهرسة القوانين في FAISS
"""

import os
import sys
import json
import argparse
from pathlib import Path

# إضافة المسار للأدوات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentence_transformers import SentenceTransformer
import faiss
from config import Config

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    """تقسيم النص إلى أجزاء متداخلة"""
    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    
    return chunks

def index_documents(data_dir: str = "data", 
                   index_file: str = "faiss.index",
                   meta_file: str = "metadata.json",
                   model_name: str = "all-MiniLM-L6-v2"):
    """فهرسة جميع المستندات النصية"""
    
    print("🚀 بدء عملية الفهرسة...")
    
    # تحميل النموذج
    model = SentenceTransformer(model_name)
    print(f"✅ تم تحميل النموذج: {model_name}")
    
    texts = []
    metadata = []
    
    # البحث عن ملفات نصية
    data_path = Path(data_dir)
    txt_files = list(data_path.glob("**/*.txt")) + list(data_path.glob("**/*.json"))
    
    print(f"🔍 وجدت {len(txt_files)} ملف للفهرسة")
    
    for file_path in txt_files:
        try:
            print(f"📖 معالجة: {file_path.name}")
            
            # قراءة الملف
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # استخراج المعلومات من اسم الملف
            country = "unknown"
            doc_type = "unknown"
            
            if "yemen" in file_path.name.lower():
                country = "Yemen"
            elif "egypt" in file_path.name.lower():
                country = "Egypt"
            elif "saudi" in file_path.name.lower():
                country = "Saudi Arabia"
            
            if "civil" in file_path.name.lower():
                doc_type = "قانون مدني"
            elif "criminal" in file_path.name.lower():
                doc_type = "قانون جنائي"
            elif "labor" in file_path.name.lower():
                doc_type = "قانون عمل"
            elif "commercial" in file_path.name.lower():
                doc_type = "قانون تجاري"
            
            # تقسيم النص
            chunks = chunk_text(content)
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metadata.append({
                    "source": str(file_path),
                    "country": country,
                    "type": doc_type,
                    "chunk": i,
                    "preview": chunk[:100],
                    "title": f"{doc_type} - {country}"
                })
                
            print(f"  ✓ تمت معالجة {len(chunks)} جزء")
            
        except Exception as e:
            print(f"  ✗ خطأ في معالجة {file_path.name}: {e}")
    
    if not texts:
        print("⚠️ لا توجد نصوص للفهرسة!")
        return False
    
    print(f"🔢 جاري تضمين {len(texts)} جزء نصي...")
    
    # تضمين النصوص
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # إنشاء الفهرس
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    
    # حفظ الفهرس
    faiss.write_index(index, index_file)
    
    # حفظ البيانات الوصفية
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"✅ تم إنشاء الفهرس بنجاح!")
    print(f"📊 إحصائيات:")
    print(f"   - عدد الأجزاء: {len(texts)}")
    print(f"   - أبعاد التضمين: {dim}")
    print(f"   - حجم الفهرس: {os.path.getsize(index_file) / (1024*1024):.2f} MB")
    print(f"   - ملف الفهرس: {index_file}")
    print(f"   - ملف البيانات: {meta_file}")
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="فهرسة القوانين في FAISS")
    parser.add_argument("--data-dir", default="data", help="مجلد البيانات")
    parser.add_argument("--index-file", default=Config.FAISS_INDEX_PATH, help="مسار الفهرس")
    parser.add_argument("--meta-file", default=Config.FAISS_METADATA_PATH, help="مسار البيانات الوصفية")
    parser.add_argument("--model", default="all-MiniLM-L6-v2", help="نموذج التضمين")
    
    args = parser.parse_args()
    
    success = index_documents(
        data_dir=args.data_dir,
        index_file=args.index_file,
        meta_file=args.meta_file,
        model_name=args.model
    )
    
    if success:
        print("🎉 تمت الفهرسة بنجاح!")
        sys.exit(0)
    else:
        print("❌ فشلت الفهرسة!")
        sys.exit(1)