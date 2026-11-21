"""本地启动入口:等价于 `uvicorn app.main:app --host 0.0.0.0 --port 8000`。

PyCharm 运行配置与命令行都指向这里,省得在 IDE 里拼一长串命令行参数。
依赖 MySQL(本机 3306)与 Milvus(容器端口见 .env 的 MILVUS_URI)已在运行。

监听用 IPv6 双栈 socket(绑 :: 且显式关掉 IPV6_V6ONLY):127.0.0.1、localhost、[::1]
三种写法都能访问。Windows 默认 IPV6_V6ONLY=1,直接绑 "0.0.0.0" 只服务 IPv4,
浏览器一旦把 localhost 解析成 ::1 就会连不上——本机"页面打不开"多半是这个原因。
"""
import socket

import uvicorn


def _dual_stack_socket(port: int) -> socket.socket:
    """绑 :: 并关闭 IPV6_V6ONLY,单个 socket 同时收 IPv4(内核映射为 ::ffff:x)和 IPv6。"""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
    sock.bind(("::", port))
    return sock


if __name__ == "__main__":
    server = uvicorn.Server(uvicorn.Config("app.main:app", log_level="info"))
    server.run(sockets=[_dual_stack_socket(8000)])
