# 将有膜有漾 Sales Agent 写入服务器 Hermes Profile

这套资产建议作为一个独立 Hermes Profile 上传到服务器，不要混进默认助手里。Profile 名称建议固定为：

```text
ymyy-sales-agent
```

## 服务器上的目标结构

建议放到 `hermes` 部署用户的 home 目录：

```text
/home/hermes/.hermes/
  profiles/
    ymyy-sales-agent/
      profile.yaml
      SOUL.md
      MEMORY.md
  skills/
    ask-with-mom-test/
    diagnose-with-spin-selling/
    answer-customer-faq-transparently/
    negotiate-with-tactical-empathy/
    strengthen-sales-wording-with-influence/
    recommend-film-product/
    handle-film-objections/
    write-sales-followup/
  knowledge-base/
    ymyy-sales-agent/
      ymyy-service-manual.jsonl
      README.md
      source-audit.md
      queries.md
```

如果服务器上 Hermes 实际运行用户不是 `hermes`，把路径里的 `/home/hermes` 换成对应用户的 home 目录。

## 本地打包

在本项目目录运行：

```bash
bash scripts/package_ymyy_hermes_profile.sh
```

会生成：

```text
build/ymyy-hermes-profile/
build/ymyy-hermes-profile.tar.gz
```

## 上传到服务器

方式 A：上传压缩包。

```bash
scp build/ymyy-hermes-profile.tar.gz hermes@<公网IP>:~

ssh hermes@<公网IP>
mkdir -p ~/.hermes
tar -xzf ~/ymyy-hermes-profile.tar.gz -C ~/
```

方式 B：直接同步目录。

```bash
rsync -av build/ymyy-hermes-profile/.hermes/ hermes@<公网IP>:~/.hermes/
```

## 让 Hermes 使用这个 Profile

如果 Hermes 支持 profile 配置命令，优先使用：

```bash
hermes profile list
hermes profile use ymyy-sales-agent
hermes profile inspect ymyy-sales-agent
```

如果当前 Hermes 版本没有 profile 命令，就在 `~/.hermes/config.yaml` 里增加或调整类似配置：

```yaml
default_profile: ymyy-sales-agent

profiles:
  ymyy-sales-agent:
    path: ~/.hermes/profiles/ymyy-sales-agent
    soul: SOUL.md
    memory: MEMORY.md
    skills:
      - ask-with-mom-test
      - diagnose-with-spin-selling
      - answer-customer-faq-transparently
      - negotiate-with-tactical-empathy
      - strengthen-sales-wording-with-influence
      - recommend-film-product
      - handle-film-objections
      - write-sales-followup
    knowledge_base:
      - ~/.hermes/knowledge-base/ymyy-sales-agent/ymyy-service-manual.jsonl

gateways:
  feishu:
    profile: ymyy-sales-agent
```

这里的关键点是：飞书网关收到消息后，要用 `ymyy-sales-agent` 这个 profile 来生成回复。

## 重启并验证

如果 Hermes 是 systemd 服务：

```bash
sudo systemctl restart hermes
sudo systemctl status hermes --no-pager
journalctl -u hermes -f
```

如果是手动启动：

```bash
hermes gateway start
```

在飞书里测试这些问题：

```text
YM-60 质保几年？
春分套餐有什么特点？
客户新买车怕剐蹭，预算中等，推荐什么？
贴完车衣明天能不能洗车？
现在多少钱？
```

预期：

- `YM-60` 回答 3 年，并引用 p.8。
- `春分套餐` 回答 K7+C15，并引用 p.18。
- 价格问题不编造价格，提示以门店最新政策为准。

## 我的建议

第一版不要把这份 profile 设为全局默认助手，而是先只绑定到销售群或测试飞书机器人。确认销售问答稳定后，再开放给更多门店人员。
