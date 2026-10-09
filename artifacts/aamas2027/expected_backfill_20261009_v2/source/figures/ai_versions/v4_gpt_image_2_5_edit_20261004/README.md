# v4 — explicit GPT Image 2.5 edit

Status: generation pending.

Purpose: first candidate generated with the explicitly selected `gpt-image-2.5`
model, editing the retained v1 AI image to improve print-scale typography and
arrow/label spacing.

Input image:
`../v1_collabllm_style_20261004/overview_ai.png`

The exact prompt is in `prompt.md`. The execution command, response metadata,
SHA-256, dimensions, and visual review will be appended after the API call.

## Execution attempts

1. The bundled CLI was invoked with `--model gpt-image-2.5`, `--quality high`,
   and `--size auto`, but the installed OpenAI SDK raised a local
   `TypeError: edit() got an unexpected keyword argument 'quality'` before any
   network request. This failure is retained in `api_call.log`.
2. The equivalent native multipart request was then sent to the internal
   OpenAI-compatible endpoint. The endpoint returned HTTP 400 with
   `PRE-006: gpt-image-2.5模型的配置不存在`. Therefore no image was generated;
   there is no valid v4 asset or model2.5 result to evaluate.

The local cockpit catalog advertises the slug as API-supported, but the actual
internal endpoint currently has no corresponding image-model configuration.
This discrepancy is recorded rather than silently substituting another model.

3. A read-only `GET /api/openai/v1/models` check completed with HTTP 200 and
   returned one model, `qwen3-coder-plus`; no image model was listed. The raw
   response was kept outside the repository at `/tmp/earning_roles_idealab_models.json`
   and no credential was written to disk.

Conclusion: this version has a valid prompt and a fully reproducible attempted
route, but no generated image. A real `gpt-image-2.5` result requires the
IdeaLab image-model configuration to be enabled or a separate image-capable
OpenAI-compatible endpoint and credential.
