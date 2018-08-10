import argparse
import sys
import os
import cv2
from datetime import datetime

import keras
from keras.models import *
from keras.datasets import cifar10
from keras.datasets import mnist
from keras.applications.vgg16 import VGG16
from keras.preprocessing.image import load_img
from keras.layers import *
from keras import *

from utils import *
from nc_lp import *
from lp_encoding import *
from run_nc_linf import run_nc_linf
from run_nc_l0 import run_nc_l0
from run_ssc import run_ssc


def deepconcolic(test_object, outs):
  print('\n== Start DeepConcolic testing ==\n')
  if test_object.criterion=='nc': ## neuron cover
    if test_object.norm=='linf':
      run_nc_linf(test_object, outs)
    elif test_object.norm=='l0':
      run_nc_l0(test_object, outs)
    else:
      print('\n not supported norm...\n')
      sys.exit(0)
  elif test_object.criterion=='ssc': ## neuron cover
    run_ssc(test_object, outs)
  else:
      print('\n for now, let us focus on neuron cover...\n')
      sys.exit(0)


def main():

  parser=argparse.ArgumentParser(description='The concolic testing for neural networks' )
  parser.add_argument(
    '--model', dest='model', default='-1', help='The input neural network model (.h5)')
  parser.add_argument("--inputs", dest="inputs", default="-1",
                    help="the input test data directory", metavar="DIR")
  parser.add_argument("--outputs", dest="outputs", default="-1",
                    help="the outputput test data directory", metavar="DIR")
  parser.add_argument("--criterion", dest="criterion", default="nc",
                    help="the test criterion", metavar="nc, bc, ssc...")
  parser.add_argument("--mnist-dataset", dest="mnist", help="MNIST dataset", action="store_true")
  parser.add_argument("--cifar10-dataset", dest="cifar10", help="CIFAR10 dataset", action="store_true")
  parser.add_argument("--vgg16-model", dest='vgg16', help="vgg16 model", action="store_true")
  parser.add_argument("--norm", dest="norm", default="linf",
                    help="the norm metric", metavar="linf, l0")
  parser.add_argument("--input-rows", dest="img_rows", default="224",
                    help="input rows", metavar="")
  parser.add_argument("--input-cols", dest="img_cols", default="224",
                    help="input cols", metavar="")
  parser.add_argument("--input-channels", dest="img_channels", default="3",
                    help="input channels", metavar="")
  parser.add_argument("--cond-ratio", dest="cond_ratio", default="0.01",
                    help="experimental", metavar="")
  parser.add_argument("--top-classes", dest="top_classes", default="1",
                    help="experimental", metavar="")

  args=parser.parse_args()


  criterion=args.criterion
  norm=args.norm
  cond_ratio=float(args.cond_ratio)
  top_classes=int(args.top_classes)

  raw_data=None
  img_rows, img_cols, img_channels = int(args.img_rows), int(args.img_cols), int(args.img_channels)

  dnn=None
  inp_ub=1
  if args.model!='-1':
    dnn=load_model(args.model)
    dnn.summary()
  elif args.vgg16:
    dnn=VGG16()
    inp_ub=255
    dnn.summary()
  else:
    print (' \n == Please specify the input neural network == \n')
    sys.exit(0)

  if args.inputs!='-1':
    
    xs=[]
    print ('To load input data...')
    for path, subdirs, files in os.walk(args.inputs):
      for name in files:
        fname=(os.path.join(path, name))
        if fname.endswith('.jpg') or fname.endswith('.png'):
          image = cv2.imread(fname)
          image = cv2.resize(image, (img_rows, img_cols))
          image=image.astype('float')
          xs.append((image))
    print ('Total data loaded: ', len(xs))
    x_test=np.asarray(xs)
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, img_channels)
    raw_data=raw_datat(x_test, [])
  elif args.mnist:
    img_rows, img_cols, img_channels = 28, 28, 1
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, img_channels)
    x_test = x_test.astype('float32')
    x_test /= 255
    raw_data=raw_datat(x_test, y_test)
  elif args.cifar10:
    img_rows, img_cols, img_channels = 32, 32, 3
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_test=x_test[0:3000]
    x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, img_channels)
    x_test = x_test.astype('float32')
    x_test /= 255
    raw_data=raw_datat(x_test, y_test)
  else:
    print (' \n == Please input dataset == \n')
    sys.exit(0)

  outs=None
  if args.outputs!='-1':
    outs=args.outputs
  else:
    print (' \n == Please specify the output directory == \n')
    sys.exit(0)

  test_object=test_objectt(dnn, raw_data, criterion, norm)
  test_object.cond_ratio=cond_ratio
  test_object.top_classes=top_classes
  test_object.inp_ub=inp_ub
  deepconcolic(test_object, outs)

if __name__=="__main__":
  main()
