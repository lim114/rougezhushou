import unittest
import numpy as np
from rouge.recognition_cache import ExactImageCache


class CachePixelBytesReview(unittest.TestCase):
 def test_strided_negative_transposed_and_gray_views_have_exact_logical_byte_order(self):
  source=np.arange(96,dtype=np.uint8).reshape(4,8,3)
  for image in(source,source[1:,:4],source[::2,::2],source[::-1,1:4],source.transpose(1,0,2),source[:,:,0]):
   expected=bytes(int(image[index])for index in np.ndindex(image.shape));cache=ExactImageCache();first=cache.call(image,'same',lambda:{'value':[1]});key=next(iter(cache.entries));self.assertEqual(key[-1],expected);first['value'].append(2);self.assertEqual(cache.call(image.copy(),'same',lambda:self.fail('Unchanged logical pixels must reuse')) ,{'value':[1]});self.assertEqual((cache.hits,cache.misses),(1,1))
 def test_dtype_byte_order_and_shape_remain_part_of_the_key(self):
  cases=[(np.array([0x1234,0x5678],dtype='<u2'),b'\x34\x12\x78\x56'),(np.array([0x1234,0x5678],dtype='>u2'),b'\x12\x34\x56\x78'),(np.array([[1.,-.5]],dtype='<f4'),b'\0\0\x80\x3f\0\0\0\xbf')];cache=ExactImageCache()
  for index,(image,expected)in enumerate(cases):
   self.assertEqual(cache.call(image,'same',lambda:index),index);key=next(reversed(cache.entries));self.assertEqual(key[-1],expected);self.assertEqual(key[:2],(image.shape,image.dtype.str))
  self.assertEqual((cache.hits,cache.misses),(0,3))
 def test_changed_current_crop_pixels_cannot_reuse_earlier_result(self):
  image=np.arange(60,dtype=np.uint8).reshape(4,5,3);crop=image[1:3,1:4];cache=ExactImageCache();cache.call(crop,'same',lambda:1);image[1,1,0]^=1;self.assertEqual(cache.call(crop,'same',lambda:2),2);self.assertEqual((cache.hits,cache.misses),(0,2))
