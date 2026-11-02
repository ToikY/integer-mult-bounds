"""Payload helpers for the compressed word. Apache-2.0.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
"""
import gzip
import json


def payload(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def matches_shipped(value, compressed):
    return gzip.decompress(compressed) == payload(value)
