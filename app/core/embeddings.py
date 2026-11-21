# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from openai import AsyncOpenAI

from app.config import settings

_CLIENT: AsyncOpenAI | None = None
_BATCH = 10   # 单次嵌入条数上限(百炼硬限,见 embed_texts 注)


def _client() -> AsyncOpenAI:
    """直连嵌入上游(硅基流动的 bge-m3,OpenAI 兼容)。
    进程内单例:复用同一 httpx 连接池,避免每次 embed 新建客户端累积连接/fd。"""
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = AsyncOpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)
    return _CLIENT


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """分批嵌入:阿里云百炼的单次上限是 10 条(超过报 batch size is invalid),
    硅基流动虽然能吃整批,按 10 条切也不影响结果——顺序由返回顺序保证。"""
    if not texts:
        return []
    out: list[list[float]] = []
    for i in range(0, len(texts), _BATCH):
        resp = await _client().embeddings.create(model=settings.embed_model,
                                                 input=texts[i:i + _BATCH])
        out.extend(d.embedding for d in resp.data)
    return out


async def embed_query(text: str) -> list[float]:
    return (await embed_texts([text]))[0]
