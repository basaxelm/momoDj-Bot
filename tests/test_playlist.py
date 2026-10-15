import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import yt_dlp
from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import ExtractorError

from cogs.music_commands import MusicCommands
from music.audio_source import AudioSourceExtractor, PlaylistResult, YTDL_BASE_OPTIONS
from music.queue import MusicQueue
from music.song import Song


def track(title):
    return {
        'title': title,
        'url': f'https://audio.invalid/{title}.m4a',
        'webpage_url': f'https://video.invalid/{title}',
        'duration': 120,
    }


class PlaylistExtractionTests(unittest.IsolatedAsyncioTestCase):
    async def extract(self, entries, query='https://www.youtube.com/playlist?list=test'):
        with patch.object(AudioSourceExtractor, '_extract_info', return_value={'entries': entries}):
            return await AudioSourceExtractor().extract_song(query, requester='requester')

    async def test_mixed_playlist_preserves_order_and_requester(self):
        result = await self.extract([track('first'), None, {'title': 'no audio'}, track('last')])
        self.assertIsInstance(result, PlaylistResult)
        self.assertEqual([song.title for song in result.songs], ['first', 'last'])
        self.assertEqual(result.skipped_count, 2)
        self.assertTrue(all(song.requester == 'requester' for song in result.songs))

    async def test_first_video_unavailable(self):
        result = await self.extract([None, track('available')])
        self.assertEqual([song.title for song in result.songs], ['available'])
        self.assertEqual(result.skipped_count, 1)

    async def test_no_playable_entries_is_an_error(self):
        for entries in ([], [None, None], [{'title': 'no stream'}], None):
            with self.subTest(entries=entries):
                with self.assertRaisesRegex(ValueError, 'playlist no contiene canciones disponibles'):
                    await self.extract(entries)

    async def test_healthy_playlist(self):
        result = await self.extract([track('first'), track('second')])
        self.assertEqual(len(result.songs), 2)
        self.assertEqual(result.skipped_count, 0)

    async def test_search_returns_first_playable_song(self):
        result = await self.extract([None, track('first'), track('second')], query='a song')
        self.assertIsInstance(result, Song)
        self.assertEqual(result.title, 'first')

    async def test_empty_search_is_an_error(self):
        with self.assertRaisesRegex(ValueError, 'búsqueda'):
            await self.extract([None], query='a song')

    async def test_single_song(self):
        with patch.object(AudioSourceExtractor, '_extract_info', return_value=track('single')):
            result = await AudioSourceExtractor().extract_song('https://youtu.be/test')
        self.assertIsInstance(result, Song)
        self.assertEqual(result.title, 'single')

    async def test_unavailable_single_song(self):
        with patch.object(AudioSourceExtractor, '_extract_info', return_value=None):
            with self.assertRaisesRegex(ValueError, 'enlace puede no estar disponible'):
                await AudioSourceExtractor().extract_song('https://youtu.be/test')

    async def test_spotify_still_resolves_to_youtube_search(self):
        extractor = AudioSourceExtractor()
        with patch.object(extractor, '_resolve_spotify_oembed', AsyncMock(return_value='artist song')):
            with patch.object(extractor, '_extract_info', return_value={'entries': [track('match')]}) as extract:
                result = await extractor.extract_song('https://open.spotify.com/track/test')
        self.assertIsInstance(result, Song)
        extract.assert_called_once_with('ytsearch:artist song')

    async def test_concurrent_requests_use_separate_extractors_and_options(self):
        instances = []
        options_seen = []

        def create(options):
            options_seen.append(options)
            instance = MagicMock()
            instance.__enter__.return_value = instance
            instance.extract_info.return_value = track('single')
            instances.append(instance)
            return instance

        with patch('music.audio_source.yt_dlp.YoutubeDL', side_effect=create):
            extractor = AudioSourceExtractor()
            await asyncio.gather(
                extractor.extract_song('https://youtu.be/first'),
                extractor.extract_song('https://youtu.be/second'),
            )
        self.assertEqual(len(instances), 2)
        self.assertIsNot(options_seen[0], options_seen[1])
        self.assertIsNot(options_seen[0]['js_runtimes'], options_seen[1]['js_runtimes'])
        self.assertNotIn('logger', YTDL_BASE_OPTIONS)
        for instance in instances:
            instance.__exit__.assert_called_once()

    async def test_real_ytdlp_continues_after_extractor_error(self):
        class FixtureIE(InfoExtractor):
            _VALID_URL = r'fixture:(?P<id>playlist|broken|first|last)'

            def _real_extract(self, url):
                video_id = self._match_id(url)
                if video_id == 'playlist':
                    return self.playlist_result([
                        self.url_result(f'fixture:{item}', ie=FixtureIE.ie_key())
                        for item in ('broken', 'first', 'broken', 'last')
                    ], playlist_id='test')
                if video_id == 'broken':
                    raise ExtractorError('Video unavailable', expected=True)
                return dict(track(video_id), id=video_id, ext='m4a', vcodec='none', acodec='aac')

        real_ytdl = yt_dlp.YoutubeDL

        def create(options):
            options = dict(options)
            options.pop('cookiefile', None)
            ytdl = real_ytdl(options, auto_init=False)
            ytdl.add_info_extractor(FixtureIE())
            return ytdl

        with patch('music.audio_source.yt_dlp.YoutubeDL', side_effect=create):
            with self.assertLogs('momoDj', level='WARNING') as logs:
                # Invoke the real yt-dlp processing pipeline without network access.
                data = await asyncio.to_thread(AudioSourceExtractor._extract_info, 'fixture:playlist')
                with patch.object(AudioSourceExtractor, '_extract_info', return_value=data):
                    result = await AudioSourceExtractor().extract_song('https://www.youtube.com/playlist?list=test')
        self.assertEqual([song.title for song in result.songs], ['first', 'last'])
        self.assertEqual(result.skipped_count, 2)
        self.assertTrue(any('Video unavailable' in line for line in logs.output))


class PlayCommandTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.player = SimpleNamespace(
            queue=MusicQueue(), voice_client=MagicMock(),
            is_playing=False, is_paused=False, play_next=AsyncMock(),
        )
        self.cog = MusicCommands(MagicMock(), lambda guild: self.player, MagicMock())
        self.cog._ensure_voice_connection = AsyncMock(return_value=self.player.voice_client)
        self.ctx = MagicMock()
        self.loading = SimpleNamespace(edit=AsyncMock(), delete=AsyncMock())
        self.ctx.send = AsyncMock(return_value=self.loading)
        self.song = Song(**{key: value for key, value in track('good').items() if key != 'url'},
                         stream_url=track('good')['url'])

    async def play(self):
        await MusicCommands.play.callback(self.cog, self.ctx, query='https://www.youtube.com/playlist?list=test')

    async def test_partial_playlist_enqueues_and_reports_skips(self):
        self.cog.extractor.extract_song = AsyncMock(return_value=PlaylistResult([self.song], 2))
        await self.play()
        self.assertEqual(list(self.player.queue.upcoming), [self.song])
        description = self.loading.edit.call_args.kwargs['embed'].description
        self.assertIn('**1** canciones', description)
        self.assertIn('omitieron **2**', description)
        self.player.play_next.assert_awaited_once()

    async def test_healthy_playlist_does_not_warn_or_interrupt_playback(self):
        self.player.is_playing = True
        self.cog.extractor.extract_song = AsyncMock(return_value=PlaylistResult([self.song], 0))
        await self.play()
        self.assertEqual(list(self.player.queue.upcoming), [self.song])
        self.assertNotIn('omitieron', self.loading.edit.call_args.kwargs['embed'].description)
        self.player.play_next.assert_not_awaited()

    async def test_failed_playlist_leaves_existing_queue_untouched(self):
        self.player.queue.add(self.song)
        self.cog.extractor.extract_song = AsyncMock(side_effect=ValueError('La playlist no contiene canciones disponibles'))
        with self.assertLogs('momoDj', level='ERROR'):
            await self.play()
        self.assertEqual(list(self.player.queue.upcoming), [self.song])
        self.assertIn('no contiene canciones disponibles', self.loading.edit.call_args.kwargs['content'])
        self.player.play_next.assert_not_awaited()

    async def test_single_song_starts_playback(self):
        self.cog.extractor.extract_song = AsyncMock(return_value=self.song)
        await self.play()
        self.assertEqual(list(self.player.queue.upcoming), [self.song])
        self.loading.delete.assert_awaited_once()
        self.player.play_next.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
