"""
KakaoTalk txt → JSON + Qdrant 업서트 스크립트 (DEBUG 강화, 멀티스레딩)
"""

import argparse
import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import groupby, islice
from pathlib import Path

import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

# ───────────────── 기본 설정 ─────────────────────────────────────
MAIN_SENDER = os.getenv("MAIN_SENDER", "홍길동")  # ★ 메인 화자
MODEL = "text-embedding-3-small"
openai.api_key = os.getenv("OPENAI_API_KEY")

# ───────────────── CLI 파서 ──────────────────────────────────────
def get_args():
    p = argparse.ArgumentParser("KakaoTalk txt preprocessor + Qdrant uploader")
    p.add_argument("-i", "--input-dir", default="kakao_data")
    p.add_argument("-o", "--output-dir", default="processed_data")
    p.add_argument("-e", "--encoding", default="utf-8")
    p.add_argument("--qdrant-host", default="qdrant")
    p.add_argument("--qdrant-port", type=int, default=6333)
    p.add_argument("--collection", default="kakao-chat")
    p.add_argument("--max-workers", type=int, default=os.cpu_count() or 1)
    return p.parse_args()


# ───────────────── 1. 한 줄 파싱 ────────────────────────────────
def parse_line(line: str):
    line = line.strip()
    if (not line or "카카오톡 대화" in line or "저장한 날짜" in line or line.startswith("---------------")):
        return None
    m = re.match(r"\[([^]]+)]\s*\[[^]]+]\s*(.+)", line)
    if not m:
        return None
    sender, message = m.groups()
    if message == "이모티콘" or re.fullmatch(r"\(.*\)", message):
        return None
    return sender.strip(), message.strip()


# ───────────────── 2. 파일 처리 ────────────────────────────────
def preprocess_file(path: Path, encoding: str):
    entries = []
    try:
        with path.open(encoding=encoding) as f:
            for ln in f:
                parsed = parse_line(ln)
                if parsed:
                    entries.append(parsed)
    except Exception as e:
        print(f"Error processing file {path}: {e}")
        return []
        
    merged = [{"sender": s, "message": " ".join(m for _, m in grp)}
              for s, grp in groupby(entries, key=lambda x: x[0])]
    return merged


# ───────────────── 3. 벡터 임베딩 ───────────────────────────────
def embed_texts(texts):
    BATCH, vecs = 96, []
    for i in range(0, len(texts), BATCH):
        try:
            resp = openai.embeddings.create(model=MODEL, input=texts[i:i + BATCH])
            vecs.extend([d.embedding for d in resp.data])
        except Exception as e:
            print(f"OpenAI API 호출 중 오류 발생 (batch {i}): {e}")
            # 해당 배치의 벡터는 비어있는 리스트로 채워 오류가 난 부분을 표시할 수 있습니다.
            # 또는 text 수만큼 None으로 채울 수도 있습니다.
            # 여기서는 API 실패시 프로그램이 중단되도록 re-raise 합니다.
            raise e
    return vecs


# ───────────────── 4. Qdrant 업서트 ────────────────────────────
def upsert_pairs_to_qdrant(pairs, host, port, col, batch_size=200):
    if not pairs:
        print("⚠️  업서트할 쌍이 없습니다."); return

    client = QdrantClient(host=host, port=port, https=False, timeout=30.0)

    print("Vectize Text...")
    vectors = embed_texts([p["query"] for p in pairs])
    vector_dim = len(vectors[0])

    print(f"🔄 컬렉션 '{col}'을(를) 다시 생성합니다. (dim={vector_dim})")
    client.recreate_collection(
        collection_name=col,
        vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
    )

    print(f"📦 총 {len(pairs)}건 → {batch_size}개씩 업서트 중...")
    for idx in range(0, len(pairs), batch_size):
        batch_pairs = pairs[idx:idx + batch_size]
        batch_vectors = vectors[idx:idx + batch_size]

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=batch_vectors[i],
                payload={
                    "content": batch_pairs[i]["response"],
                    "query_sender": batch_pairs[i]["query_sender"],
                    "response_sender": batch_pairs[i]["response_sender"]
                }
            ) for i in range(len(batch_pairs))
        ]
        try:
            client.upsert(collection_name=col, points=points)
            print(f"  ✅ {idx + len(points):>5}/{len(pairs)} 완료")
        except Exception as e:
            print(f"  ❌ batch {idx} 실패: {e}")

    print(f"🎉 전체 업서트 완료 ({len(pairs)}건)")


# ───────────────── 5. 단일 파일 처리 로직 ────────────────────────
def process_single_file(txt_path, encoding, out_dir):
    """단일 .txt 파일을 처리하고, 대화 쌍을 추출합니다."""
    merged = preprocess_file(txt_path, encoding)
    if not merged:
        return [], txt_path.name

    out_path = out_dir / f"{txt_path.stem}.json"
    out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    
    pairs, prev_other = [], None
    for item in merged:
        if item["sender"] == MAIN_SENDER:
            if prev_other:
                pairs.append({
                    "query_sender": prev_other["sender"],
                    "query": prev_other["message"],
                    "response_sender": item["sender"],
                    "response": item["message"]
                })
            prev_other = None
        else:
            prev_other = item
            
    # 디버그 로그
    print(f"\n📄 {txt_path.name} → {out_path} (lines={len(merged)})")
    print(f"[DEBUG] MAIN_SENDER                 : '{MAIN_SENDER}'")
    print(f"[DEBUG] merged total lines          : {len(merged)}")
    print(f"[DEBUG] matched query–response pairs: {len(pairs)}")
    for sample in islice(pairs, 0, 5):
        print(f"   • Q: {sample['query'][:40]}... -> A: {sample['response'][:40]}...")

    return pairs, txt_path.name

# ───────────────── 6. 메인 로직 ────────────────────────────────
def main():
    args = get_args()
    in_dir, out_dir = Path(args.input_dir), Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    txt_files = list(in_dir.glob("*.txt"))
    if not txt_files:
        print(f"입력 디렉토리 '{in_dir}'에 .txt 파일이 없습니다.")
        return

    all_pairs = []
    with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
        print(f"{args.max_workers}개의 스레드로 병렬 처리 시작...")
        
        future_to_file = {
            executor.submit(process_single_file, txt, args.encoding, out_dir): txt 
            for txt in txt_files
        }

        for future in as_completed(future_to_file):
            try:
                pairs, filename = future.result()
                if pairs:
                    all_pairs.extend(pairs)
                print(f"'{filename}' 처리 완료.")
            except Exception as exc:
                filename = future_to_file[future].name
                print(f"'{filename}' 처리 중 예외 발생: {exc}")
    
    print("\n" + "="*50)
    print(f"모든 파일 처리 완료. 총 {len(all_pairs)}개의 대화 쌍을 찾았습니다.")
    print("="*50 + "\n")

    if all_pairs:
        upsert_pairs_to_qdrant(
            all_pairs,
            host=args.qdrant_host,
            port=args.qdrant_port,
            col=args.collection
        )
    else:
        print("Qdrant에 업로드할 대화 쌍이 없습니다.")


if __name__ == "__main__":
    main()
