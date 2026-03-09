import httpx

base = 'http://localhost:8000/api/v1/agents'
agent_id = 'did:silicon:agent:55e3448eb352466e887e03890d112345'

print("=" * 50)
print("测试记忆系统")
print("=" * 50)

# 创建记忆
print("\n1. 创建记忆...")
r = httpx.post(f'{base}/{agent_id}/memories', json={'content': '今天学习了数据库知识', 'memory_type': 'long_term'})
print(f'   状态：{r.status_code}')
print(f'   结果：{r.json()}')

# 再创建一条
print("\n2. 创建第二条记忆...")
r = httpx.post(f'{base}/{agent_id}/memories', json={'content': '硅基世界部署成功', 'memory_type': 'short_term'})
print(f'   状态：{r.status_code}')
print(f'   结果：{r.json()}')

# 获取记忆列表
print("\n3. 获取记忆列表...")
r = httpx.get(f'{base}/{agent_id}/memories')
print(f'   状态：{r.status_code}')
for m in r.json():
    print(f'   - [{m["memory_type"]}] {m["content"]}')

print("\n" + "=" * 50)
print("测试完成!")
print("=" * 50)
