# 使用教程

1. 打开 [Lab 案例](https://www.sandbase.ai/lab/prompts/gpt-image-2-6)，阅读来源说明并复制原始 Prompt。参考输入图与结果图分别核对。
2. 纯文字生图可打开 [GPT Image 2.6 Flare](https://www.sandbase.ai/models/openai/gpt-image-2.6-flare)；需要输入图则使用 [Flare Edit](https://www.sandbase.ai/models/openai/gpt-image-2.6-flare/edit)。参数和费用以模型页面当前信息为准。
3. 检查生成结果中的主体、构图和细节。分享对比时记录实际模型变体和参数。

连接账号后，可以使用 SandBase CLI：

```bash
npx -y @sandbaseai/cli@latest inspect openai/gpt-image-2.6-flare
npx -y @sandbaseai/cli@latest run openai/gpt-image-2.6-flare -i '{"prompt":"a realistic photo of a woman holding a cup of tea inside her home"}' -w -o result.json
```

模型生图单独计费，X 数据接口的免费额度不涵盖生图。Flare 是可用调用入口，不代表原作者使用的就是这个变体。本教程不承诺 GIF 输出或完全复现原图。
