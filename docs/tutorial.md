# Try a prompt

1. Open an example on [Lab](https://www.sandbase.ai/lab/prompts/gpt-image-2-6), read its source note and copy the original prompt. Check any reference inputs separately.
2. Open [GPT Image 2.6 Flare](https://www.sandbase.ai/models/openai/gpt-image-2.6-flare) for text-to-image, or [Flare Edit](https://www.sandbase.ai/models/openai/gpt-image-2.6-flare/edit) when an input image is required. Check current parameters and pricing there.
3. Inspect the result against your intended subject, composition and details. Record your model variant and settings if sharing a comparison.

Using the SandBase CLI after connecting your account:

```bash
npx -y @sandbaseai/cli@latest inspect openai/gpt-image-2.6-flare
npx -y @sandbaseai/cli@latest run openai/gpt-image-2.6-flare -i '{"prompt":"a realistic photo of a woman holding a cup of tea inside her home"}' -w -o result.json
```

Image generation is billed; the free X data-call allowance does not cover model generation. Flare is an available endpoint, not proof that the original creator used this variant. These instructions do not promise GIF output or exact reproduction.
