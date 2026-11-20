#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2026 lyra XE1POC
"""Build the DM-32UV firmware: RadioFoundry at a pinned public commit plus the patches in integration/current (the DM32
fork: mode row with AM, extended RX, digital monitor on P25/NXDN, AES-256 for P25/NXDN). Never opens a radio and never
fetches the AMBE codec.

    python3 tools/build_current.py [--tree build/current] [--cross PREFIX] [--jobs N]

The image is TREE/build/dm32/rfoundry_dm32.bin; package it with TREE/tools/release.py.
"""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PIN = 'e89121e97a314f0ddd0475f848713ba10710d7db'
UPSTREAM = 'https://github.com/RadioFoundry/RadioFoundry.git'
PATCH_DIR = ROOT / 'integration/current'
PATCHES = (
	'base.patch', 'channel-aes-ysf.patch', 'vfo-rx-bands.patch', 'ysf-tx-pcm.patch',
	'ysf-vfo-identity.patch',
	'vfo-digital.patch',
	'dmr-motorola-privacy.patch',
	'digital-repeater-interop.patch',
	'ysf-dn-narrow.patch',
	'unified-tx-splash.patch',
	'aprs-dual-focus.patch',
	'dual-back-ab.patch',	# dual watch: Back switches A/B, held Back stops
	'aprs-rx-release.patch',	# APRS lets go of FM audio before a retune: P25 engine start (NO TX)
	'p25-audio-fifo.patch',	# RadioFoundry 845f9ad5 (#660): HR_C7000 speaker FIFO starvation, P25 clipping
)


def run(*args, cwd=None):
	subprocess.run([str(a) for a in args], cwd=cwd, check=True)


def out(*args, cwd=None):
	return subprocess.check_output([str(a) for a in args], cwd=cwd, text=True).strip()


def prepare(tree):
	if not (tree / '.git').exists():
		tree.mkdir(parents=True, exist_ok=True)
		run('git', 'init', '-q', tree)
		run('git', 'config', 'core.autocrlf', 'false', cwd=tree)
		run('git', 'remote', 'add', 'origin', UPSTREAM, cwd=tree)
		run('git', 'fetch', '-q', '--depth=1', 'origin', PIN, cwd=tree)
		run('git', 'checkout', '-q', '--detach', PIN, cwd=tree)
	# Always from the pin: a tree left by an earlier build is reset, so the image is the patch's and nothing else
	if out('git', 'rev-parse', 'HEAD', cwd=tree) != PIN:
		raise SystemExit('%s is not at %s: remove it and build again' % (tree, PIN))
	run('git', 'reset', '-q', '--hard', PIN, cwd=tree)
	run('git', 'clean', '-q', '-fdx', '-e', 'build/', cwd=tree)
	for patch in PATCHES:
		run('git', 'apply', '--binary', PATCH_DIR / patch, cwd=tree)
	run('git', 'submodule', 'update', '--init', '--depth=1', 'third_party/FreeRTOS-Kernel', cwd=tree)


def main():
	ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
	ap.add_argument('--tree', type=Path, default=ROOT / 'build/current')
	ap.add_argument('--cross', default=os.environ.get('CROSS', str(ROOT / 'toolchain/bin/csky-elf-')))
	ap.add_argument('--jobs', type=int, default=min(os.cpu_count() or 2, 8))
	args = ap.parse_args()
	tree = args.tree.resolve()
	prepare(tree)
	# The version is this repository's commit, the time its commit time: the patched tree is never committed
	version = out('git', 'rev-parse', '--short=8', 'HEAD', cwd=ROOT)
	git_time = out('git', 'log', '-1', '--format=%ct', 'HEAD', cwd=ROOT)
	run('make', '-j%d' % args.jobs, 'BOARD=dm32', 'CROSS=' + args.cross, 'BUILD=build/dm32', 'GITVERSION=' + version,
	    'GITDIRTY=', 'RFOUNDRY_GIT_TIME=' + git_time, 'all', 'stack-check', cwd=tree)


if __name__ == '__main__':
	main()
