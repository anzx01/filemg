import json

# 读取配置文件
with open('dist/config/field_mapping_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 测试路径
test_paths = [
    "D:/sjdataapp/AI比赛测试数据/华夏银行.xlsx",
    "D:/sjdataapp/AI比赛测试数据/建设银行.xlsx", 
    "D:/sjdataapp/AI比赛测试数据/招商银行.xlsx"
]

print("配置文件中的路径:")
for i, path in enumerate(config.keys(), 1):
    print(f"{i:2d}. {path}")

print("\n测试路径匹配:")
for test_path in test_paths:
    if test_path in config:
        print(f"✅ {test_path} - 匹配成功")
    else:
        print(f"❌ {test_path} - 匹配失败")
