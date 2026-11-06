"""Consumer compatibility and publication boundaries; no network requests."""
import copy
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'scripts'))
from sync_lab import render, validate_feed


def example(source='post-body'):
    return {'id': '21110001-example', 'author': 'creator', 'source_url': 'https://x.com/creator/status/21110001',
            'title': 'Example', 'title_zh': '示例', 'prompt': 'Make a watercolor cat.',
            'images': ['/lab/media/prompts/blobs/' + 'a' * 64 + '.jpg'],
            'provenance': {'type': 'x', 'prompt_source': source, 'note': {'en': 'Author attribution.', 'zh-CN': '作者声明。'}}}


def feed(item):
    return {'slug': 'gpt-image-2-6', 'synced_at': '2026-11-06T00:00:00Z', 'items': [item]}


class ConsumerTests(unittest.TestCase):
    def test_author_sources_and_missing_reference_are_disclosed(self):
        for source in ['post-body', 'self-thread', 'comment']:
            item = example(source)
            item['needs_input'] = True
            result = validate_feed(feed(item))
            self.assertIn('not provided here', render(result))
            self.assertIn('未提供', render(result, zh=True))
            self.assertIn(item['prompt'], render(result))

    def test_promptless_works_are_validated_and_rendered_without_empty_prompt(self):
        item = example('none')
        item.update(prompt='', prompt_unavailable=True)
        result = validate_feed(feed(item))
        for index in [True, False]:
            output = render(result, index=index)
            self.assertIn('no prompt shared', output)
            self.assertNotIn('```text', output)
        self.assertIn('0 prompts · 1 work examples', render(result))
        for change in [{'prompt': 'invented'}, {'prompt_unavailable': False}, {'author': 'invalid handle'},
                       {'images': ['https://private.example/image.jpg']}, {'id': '../bad'}]:
            with self.assertRaises(ValueError):
                validate_feed(feed({**item, **change}))

    def test_clips_have_public_links_and_require_posters(self):
        item = example('self-thread')
        item['videos'] = ['/lab/media/prompts/blobs/' + 'b' * 64 + '.mp4']
        result = validate_feed(feed(item))
        self.assertIn('Play animation 1', render(result))
        self.assertIn('播放动图 1', render(result, zh=True))
        for url in ['https://video.twimg.com/a.mp4', '/lab/media/repository-artifacts/private.mp4',
                    '/lab/media/prompts/blobs/' + 'b' * 64 + '.html']:
            with self.assertRaises(ValueError):
                validate_feed(feed({**item, 'videos': [url]}))
        with self.assertRaises(ValueError):
            validate_feed(feed({**item, 'videos': item['videos'] * 2}))

    def test_duplicate_promptless_identity_cannot_bypass_validation(self):
        item = example('none')
        item.update(prompt='', prompt_unavailable=True)
        result = feed(item)
        result['items'].append(copy.deepcopy(item))
        with self.assertRaises(ValueError):
            validate_feed(result)

    def test_source_context_and_prompt_contract_are_required(self):
        item = example()
        for change in [{'prompt': ''}, {'prompt_unavailable': True}, {'images': []},
                       {'provenance': {'type': 'x', 'prompt_source': 'unknown'}}]:
            with self.assertRaises(ValueError):
                validate_feed(feed({**item, **change}))


if __name__ == '__main__':
    unittest.main()
