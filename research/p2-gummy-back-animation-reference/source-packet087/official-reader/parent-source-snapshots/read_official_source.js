'use strict';
// External source research runner only. No application imports or rendering.
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const vm = require('vm');

const root = __dirname;
const orientation = process.argv[2];
const factoryPath = process.argv[3];
const factoryExpectedSHA = process.argv[4];
if (!['Front', 'Back'].includes(orientation) || !factoryPath || !/^[0-9a-f]{64}$/.test(factoryExpectedSHA || '')) {
  throw new Error('Specify actual orientation, frozen reviewed factory path, and SHA-256.');
}
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');
const receipt = {
  version: 1,
  operation: 'Unmodified official Spine 3.8 readSkeletonData source operation',
  orientation,
  started_at: new Date().toISOString(),
  node_version: process.version,
  full_skeleton_parser_calls: 0,
  application_API_helper_formatter_test_Qt_Wine_calls: 0,
  official_commit: '8b4844bd4b193ba9e54487ed397a777993cbad56',
  render_validation: false,
  atlas_or_texture_source_acquisition: false,
  game_binding_or_clock_claims: false,
  reader_source_modified: false,
  bone_or_slot_replacement: false,
  EOF_consumption_claim: false,
  limitations: [
    'Only the unmodified official reader return/error is observed; it exposes no final byte position.',
    'Official default TextureRegion objects have no atlas/image provenance. Visual geometry, UVs and offsets are not validated.',
    'Names, event seconds and animation duration are source data; no normal/skill/skin/native clock binding is inferred.',
    'The historical parser identity and historical total attempt count remain unknown.'
  ]
};
const saveReceipt = () => fs.writeFileSync(path.join(root, `parse-${orientation}-operation.json`), JSON.stringify(receipt, null, 2) + '\n');
let verifiedInput = null;
let verifiedResource = null;
const recordByteInvariance = () => {
  if (!verifiedInput || !verifiedResource) return;
  const inMemorySHA = sha256(verifiedInput);
  const onDiskSHA = sha256(fs.readFileSync(verifiedResource.source_path));
  receipt.after_read_byte_invariance = {input_sha256: inMemorySHA, resource_file_sha256: onDiskSHA, input_unchanged: inMemorySHA === verifiedResource.sha256, resource_file_unchanged: onDiskSHA === verifiedResource.sha256};
  if (!receipt.after_read_byte_invariance.input_unchanged || !receipt.after_read_byte_invariance.resource_file_unchanged) throw new Error('Source resource bytes changed during reading');
};
try {
  const officialRoot = '/workspace/.continuation/p2-gummy-back-parser-source087-official-reader/official-source';
  const bundlePath = path.join(officialRoot, 'spine-ts/build/spine-core.js');
  const bundle = fs.readFileSync(bundlePath);
  const bundleSHA = sha256(bundle);
  if (bundleSHA !== 'f1e0a31b9906e4d4daf2733857d21381ddbbe75adec7f4d83e1cc9b2b070dfc1') throw new Error('Official bundle SHA mismatch');
  const factoryBytes = fs.readFileSync(factoryPath);
  if (sha256(factoryBytes) !== factoryExpectedSHA) throw new Error('Reviewed factory SHA mismatch');
  const acquisition = JSON.parse(fs.readFileSync(path.join(root, 'git-acquisition-receipt.json'), 'utf8'));
  const resource = acquisition.resources.find(item => item.orientation === orientation);
  if (!resource) throw new Error('No verified fixed Git resource entry');
  const raw = fs.readFileSync(resource.source_path);
  const actualBlob = crypto.createHash('sha1').update(Buffer.from(`blob ${raw.length}\0`)).update(raw).digest('hex');
  if (raw.length !== resource.bytes || sha256(raw) !== resource.sha256 || actualBlob !== resource.git_blob_sha1) throw new Error('Resource bytes/SHA/Git blob mismatch');
  receipt.resource = resource;
  receipt.official_bundle = {source_path: bundlePath, bytes: bundle.length, sha256: bundleSHA};
  receipt.reviewed_factory = {source_path: factoryPath, bytes: factoryBytes.length, sha256: factoryExpectedSHA};
  const context = vm.createContext({console});
  vm.runInContext(bundle.toString('utf8'), context, {filename: bundlePath});
  const spine = context.spine;
  if (!spine || typeof spine.SkeletonBinary !== 'function') throw new Error('Official bundle did not expose SkeletonBinary');
  const createLoader = require(factoryPath).createLoader;
  if (typeof createLoader !== 'function') throw new Error('Reviewed factory module must export the factory function');
  const loader = createLoader(spine);
  const reader = new spine.SkeletonBinary(loader);
  // The official BinaryInput uses DataView(data.buffer), without byteOffset.
  // This copy passes the actual file from buffer offset zero, without a Node slab prefix.
  const input = Uint8Array.from(raw);
  if (input.byteOffset !== 0 || input.byteLength !== input.buffer.byteLength) throw new Error('Unexpected input view offset');
  verifiedInput = input;
  verifiedResource = resource;
  receipt.input_copy = {byte_offset: input.byteOffset, byte_length: input.byteLength, backing_buffer_bytes: input.buffer.byteLength, sha256: sha256(input)};
  receipt.full_skeleton_parser_calls = 1;
  saveReceipt();
  const data = reader.readSkeletonData(input);
  recordByteInvariance();
  const animations = data.animations.map(animation => {
    const events = [];
    for (const timeline of animation.timelines) {
      if (timeline instanceof spine.EventTimeline) {
        for (const event of timeline.events) events.push({
          name: event.data.name, seconds: event.time,
          int_value: event.intValue, float_value: event.floatValue, string_value: event.stringValue,
          audio_path: event.data.audioPath, volume: event.volume, balance: event.balance
        });
      }
    }
    return {name: animation.name, duration_seconds: animation.duration, timeline_count: animation.timelines.length, events};
  });
  const result = {
    version: 1, orientation, resource,
    official_bundle_sha256: bundleSHA, reviewed_factory_sha256: factoryExpectedSHA,
    skeleton: {hash: data.hash, spine_version: data.version, fps_nonessential_source: data.fps, x: data.x, y: data.y, width: data.width, height: data.height, images_path: data.imagesPath, audio_path: data.audioPath, bone_count: data.bones.length, slot_count: data.slots.length, skin_count: data.skins.length},
    bones: data.bones.map(bone => ({index: bone.index, name: bone.name, parent_index: bone.parent === null ? null : bone.parent.index})),
    slots: data.slots.map(slot => ({index: slot.index, name: slot.name, bone_index: slot.boneData.index})),
    animations,
    data_scope: 'Source skeleton metadata, real bone/slot identities, animation durations and event payloads only; no rendered attachments or native game clocks.'
  };
  const outputPath = path.join(root, `parse-${orientation}-result.json`);
  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2) + '\n');
  receipt.reader_returned = true;
  receipt.result = {source_path: outputPath, bytes: fs.statSync(outputPath).size, sha256: sha256(fs.readFileSync(outputPath)), animation_count: animations.length, source_event_count: animations.reduce((sum, a) => sum + a.events.length, 0)};
  receipt.finished_at = new Date().toISOString();
  saveReceipt();
  console.log(JSON.stringify({orientation, reader_returned: true, bone_count: data.bones.length, slot_count: data.slots.length, animations: animations.map(a => ({name: a.name, duration_seconds: a.duration_seconds, events: a.events.map(e => ({name: e.name, seconds: e.seconds}))}))}, null, 2));
} catch (error) {
  recordByteInvariance();
  receipt.reader_returned = false;
  receipt.failure_stage = receipt.full_skeleton_parser_calls ? 'official readSkeletonData' : 'source runner preparation';
  receipt.error = {name: error.name, message: error.message, stack: error.stack};
  receipt.finished_at = new Date().toISOString();
  saveReceipt();
  console.error(error.stack);
  process.exitCode = 1;
}
