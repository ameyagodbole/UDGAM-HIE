import tensorflow as tf
import os
import io

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util

import pandas as pd
import PIL.Image
from sklearn.model_selection import train_test_split

# flags = tf.app.flags
# flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
# FLAGS = flags.FLAGS


def create_tf_example(example):
	# TODO(user): Populate the following variables from your example.
	filename = os.path.join('./spotgarbage-GINI/spotgarbage/garbage-queried-images/', example['query'], example['image'])
	image_format = b'jpeg'
	image = PIL.Image.open(filename)

	# x1, x2 = example['startX'], example['endX']
	# y1, y2 = example['startY'], example['endY']

	# midx = (x2+x1)/2
	# midx = (y2+y1)/2
	# gapx = min(image.size[0]-midx, midx)
	# gapy = min(image.size[1]-midy, midy)

	# im2 = image.resize((227,227))
	# im2.convert('RGB').save('./tmp.jpg', 'JPEG')
	with tf.gfile.GFile(filename, 'rb') as fid:
		encoded_jpg = fid.read()
	# os.remove('./tmp.jpg')

	height = image.size[0] # Image height
	width = image.size[1] # Image width

	# encoded_image_data = io.BytesIO(encoded_jpg)

	xmins = [float(example['startX'])/image.size[0]] # List of normalized left x coordinates in bounding box (1 per box)
	xmaxs = [float(example['endX'])/image.size[0]] # List of normalized right x coordinates in bounding box
						 # (1 per box)
	ymins = [float(example['startY'])/image.size[1]] # List of normalized top y coordinates in bounding box (1 per box)
	ymaxs = [float(example['endY'])/image.size[1]] # List of normalized bottom y coordinates in bounding box
						 # (1 per box)
	classes_text = ['trash']
	classes = [1]
	# 'image/encoded': dataset_util.bytes_feature(encoded_image_data),
	tf_example = tf.train.Example(features=tf.train.Features(feature={
			'image/height': dataset_util.int64_feature(height),
			'image/width': dataset_util.int64_feature(width),
			'image/filename': dataset_util.bytes_feature(filename),
			'image/source_id': dataset_util.bytes_feature(filename),
			'image/encoded': dataset_util.bytes_feature(encoded_jpg),
			'image/format': dataset_util.bytes_feature(image_format),
			'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
			'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
			'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
			'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
			'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
			'image/object/class/label': dataset_util.int64_list_feature(classes),
	}))
	return tf_example


def main(_):
	# TODO(user): Write code to read in your dataset to examples variable
	df = pd.read_csv('spotgarbage-GINI/spotgarbage/garbage-queried-images.csv')
	all_examples = df.loc[df['label']==1]
	count = 0

	train, test = train_test_split(all_examples, test_size = 0.2)
	
	# writer = tf.python_io.TFRecordWriter(FLAGS.output_path+'trash_train.record')
	writer = tf.python_io.TFRecordWriter('trash_train.record')
	print 'train'
	for idx, example in train.iterrows():
		if count%50==0:
			print count
		count += 1
		tf_example = create_tf_example(example)
		writer.write(tf_example.SerializeToString())
	print '----'
	print 'train len:',count
	writer.close()

	count = 0
	# writer = tf.python_io.TFRecordWriter(FLAGS.output_path+'trash_test.record')
	writer = tf.python_io.TFRecordWriter('trash_test.record')
	print 'test'
	for idx, example in test.iterrows():
		if count%50==0:
			print count
		count += 1
		tf_example = create_tf_example(example)
		writer.write(tf_example.SerializeToString())
	print '----'
	print 'test len:',count
	writer.close()


if __name__ == '__main__':
	tf.app.run()
