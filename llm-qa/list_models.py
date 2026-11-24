import json

d = json.load(open("/tmp/ds_models.json"))
ids = sorted(m["id"] for m in d["data"])
print("deepseek 相关:")
for i in [x for x in ids if "deepseek" in x.lower()]:
    print("  ", i)
print("qwen 文本类（前 25）:")
for i in [x for x in ids if x.startswith("qwen")][:25]:
    print("  ", i)
