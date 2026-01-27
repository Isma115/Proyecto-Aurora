# -*- coding: utf-8 -*-
"""
Motor RAG (Retrieval-Augmented Generation)
Búsqueda de contexto relevante en archivos de texto
"""

import os
import re
from difflib import SequenceMatcher
from collections import Counter
import math
from config import KNOWLEDGE_DIR, MEMORY_DIR, SIMILARITY_THRESHOLD, CHUNK_SIZE, MAX_RAG_RESULTS, MIN_RAG_QUERY_LENGTH


class RAGEngine:
    """Motor de búsqueda RAG para recuperar contexto relevante"""
    
    def __init__(self, knowledge_dir=KNOWLEDGE_DIR, memory_dir=MEMORY_DIR):
        self.knowledge_dir = knowledge_dir
        self.memory_dir = memory_dir
        self.documents = []
        self.chunks = []
        self.load_documents()
    
    def load_documents(self):
        """Carga documentos de texto de los directorios configurados (conocimiento Y memoria)"""
        self.documents = []
        self.chunks = []
        
        # Cargar AMBOS: conocimiento y memoria (misma lógica de filtrado por similitud)
        directories = [
            (self.knowledge_dir, 'conocimiento'),
            (self.memory_dir, 'memoria')
        ]
        
        for directory, doc_type in directories:
            if not os.path.exists(directory):
                continue
            
            for filename in os.listdir(directory):
                if filename.endswith('.txt'):
                    filepath = os.path.join(directory, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if not content.strip(): continue
                            
                            self.documents.append({
                                'filename': filename,
                                'filepath': filepath,
                                'content': content,
                                'type': doc_type
                            })
                            # Dividir en chunks
                            doc_chunks = self.chunk_text(content, filename, doc_type=doc_type)
                            self.chunks.extend(doc_chunks)
                    except Exception as e:
                        print(f"Error cargando {filename}: {e}")
    
    def chunk_text(self, text, source_filename, doc_type='general', chunk_size=CHUNK_SIZE, overlap=100):
        """Divide el texto en fragmentos con solapamiento"""
        chunks = []
        text = text.strip()
        
        if len(text) <= chunk_size:
            chunks.append({
                'text': text,
                'source': source_filename,
                'type': doc_type,
                'start': 0,
                'end': len(text)
            })
            return chunks
        
        # Dividir por párrafos primero
        paragraphs = text.split('\n\n')
        current_chunk = ""
        current_start = 0
        position = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                position += 2
                continue
            
            if len(current_chunk) + len(para) + 2 <= chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
                    current_start = position
            else:
                if current_chunk:
                    chunks.append({
                        'text': current_chunk,
                        'source': source_filename,
                        'type': doc_type,
                        'start': current_start,
                        'end': position
                    })
                current_chunk = para
                current_start = position
            
            position += len(para) + 2
        
        # Añadir el último chunk
        if current_chunk:
            chunks.append({
                'text': current_chunk,
                'source': source_filename,
                'type': doc_type,
                'start': current_start,
                'end': position
            })
        
        return chunks
    
    def preprocess_text(self, text):
        """Preprocesa el texto para comparación"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def tokenize(self, text):
        """Tokeniza el texto en palabras"""
        return self.preprocess_text(text).split()
    
    def calculate_tf(self, tokens):
        """Calcula la frecuencia de términos (TF)"""
        tf = Counter(tokens)
        total = len(tokens)
        return {word: count / total for word, count in tf.items()}
    
    def calculate_idf(self, token, all_documents):
        """Calcula la frecuencia inversa de documento (IDF)"""
        doc_count = sum(1 for doc in all_documents if token in doc)
        if doc_count == 0:
            return 0
        return math.log(len(all_documents) / doc_count)
    
    def calculate_tfidf(self, tokens, all_documents):
        """Calcula TF-IDF para un conjunto de tokens"""
        tf = self.calculate_tf(tokens)
        tfidf = {}
        for token in tf:
            idf = self.calculate_idf(token, all_documents)
            tfidf[token] = tf[token] * idf
        return tfidf
    
    def cosine_similarity(self, vec1, vec2):
        """Calcula la similitud del coseno entre dos vectores"""
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    def sequence_similarity(self, text1, text2):
        """Calcula similitud usando SequenceMatcher de difflib"""
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)
        return SequenceMatcher(None, text1, text2).ratio()
    
    def calculate_similarity(self, query, chunk_text):
        """
        Calcula la similitud combinando múltiples métodos:
        - Similitud de secuencia (para coincidencias exactas)
        - TF-IDF con similitud del coseno (para similitud semántica)
        - Coincidencia de palabras clave
        - Búsqueda de subcadenas
        """
        query_lower = query.lower()
        chunk_lower = chunk_text.lower()
        
        # Método 1: Búsqueda directa de palabras clave importantes
        query_tokens = set(self.tokenize(query))
        chunk_tokens = set(self.tokenize(chunk_text))
        
        if not query_tokens:
            return 0
        
        # Filtrar palabras comunes (stopwords extendido español)
        stopwords = {
            'de', 'la', 'que', 'el', 'en', 'y', 'a', 'los', 'del', 'se', 'las', 'por', 'un', 'para', 
            'con', 'no', 'una', 'su', 'al', 'lo', 'como', 'más', 'pero', 'sus', 'le', 'ya', 'o', 
            'este', 'sí', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 'también', 
            'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 'todos', 
            'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 'esto', 
            'mí', 'antes', 'algunos', 'qué', 'unos', 'yo', 'otro', 'otras', 'otra', 'él', 'tanto', 
            'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 
            'estas', 'algunas', 'algo', 'nosotros', 'mi', 'mis', 'tú', 'te', 'ti', 'tu', 'tus', 
            'ellas', 'nosotras', 'vosotros', 'vosotras', 'os', 'mío', 'mía', 'míos', 'mías', 
            'tuyo', 'tuya', 'tuyos', 'tuyas', 'suyo', 'suya', 'suyos', 'suyas', 'nuestro', 
            'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 
            'es', 'está', 'son', 'sea', 'sean', 'ser', 'era', 'eras', 'eramos', 'eran',
            'estoy', 'estás', 'estamos', 'están', 'estar', 'ha', 'han', 'he', 'has', 'hacer',
            'tener', 'tengo', 'tienes', 'tiene', 'tenemos', 'tienen', 'hacer', 'hago', 'hace',
            'decir', 'dice', 'dijo', 'ir', 'voy', 'va', 'vamos', 'van', 'ver', 'veo', 'ves', 've',
            'cómo', 'cuál', 'cuáles', 'quién', 'quiénes', 'dónde', 'cuándo', 'cuánto', 'cuánta', 
            'cuántos', 'cuántas', 'por qué', 'para qué',
            'hola', 'buenos', 'días', 'tardes', 'noches', 'qué', 'tal', 'estás'
        }
        
        query_keywords = query_tokens - stopwords
        chunk_keywords = chunk_tokens - stopwords
        
        # Si la query se queda vacía tras filtrar (ej: "qué es"), usar tokens originales
        if not query_keywords:
            query_keywords = query_tokens
            
        # 1. Coincidencia de palabras clave (Jaccard Index sobre keywords)
        # Importante: Penalizar si el chunk no tiene las palabras clave
        intersection = query_keywords & chunk_keywords
        keyword_match = len(intersection) / len(query_keywords) if query_keywords else 0
        
        # 2. Densidad de coincidencia (cuántas veces aparecen las palabras clave en el texto)
        # Esto ayuda a priorizar textos que hablan MUCHO del tema
        match_count = sum(chunk_lower.count(word) for word in query_keywords)
        # Normalizar por logitud (logarítmico para no penalizar exceso textos largos)
        density_score = min(1.0, match_count / (math.log(len(chunk_lower) + 1) * 2))
        
        # 3. Substring score (para palabras compuestas o variaciones)
        substring_score = 0
        for word in query_keywords:
            if len(word) >= 4 and word in chunk_lower:
                substring_score += 1
        substring_score = substring_score / len(query_keywords) if query_keywords else 0
        
        # 4. TF-IDF y Coseno (Semántico estadístico)
        # Nota: Recalcular esto por chunk es costoso, en prod se cachearía.
        all_chunk_tokens = [self.tokenize(c['text']) for c in self.chunks]
        query_tokens_list = self.tokenize(query)
        chunk_tokens_list = self.tokenize(chunk_text)
        
        tfidf_sim = 0
        if all_chunk_tokens and query_tokens_list and chunk_tokens_list:
            query_tfidf = self.calculate_tfidf(query_tokens_list, all_chunk_tokens)
            chunk_tfidf = self.calculate_tfidf(chunk_tokens_list, all_chunk_tokens)
            tfidf_sim = self.cosine_similarity(query_tfidf, chunk_tfidf)

        # 5. Penalización por longitud excesiva si hay pocos matches
        length_penalty = 1.0
        if len(chunk_text) > 1000 and match_count < 2:
            length_penalty = 0.5  # Penalizar chunks gigantes con solo 1 coincidencia casual

        # Combinación Ponderada
        # Ajustamos pesos para favorecer la "Densidad" y "Coincidencia Exacta"
        combined = (
            keyword_match * 0.40 +    # ¿Están las palabras que busco?
            density_score * 0.25 +    # ¿Aparecen frecuentemente?
            tfidf_sim * 0.25 +        # ¿Son relevantes estadísticamente?
            substring_score * 0.10    # ¿Hay coincidencias parciales?
        )
        
        # Aplicar penalización
        combined *= length_penalty
        
        # Bonus fuerte si TODAS las keywords están presentes
        if keyword_match >= 0.9:
            combined *= 1.3
        
        # Limitar a 0-1
        return min(1.0, combined)
    
    def search(self, query, threshold=SIMILARITY_THRESHOLD, max_results=MAX_RAG_RESULTS):
        """
        Busca fragmentos relevantes basándose en la query.
        Devuelve fragmentos con similitud mayor al umbral.
        """
        if not self.chunks:
            self.load_documents()
        
        if not self.chunks:
            return []
        
        results = []
        
        for chunk in self.chunks:
            similarity = self.calculate_similarity(query, chunk['text'])
            
            if similarity >= threshold:
                results.append({
                    'text': chunk['text'],
                    'source': chunk['source'],
                    'type': chunk.get('type', 'conocimiento'),
                    'similarity': similarity,
                    'start': chunk.get('start', 0),
                    'end': chunk.get('end', len(chunk['text']))
                })
        
        # Ordenar por similitud descendente
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:max_results]

    def expand_context(self, chunk_data, min_words=150):
        """
        Expande el contexto del chunk si es muy corto (< min_words).
        Utiliza el documento original para ampliar la ventana de texto.
        """
        text = chunk_data['text']
        word_count = len(text.split())
        
        if word_count >= min_words:
            return text
            
        # Buscar documento original
        source_doc = next((d for d in self.documents if d['filename'] == chunk_data['source']), None)
        if not source_doc:
            return text
            
        full_content = source_doc['content']
        start = chunk_data.get('start', 0)
        end = chunk_data.get('end', len(full_content))
        
        print(f"[RAG] Expandiendo contexto de {word_count} palabras a objetivo {min_words}...")
        
        # Expandir hacia ambos lados
        # Paso de expansión (caracteres)
        step = 200
        
        while len(full_content[start:end].split()) < min_words:
            changed = False
            
            # Expandir hacia atrás
            if start > 0:
                old_start = start
                start = max(0, start - step)
                # Intentar ajustar a inicio de párrafo o frase si es posible (simple heurística)
                # Si caemos en medio de linea, retrocedemos hasta \n si está cerca
                if start > 0:
                    prev_newline = full_content.rfind('\n', max(0, start-100), start)
                    if prev_newline != -1:
                        start = prev_newline + 1
                        
                if start != old_start:
                    changed = True
            
            # Expandir hacia adelante
            if end < len(full_content):
                old_end = end
                end = min(len(full_content), end + step)
                # Ajustar a fin de párrafo
                next_newline = full_content.find('\n', end, end+100)
                if next_newline != -1:
                    end = next_newline
                    
                if end != old_end:
                    changed = True
                
            if not changed: # Ya no se puede expandir más (límites alcanzados)
                break
                
        expanded_text = full_content[start:end].strip()
        final_count = len(expanded_text.split())
        print(f"[RAG] Contexto expandido a {final_count} palabras.")
        
        return expanded_text

    
    def get_context(self, query, threshold=SIMILARITY_THRESHOLD):
        """
        Obtiene el contexto relevante para una query.
        Devuelve un string formateado con los fragmentos relevantes.
        """
        # Verificar longitud mínima
        if not query or len(query.strip()) < MIN_RAG_QUERY_LENGTH:
            return None, 0.0

        results = self.search(query, threshold=0.1, max_results=5)
        
        if not results:
            return None, 0.0
            
        # Tomar el mejor resultado
        best_result = results[0]
        similarity_score = best_result['similarity']
        
        # Solo usar contexto si supera o iguala el umbral configurado
        if similarity_score >= threshold:
            context_parts = []
            
            print(f"\n🔍 Búsqueda RAG para: '{query}'")
            print(f"   Mejor resultado: {similarity_score:.1%} (Umbral: {threshold:.0%})")
            
            result = best_result
            
            # Determinar tipo
            doc_type = result.get('type')
            if not doc_type:
                if 'memoria' in result.get('filepath', '').lower():
                    doc_type = 'memoria'
                else:
                    doc_type = 'conocimiento'
            
            if doc_type == 'memoria':
                is_vivid = "RECUERDO VIVIDO" in result['text'] or (len(result['text'].split('\n')) > 0 and "RECUERDO VIVIDO" in result['text'].split('\n')[0])
                tag = "REC. VIVIDO" if is_vivid else "MEMORIA"
                header = f"🧠 {tag} RECUPERADO (Fuente: {result['source']} - Similitud: {result['similarity']:.0%})"
                print(f"   [{tag}] Found: {result['source']}")
            else:
                header = f"📚 INFORMACIÓN DE BASE DE CONOCIMIENTO (Fuente: {result['source']} - Similitud: {result['similarity']:.0%})"
                print(f"   [CONOCIMIENTO] Found: {result['source']}")
                
                print(f"   [CONOCIMIENTO] Found: {result['source']}")
            
            # EXPANDIR CONTEXTO SI ES NECESARIO
            final_text = self.expand_context(result, min_words=150)
                
            context_parts.append(f"[{header}]\n{final_text}")
            formatted_context = "\n\n" + "="*20 + "\n\n".join(context_parts) + "\n\n" + "="*20
            return formatted_context, similarity_score
            
        print(f"\n🔍 Búsqueda RAG para: '{query}'")
        print(f"   Mejor resultado descartado: {similarity_score:.1%} (Requiere >= {threshold:.0%})")
        return None, similarity_score
    
    def reload(self):
        """Recarga los documentos"""
        self.load_documents()
    
    def get_stats(self):
        """Obtiene estadísticas del motor RAG"""
        return {
            'documents': len(self.documents),
            'chunks': len(self.chunks),
            'knowledge_dir': self.knowledge_dir
        }
