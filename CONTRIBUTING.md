# Contributing

Suggest an example with its original X URL, verbatim prompt, result image and any required reference inputs. Explain the author's model claim. Suggestions enter Lab review before this repository consumes them. Do not submit copied media files or API keys.

Developers: run `python3 scripts/sync_lab.py` to read the public Lab feed, then `python3 scripts/sync_lab.py --check`. The workflow is manual; no X API credentials are needed. `--build` regenerates Markdown offline. Upstream removals are respected on the next sync.

# 贡献

提交原始 X 链接、逐字提示词、结果图和必要的参考输入图，并说明作者如何标注模型。新增案例先进入 Lab 审核，再同步到本仓库。请勿上传媒体副本或密钥。

运行上述同步与校验命令即可更新。当前仅手动触发，不需要 X API 凭据。上游删除会在下次同步时生效。
