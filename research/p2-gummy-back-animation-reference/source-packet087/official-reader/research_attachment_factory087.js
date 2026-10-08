'use strict';

// Research metadata decoding only. Every attachment is an official runtime
// object, and SkeletonBinary fills its real payload. Region objects retain
// the official zero defaults. No atlas, image, geometry, or render validity
// is asserted; UVs/region offsets are outside the extracted event metadata.
function createLoader(spine) {
  return {
    newRegionAttachment(skin, name, path) {
      const attachment = new spine.RegionAttachment(name);
      attachment.setRegion(new spine.TextureRegion());
      return attachment;
    },
    newMeshAttachment(skin, name, path) {
      const attachment = new spine.MeshAttachment(name);
      attachment.region = new spine.TextureRegion();
      return attachment;
    },
    newBoundingBoxAttachment(skin, name) {
      return new spine.BoundingBoxAttachment(name);
    },
    newPathAttachment(skin, name) {
      return new spine.PathAttachment(name);
    },
    newPointAttachment(skin, name) {
      return new spine.PointAttachment(name);
    },
    newClippingAttachment(skin, name) {
      return new spine.ClippingAttachment(name);
    }
  };
}

exports.createLoader = createLoader;
