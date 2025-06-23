"""
KakaoTalk txt → JSON + Qdrant 업서트 스크립트 (DEBUG 강화)
"""

import argparse, json, os, re, uuid
from itertools import groupby, islice
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import openai

# ───────────────── 기본 설정 ─────────────────────────────────────
MAIN_SENDER = os.getenv("MAIN_SENDER", "장보광")            # ★ 메인 화자
QDRANT_APIKEY = os.getenv("X_API_KEY") 
MODEL       = "text-embedding-3-small"
openai.api_key = os.getenv("OPENAI_API_KEY")

# ───────────────── CLI 파서 ──────────────────────────────────────
def get_args():
    p = argparse.ArgumentParser("KakaoTalk txt preprocessor + Qdrant uploader")
    p.add_argument("-i", "--input-dir",  default="kakao_data")
    p.add_argument("-o", "--output-dir", default="processed_data")
    p.add_argument("-e", "--encoding",   default="utf-8")
    p.add_argument("--qdrant-host", default="qdrant")
    p.add_argument("--qdrant-port", type=int, default=6333)
    p.add_argument("--collection",  default="kakao-chat")
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
    for ln in path.open(encoding=encoding):
        parsed = parse_line(ln)
        if parsed:
            entries.append(parsed)
    merged = [{"sender": s, "message": " ".join(m for _, m in grp)}
              for s, grp in groupby(entries, key=lambda x: x[0])]
    return merged

# ───────────────── 3. 벡터 임베딩 ───────────────────────────────
def embed_texts(texts):
    BATCH, vecs = 96, []
    for i in range(0, len(texts), BATCH):
        resp = openai.embeddings.create(model=MODEL, input=texts[i:i+BATCH])
        vecs.extend([d.embedding for d in resp.data])
    return vecs

# ───────────────── 4. Qdrant 업서트 ────────────────────────────
def upsert_pairs_to_qdrant(pairs, host, port, col, batch_size=200):
    if not pairs:
        print("⚠️  업서트할 쌍이 없습니다."); return

    client = QdrantClient(                          # ★ API 키·HTTPS 설정
        host=host,
        port=port,
        api_key=QDRANT_APIKEY,
        https=False,
        timeout=30.0
    )

    vectors = embed_texts([p["query"] for p in pairs])
    vector_dim = len(vectors[0])

    # 컬렉션 확인/생성
    if col not in [c.name for c in client.get_collections().collections]:
        print(f"🆕 컬렉션 '{col}' 생성 (dim={vector_dim})")
        client.recreate_collection(
            collection_name=col,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
        )

    print(f"📦 총 {len(pairs)}건 → {batch_size}개씩 업서트 중...")
    for idx in range(0, len(pairs), batch_size):
        batch_pairs   = pairs[idx:idx+batch_size]
        batch_vectors = vectors[idx:idx+batch_size]

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=batch_vectors[i],
                payload={
                    "content":         batch_pairs[i]["response"],
                    "query_sender":    batch_pairs[i]["query_sender"],
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


# ───────────────── 5. 메인 로직 ────────────────────────────────
def main():
    args = get_args()
    in_dir, out_dir = Path(args.input_dir), Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for txt in in_dir.glob("*.txt"):
        merged = preprocess_file(txt, args.encoding)
        out_path = out_dir / f"{txt.stem}.json"
        out_path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📄 {txt.name} → {out_path} (lines={len(merged)})")

        # ── 메인↔상대 쌍 추출
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

        # ── 디버그 로그 ────────────────────────────────
        print(f"[DEBUG] MAIN_SENDER                 : '{MAIN_SENDER}'")
        print(f"[DEBUG] merged total lines          : {len(merged)}")
        print(f"[DEBUG] matched query–response pairs: {len(pairs)}")
        # 첫 5개 샘플 출력
        for sample in islice(pairs, 0, 5):
            print(f"   • Q: {sample['query'][:40]}... -> A: {sample['response'][:40]}...")

        # ── Qdrant 업서트 ─────────────────────────────
        upsert_pairs_to_qdrant(
            pairs,
            host=args.qdrant_host,
            port=args.qdrant_port,
            col=args.collection
        )

if __name__ == "__main__":
    main()
