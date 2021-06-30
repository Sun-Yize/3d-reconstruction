from flask import send_file, Flask, request
import cv2
import torch

import shutil
from subprocess import call
from PIL import Image
from models import load_model
from lib.config import cfg, cfg_from_list
from lib.solver import Solver
from lib.voxel import voxel2obj
import os
import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import imageio
from matplotlib.backends.backend_agg import FigureCanvasAgg
import sys
matplotlib.use('Agg')
app = Flask(__name__)

def cmd_exists(cmd):
    return shutil.which(cmd) is not None


def load_demo_images(path):
    ims = []
    for i in range(1):
        im = Image.open(path).convert("RGB").resize((127, 127))
        print(np.shape(im))
        ims.append([np.array(im).transpose(
            (2, 0, 1)).astype(np.float32) / 255.])
        print(np.shape(ims))
    return np.array(ims)


class ObjFile:
    def __init__(self, obj_file=None):
        self.nodes = None
        self.faces = None
        if obj_file:
            self.ObjParse(obj_file)

    def ObjInfo(self):
        print("Num vertices  :    %d" % (len(self.nodes)))
        print("Num faces     :    %d" % (len(self.faces)))
        nmin, nmax = self.MinMaxNodes()
        print("Min/Max       :    %s %s" % (np.around(nmin, 3), np.around(nmax, 3)))

    @staticmethod
    def MinMax3d(arr):
        nmin = 1E9 * np.ones((3))
        nmax = -1E9 * np.ones((3))
        for a in arr:
            for i in range(3):
                nmin[i] = min(nmin[i], a[i])
                nmax[i] = max(nmax[i], a[i])
        return (nmin, nmax)

    def MinMaxNodes(self):
        return ObjFile.MinMax3d(self.nodes)

    def ObjParse(self, obj_file):
        f = open(obj_file)
        lines = f.readlines()
        f.close()
        nodes = []
        # add zero entry to get ids right
        nodes.append([.0, .0, .0])
        faces = []
        for line in lines:
            if 'v' == line[0] and line[1].isspace():  # do not match "vt" or "vn"
                v = line.split()
                nodes.append(ObjFile.ToFloats(v[1:])[:3])
            if 'f' == line[0]:
                # remove /int
                line = re.sub(RE, '', line)
                f = line.split()
                faces.append(ObjFile.ToInts(f[1:]))

        self.nodes = np.array(nodes)
        assert (np.shape(self.nodes)[1] == 3)
        self.faces = faces

    def ObjWrite(self, obj_file):
        f = open(obj_file, 'w')
        for n in self.nodes[1:]:  # skip first dummy 'node'
            f.write('v ')
            for nn in n:
                f.write('%g ' % (nn))
            f.write('\n')
        for ff in self.faces:
            f.write('f ')
            for fff in ff:
                f.write('%d ' % (fff))
            f.write('\n')

    @staticmethod
    def ToFloats(n):
        if isinstance(n, list):
            v = []
            for nn in n:
                v.append(float(nn))
            return v
        else:
            return float(n)

    @staticmethod
    def ToInts(n):
        if isinstance(n, list):
            v = []
            for nn in n:
                v.append(int(nn))
            return v
        else:
            return int(n)

    @staticmethod
    def Normalize(v):
        v2 = np.linalg.norm(v)
        if v2 < 0.000000001:
            return v
        else:
            return v / v2

    def QuadToTria(self):
        trifaces = []
        for f in self.faces:
            if len(f) == 3:
                trifaces.append(f)
            elif len(f) == 4:
                f1 = [f[0], f[1], f[2]]
                f2 = [f[0], f[2], f[3]]
                trifaces.append(f1)
                trifaces.append(f2)
        return trifaces

    @staticmethod
    def ScaleVal(v, scale, minval=True):

        if minval:
            if v > 0:
                return v * (1. - scale)
            else:
                return v * scale
        else:  # maxval
            if v > 0:
                return v * scale
            else:
                return v * (1. - scale)

    def Plot(self):
        plt.ioff()
        tri = self.QuadToTria()
        fig = plt.figure(dpi=50)
        ax = fig.gca(projection='3d')
        ax.plot_trisurf(self.nodes[:, 0], self.nodes[:, 1], self.nodes[:, 2], triangles=tri)
        ax.axis('off')
        fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
        gif_images = []
        canvas = FigureCanvasAgg(plt.gcf())

        for elevation in np.linspace(-180, 180, 20):
            print(elevation)
            ax.view_init(0, elevation)
            canvas.draw()
            img = np.array(canvas.renderer.buffer_rgba())
            gif_images.append(img)
        imageio.mimsave("test.gif", gif_images, fps=8)


@app.route("/", methods=['POST'])
def receiveImg():
    image = request.files['file']
    image.save('test_img.png')
    return "success"


@app.route("/monocular", methods=['GET'])
def monocular():
    img = cv2.imread('test_img.png')
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    print(img.shape)
    input_batch = transform(img).to(device)
    with torch.no_grad():
            prediction = midas(input_batch)

            prediction = torch.nn.functional.interpolate(
                    prediction.unsqueeze(1),
                    size=img.shape[:2],
                    mode="bicubic",
                    align_corners=False,
            ).squeeze()
    output = prediction.cpu().numpy()
    matplotlib.image.imsave('result.png', output, cmap='gray')
    return "success"

cfg_from_list(['CONST.BATCH_SIZE', 1])
NetClass = load_model('ResidualGRUNet')
net = NetClass(compute_grad=False)  # instantiate a network
net.load('output/ResidualGRUNet/default_model/weights.npy')
solver = Solver(net)  # instantiate a solver
demo_imgs = load_demo_images('test_img.png')
voxel_prediction, _ = solver.test_output(demo_imgs)
voxel2obj('prediction.obj', voxel_prediction[0, :, 1, :, :] > cfg.TEST.VOXEL_THRESH)
print('success saving')
ob = ObjFile('prediction_1.obj')
ob.Plot()

@app.route("/obj_model", methods=['GET'])
def obj_model():
    demo_imgs = load_demo_images('test_img.png')
    voxel_prediction, _ = solver.test_output(demo_imgs)
    voxel2obj('prediction.obj', voxel_prediction[0, :, 1, :, :] > cfg.TEST.VOXEL_THRESH)
    print('success saving')
    ob = ObjFile('prediction_1.obj')
    ob.Plot()
    return "success"


if __name__ == '__main__':
    context = (sys.path[0] + '/Nginx/1_www.inifyy.cn_bundle.crt', sys.path[0] + '/Nginx/2_www.inifyy.cn.key')
    app.run(debug=1, host='172.17.0.3', port=8083, ssl_context=context)
