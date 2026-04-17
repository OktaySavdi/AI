---
name: "videodb"
description: >
  Video and audio: ingest, search, edit, generate, and stream with VideoDB.
  Activate when working with video/audio processing or VideoDB integration.
metadata:
  version: 1.0.0
  category: engineering
---

# VideoDB Skill

## What is VideoDB

VideoDB is a database purpose-built for video and audio content. It provides:
- Upload and store video/audio at scale
- Scene-level semantic search
- Programmatic video editing (trim, splice, overlay)
- Real-time streaming with dynamic compilation

## Python SDK Basics

```python
import videodb
conn = videodb.connect(api_key="YOUR_API_KEY")
coll = conn.get_collection()

# Upload a video
video = coll.upload(url="https://example.com/video.mp4")
print(video.id)

# Index for semantic search
video.index_spoken_words()   # transcribes and indexes audio
video.index_scenes()         # indexes visual content
```

## Semantic Search

```python
# Search across all indexed videos
results = coll.search("person explaining machine learning")
for result in results.get_shots():
    print(result.video_id, result.start, result.end, result.text)

# Search within a specific video
results = video.search("product demo")
stream_url = results.compile_stream()
print(stream_url)  # playable URL of just the matching segments
```

## Programmatic Editing

```python
from videodb import play_stream
from videodb.timeline import Timeline, VideoAsset, AudioAsset

# Create a timeline
timeline = Timeline(conn)

# Add video segments
video_asset = VideoAsset(asset_id=video.id, start=10, end=30)
timeline.add_inline(video_asset)

# Add background audio
audio = coll.upload(url="https://example.com/music.mp3")
audio_asset = AudioAsset(asset_id=audio.id, start=0, end=20)
timeline.add_overlay(0, audio_asset)

# Generate and stream
stream_url = timeline.generate_stream()
play_stream(stream_url)
```

## Transcription & Subtitles

```python
# Get transcript
transcript = video.get_transcript()
for segment in transcript:
    print(f"{segment.start:.1f}s: {segment.text}")

# Generate SRT file
srt = video.generate_srt()
with open("subtitles.srt", "w") as f:
    f.write(srt)
```

## Use Cases

- AI video search engines ("find all clips mentioning X")
- Automated highlight reels from long recordings
- Podcast clip extraction for social media
- Video RAG (retrieval-augmented generation with video context)
