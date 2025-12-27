"""
retrieval_engine.py - محرك البحث والفهرسة
"""

import json
import os
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from config import Config

class RetrievalEngine:
    """محرك البحث الذكي باستخدام FAISS"""
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = None
        self.metadata = []
        self.load_index()
    
    def load_index(self):
        """تحميل الفهرس إذا كان موجوداً"""
        try:
            if os.path.exists(Config.FAISS_INDEX_PATH):
                self.index = faiss.read_index(Config.FAISS_INDEX_PATH)
                
                with open(Config.FAISS_METADATA_PATH, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                    
                print(f"✅ تم تحميل الفهرس: {len(self.metadata)} مستند")
            else:
                print("⚠️ الفهرس غير موجود، سيتم إنشاء فهرس جديد عند الحاجة")
        except Exception as e:
            print(f"❌ خطأ في تحميل الفهرس: {e}")
    
    def search(self, query: str, country: str = None, top_k: int = 5) -> List[Dict]:
        """بحث عن قوانين ذات صلة"""
        
        if not self.index or len(self.metadata) == 0:
            return []
        
        # تضمين الاستعلام
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        
        # البحث في الفهرس
        distances, indices = self.index.search(query_embedding, top_k)
        
        # تجميع النتائج
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                
                # تصفية حسب الدولة إذا تم تحديدها
                if country and 'country' in meta and meta['country'] != country:
                    continue
                
                results.append({
                    'score': float(1 / (1 + dist)),  # تحويل المسافة إلى درجة تشابه
                    'source': meta.get('source', ''),
                    'chunk': meta.get('chunk', ''),
                    'title': meta.get('title', ''),
                    'preview': meta.get('preview', '')[:200]
                })
        
        # ترتيب حسب الدرجة
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results
    
    def index_documents(self, documents: List[Dict]):
        """فهرسة مستندات جديدة"""
        
        texts = []
        metas = []
        
        for doc in documents:
            # تقسيم النص إلى أجزاء
            chunks = self._chunk_text(doc['content'])
            
            for i, chunk in enumerate(chunks):
                texts.append(chunk)
                metas.append({
                    'source': doc.get('source', 'unknown'),
                    'country': doc.get('country', ''),
                    'title': doc.get('title', ''),
                    'chunk': i,
                    'preview': chunk[:100]
                })
        
        # تضمين النصوص
        embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        
        # إنشاء أو تحديث الفهرس
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        
        self.index.add(embeddings)
        self.metadata.extend(metas)
        
        # حفظ الفهرس
        self._save_index()
        
        return len(texts)
    
    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """تقسيم النص إلى أجزاء متداخلة"""
        words = text.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        
        return chunks
    
    def _save_index(self):
        """حفظ الفهرس والبيانات الوصفية"""
        try:
            # حفظ الفهرس
            faiss.write_index(self.index, Config.FAISS_INDEX_PATH)
            
            # حفظ البيانات الوصفية
            with open(Config.FAISS_METADATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ تم حفظ الفهرس: {len(self.metadata)} مستند")
        except Exception as e:
            print(f"❌ خطأ في حفظ الفهرس: {e}")
    
    def get_statistics(self) -> Dict:
        """الحصول على إحصائيات الفهرس"""
        return {
            'total_documents': len(self.metadata),
            'index_type': 'FAISS FlatL2' if self.index else 'غير محمل',
            'dimensions': self.index.d if self.index else 0,
            'size_mb': os.path.getsize(Config.FAISS_INDEX_PATH) / (1024 * 1024) 
                        if os.path.exists(Config.FAISS_INDEX_PATH) else 0
        }