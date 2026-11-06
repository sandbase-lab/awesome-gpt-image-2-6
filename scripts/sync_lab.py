#!/usr/bin/env python3
"""Fetch reviewed Lab data, render bilingual Markdown, or validate deterministic output."""
import argparse
import json
import pathlib
import re
import urllib.request
from config import CFG, SITE

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/prompts.json'


def validate_feed(feed):
    if feed.get('slug') != CFG['slug'] or not feed.get('synced_at') or not feed.get('items'):
        raise ValueError('Expected a non-empty, dated Lab collection')
    seen = set()
    for item in feed['items']:
        provenance = item.get('provenance', {})
        identity = item['id']
        if not re.fullmatch(r'\d{6,25}-[a-z0-9-]{1,40}', identity) or identity in seen:
            raise ValueError('Invalid or duplicate case identity')
        seen.add(identity)
        if not re.fullmatch(r'[A-Za-z0-9_]{1,15}', item['author']):
            raise ValueError('Invalid creator handle')
        source = item['source_url']
        if not re.fullmatch(r'https://x\.com/[A-Za-z0-9_]{1,15}/status/\d{6,25}', source):
            raise ValueError('Missing original X attribution')
        prompt_source = provenance.get('prompt_source')
        if provenance.get('type') != 'x' or prompt_source not in {'post-body', 'self-thread', 'comment', 'none'}:
            raise ValueError('Missing reviewed prompt provenance')
        if prompt_source == 'none':
            if item.get('prompt_unavailable') is not True or item.get('prompt') != '':
                raise ValueError('Promptless works must be explicitly labeled')
        elif not isinstance(item.get('prompt'), str) or not item['prompt'].strip() or item.get('prompt_unavailable'):
            raise ValueError('Missing reviewed prompt text')
        if not item.get('images'):
            raise ValueError('Missing result preview')
        for url in item['images'] + item.get('input_images', []):
            if not re.fullmatch(r'/lab/media/(?:prompts/(?:blobs/[a-f0-9]{64}|[a-z0-9-]{2,40}/\d{6,25}/\d{1,2})|static/downloads/(?:[a-z0-9][a-z0-9._-]*/)*[a-z0-9][a-z0-9._-]*)\.(?:jpg|jpeg|png|webp)', url):
                raise ValueError('Media must be a public Lab image; no independent X fetch')
        videos = item.get('videos', [])
        if len(videos) > len(item['images']):
            raise ValueError('Every clip requires a result preview')
        for url in videos:
            if not re.fullmatch(r'/lab/media/prompts/blobs/[a-f0-9]{64}\.mp4', url):
                raise ValueError('Clips must be public Lab MP4 objects')
        if not all(provenance.get('note', {}).get(lang) for lang in ('en', 'zh-CN')):
            raise ValueError('Missing bilingual source context')
    return feed


def text(value):
    return re.sub(r'([\\`*_{}\[\]<>()#!|])', r'\\\1', value.replace('\r', '').replace('\n', ' '))


def prompt_block(prompt):
    fence = '`' * max(3, max((len(x) + 1 for x in re.findall(r'`+', prompt)), default=3))
    return f'{fence}text\n{prompt}\n{fence}'


def render(feed, zh=False, index=False):
    name = CFG['name']
    guide = 'docs/zh-CN/' if zh else 'docs/'
    shown = feed['items']
    works = sum(bool(item.get('prompt_unavailable')) for item in shown)
    prompts = len(shown) - works
    if index:
        out = [f'# {name} ' + ('提示词索引' if zh else 'prompt index'), '',
               ('原文按来源保留，不自动翻译。' if zh else 'Prompts retain their original wording and language.'), '']
    else:
        out = [f'# Awesome {name}', '',
               ('[English](README.md) · 简体中文' if zh else 'English · [简体中文](README.zh-CN.md)'), '',
               ('来自 X 原作者的图片、动图与原始提示词，由 [SandBase Lab](' if zh else 'Images, animations and original prompts from X creators, curated by [SandBase Lab](') + CFG['lab_collection'] + ').', '',
               (f"**{len(shown)} 个案例：{prompts} 条提示词 · {works} 个作品示例** · Lab 数据日期：{feed['synced_at']}。" if zh else f"**{len(shown)} examples: {prompts} prompts · {works} work examples** · Lab snapshot: {feed['synced_at']}."), '',
               ('模型归属依据作者的原帖声明；具体变体可能未知，尚未由 SandBase 复跑。图片和提示词权利属于原作者。' if zh else 'Model attribution follows the original creator’s claim. The variant may be unknown; SandBase has not rerun these examples. Images and prompts remain their creators’ work.'), '',
               f"[{'提示词索引' if zh else 'Prompt index'}]({guide}prompts.md) · [{'提示词指南' if zh else 'Prompt guide'}]({guide}prompt-guide.md) · [{'使用教程' if zh else 'Tutorial'}]({guide}tutorial.md) · [{'模型比较' if zh else 'Model comparison'}]({guide}model-comparison.md)", '',
               f"[{'在 Lab 浏览' if zh else 'Browse on Lab'}]({CFG['lab_collection']}) · [Flare]({CFG['model_page']}) · [Flare Edit]({CFG['edit_page']})", '']
    for item in shown:
        title = item.get('title_zh', item['title']) if zh else item['title']
        page = f"{CFG['lab_collection']}/{item['id']}"
        out += [f"## [{text(title)}]({page})", '', f"[@{item['author']}]({item['source_url']})", '']
        if not index:
            out += [f"[![{text(title)}]({SITE + url})]({page})" for url in item['images']]
            out += ['']
        if item.get('videos'):
            out += [f"[{'播放动图' if zh else 'Play animation'} {n + 1}]({SITE + url})" for n, url in enumerate(item['videos'])]
            out += ['']
        out += [text(item['provenance']['note']['zh-CN' if zh else 'en']), '']
        if item.get('prompt_unavailable'):
            out += [('**作品示例：作者未公开提示词。**' if zh else '**Work example: no prompt shared by the author.**'), '']
        else:
            out += [prompt_block(item['prompt']), '']
        if item.get('needs_input') and not item.get('input_images'):
            out += [('此提示词需要参考输入图；本页未提供，请准备自己有权使用的素材。' if zh else 'This prompt requires a reference input that is not provided here. Supply your own authorized material.'), '']
        if item.get('input_images'):
            out += [('参考输入图：' if zh else 'Reference inputs:'), '']
            out += [f"[{'输入图' if zh else 'Input'} {n + 1}]({SITE + url})" for n, url in enumerate(item['input_images'])]
            out += ['']
    if not index:
        out += ['## ' + ('贡献与权利' if zh else 'Contributing and rights'), '',
                ('通过 Issue 提交原帖、Prompt 和对应媒体。先进入 Lab 审核，再同步至本仓库。' if zh else 'Submit the original post, prompt and media mapping through an issue. Additions are reviewed in Lab before syncing here.'), '',
                '[Contributing](CONTRIBUTING.md) · [Media rights](MEDIA-RIGHTS.md)', '',
                ('本项目与 OpenAI 无隶属或背书关系。' if zh else 'Not affiliated with or endorsed by OpenAI.'), '']
    return '\n'.join(out)


def outputs(feed):
    return {'README.md': render(feed), 'README.zh-CN.md': render(feed, zh=True),
            'docs/prompts.md': render(feed, index=True), 'docs/zh-CN/prompts.md': render(feed, zh=True, index=True)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true', help='Render already saved Lab data without network')
    parser.add_argument('--check', action='store_true', help='Validate data and deterministic Markdown')
    parser.add_argument('--fixture', type=pathlib.Path, help='Local Lab feed for prepublication verification only')
    args = parser.parse_args()
    if args.check or args.build:
        feed = validate_feed(json.loads(DATA.read_text(encoding='utf-8')))
    elif args.fixture:
        feed = validate_feed(json.loads(args.fixture.read_text(encoding='utf-8')))
    else:
        request = urllib.request.Request(CFG['lab_data'], headers={'Accept': 'application/json', 'User-Agent': CFG['repo'] + '/1.0'})
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.url != CFG['lab_data']:
                raise ValueError('Unexpected feed redirect')
            feed = validate_feed(json.load(response))
    if not args.check:
        DATA.parent.mkdir(exist_ok=True)
        DATA.write_text(json.dumps(feed, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for path, content in outputs(feed).items():
        target = ROOT / path
        if args.check:
            if target.read_text(encoding='utf-8') != content:
                raise ValueError(f'Stale generated Markdown: {path}')
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding='utf-8')
    if args.check:
        for path in ROOT.rglob('*'):
            if '.git' not in path.parts and path.is_file() and path.suffix.lower() in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.mp4', '.zip'}:
                raise ValueError('Media belongs in Lab R2, not this repository')
    print(f"{'Validated' if args.check else 'Rendered'} {len(feed['items'])} Lab examples")


if __name__ == '__main__':
    main()
