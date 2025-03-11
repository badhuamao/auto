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
            ["ping", "-c", "3", "-W", "2", host],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f"🧪 Ping 完整结果:\n{result.stdout}")  # ➡️ 打印完整的 ping 输出
        if result.returncode == 0:
            match = re.search(r"min/avg/max/mdev = ([\d.]+)/", result.stdout)
            if match:
                latency = float(match.group(1))
                print(f"✅ 匹配到延迟值: {latency} ms")
                return (node, latency)
            else:
                print("❌ 正则匹配失败！可能是 ping 输出格式不同。")
        else:
            print(f"❌ Ping 测速失败，返回码: {result.returncode}")
        
        # 如果 ping 失败，改用 curl 测速
        result = subprocess.run(
            ["curl", "-o", "/dev/null", "-s", "-w", "%{time_connect}", f"http://{host}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            latency = float(result.stdout.strip()) * 1000  # 单位转换为 ms
            print(f"✅ 使用 curl 测速: {host} - {latency:.2f} ms")
            return (node, latency)
        else:
            print(f"❌ curl 测速失败，返回码: {result.returncode}")
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

    # 输出到 result.txt
    if not valid_nodes:
        print("⚠️ 未获取到有效节点，输出为空！")
    else:
        with open("result.txt", "w") as f:
            for node, latency in valid_nodes:
                f.write(f"{node} # {latency}ms\n")
                print(f"📝 输出到文件: {node} - {latency}ms")  # ✅ 调试输出
        print("🎯 已保存到 result.txt")

if __name__ == "__main__":
    process_nodes()
