import requests
import re
import base64
import subprocess
import concurrent.futures

# 订阅链接列表（支持多个链接）
SUBSCRIBE_URLS = [
    "https://raw.githubusercontent.com/xiaomayi0804/ding/refs/heads/main/vip-jd",
    "https://raw.githubusercontent.com/xiaomayi0804/ding/refs/heads/main/vip-jd2"
    "https://raw.githubusercontent.com/xiaomayi0804/ding/refs/heads/main/vip-jd1"
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
        return None
    
    try:
        # 用 ping 测速
        result = subprocess.run(
            ["ping", "-c", "3", "-W", "2", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            # 提取延迟（取ping最小值）
            match = re.search(r"min/avg/max/mdev = ([\d.]+)/", result.stdout)
            if match:
                latency = float(match.group(1))
                print(f"✅ {host} - {latency} ms")
                return (node, latency)
    except Exception as e:
        print(f"❌ {host} - 测速失败: {e}")
    
    return None

# 从节点URL提取主机名
def extract_host(node):
    match = re.search(r'@(.*?):', node)
    if match:
        return match.group(1)
    return None

# 处理节点
def process_nodes():
    nodes = fetch_nodes()
    print(f"💡 获取到总共 {len(nodes)} 个节点")

    nodes = deduplicate(nodes)
    print(f"🗑️ 去重后剩余 {len(nodes)} 个节点")

    valid_nodes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(test_node, nodes)
        for result in results:
            if result:
                valid_nodes.append(result)

    # 按延迟排序，取前5个
    valid_nodes = sorted(valid_nodes, key=lambda x: x[1])[:5]
    print(f"🚀 保留最快的 {len(valid_nodes)} 个节点")

    # 保存到根目录的 result.txt 文件
    with open("result.txt", "w") as f:
        for node, latency in valid_nodes:
            f.write(f"{node} # {latency}ms\n")

    print("🎉 节点已保存到 result.txt")

if __name__ == "__main__":
    process_nodes()
