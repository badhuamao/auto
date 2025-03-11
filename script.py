import requests
import re
import base64
import subprocess
import concurrent.futures

# 订阅链接列表（支持多个链接）
SUBSCRIBE_URLS = [
    "https://example.com/subscription1",
    "https://example.com/subscription2"
]

# 获取节点（支持多个链接）
def fetch_nodes():
    nodes = []
    for url in SUBSCRIBE_URLS:
        try:
            print(f"🌐 获取订阅: {url}")
            response = requests.get(url)
            if response.status_code != 200:
                print(f"❌ 无法获取 {url}，状态码: {response.status_code}")
                continue
            decoded = base64.b64decode(response.content).decode('utf-8')
            fetched_nodes = decoded.strip().split('\n')
            print(f"🧪 解码后节点内容:\n{decoded}")  # ➡️ 打印解码后的内容
            nodes.extend(fetched_nodes)
            print(f"✅ 从 {url} 获取到 {len(fetched_nodes)} 个节点")
        except Exception as e:
            print(f"❌ 获取 {url} 失败: {e}")
    return nodes

# 去重
def deduplicate(nodes):
    return list(set(nodes))

# 测速（返回延迟时间）
def test_node(node):
    host = extract_host(node)
    if not host:
        print(f"❓ 未能提取主机名: {node}")
        return None
    
    try:
        print(f"🚀 测速 {host} ...")
        # 尝试使用 ping 测速
        result = subprocess.run(
  
