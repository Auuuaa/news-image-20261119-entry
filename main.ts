// News-image entry for Thursday 19 November 2026 (Node 22, standard
// library only). The image is the entry.png beside this file; the program
// copies it to /output/entry.png after checking it is a whole PNG within
// the competition's limits (at most 1024x1024 pixels, at most 1 MiB).
// Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

// CRC-32 (IEEE 802.3) over a Buffer, built from the standard polynomial.
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf) {
  let c = 0xffffffff;
  for (const byte of buf) {
    c = CRC_TABLE[(c ^ byte) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

const image = readFileSync(new URL('./entry.png', import.meta.url));

if (image.length > 1048576) {
  throw new Error(`entry.png is ${image.length} bytes, over the 1 MiB limit`);
}
const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!image.subarray(0, 8).equals(PNG_SIGNATURE)) {
  throw new Error('entry.png is not a PNG file');
}

// Walk every chunk: length, type, data, CRC. The first chunk must be IHDR
// (its width and height are at most 1024), the last must be IEND, and no
// bytes may follow it -- so the file is a whole PNG, not a truncation.
let offset = 8;
let seenIhdr = false;
let seenIend = false;
while (offset < image.length) {
  if (offset + 12 > image.length) {
    throw new Error('entry.png ends in the middle of a chunk');
  }
  const length = image.readUInt32BE(offset);
  const type = image.toString('latin1', offset + 4, offset + 8);
  const dataStart = offset + 8;
  const dataEnd = dataStart + length;
  if (dataEnd + 4 > image.length) {
    throw new Error(`PNG chunk ${type} is truncated`);
  }
  const storedCrc = image.readUInt32BE(dataEnd);
  const computedCrc = crc32(image.subarray(offset + 4, dataEnd));
  if (storedCrc !== computedCrc) {
    throw new Error(`PNG chunk ${type} has a bad CRC`);
  }
  if (!seenIhdr) {
    if (type !== 'IHDR' || length !== 13) {
      throw new Error('entry.png does not start with a valid IHDR chunk');
    }
    const width = image.readUInt32BE(dataStart);
    const height = image.readUInt32BE(dataStart + 4);
    if (width === 0 || height === 0 || width > 1024 || height > 1024) {
      throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 limit`);
    }
    seenIhdr = true;
  }
  if (type === 'IEND') {
    seenIend = true;
    if (dataEnd + 4 !== image.length) {
      throw new Error('entry.png has bytes after the IEND chunk');
    }
    break;
  }
  offset = dataEnd + 4;
}
if (!seenIhdr || !seenIend) {
  throw new Error('entry.png is missing its IHDR or IEND chunk');
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'entry.png'), image);
