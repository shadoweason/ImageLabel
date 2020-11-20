#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import cv2
from tkinter import *
from tkinter.ttk import Treeview
import tkinter.filedialog as filedialog
from tkinter.messagebox import showwarning, askyesno
from threading import Thread
from enum import Enum


def get_files_from_dir(dir, wildcard):
    file_names = []
    exts = wildcard.split(" ")
    files = os.listdir(dir)
    for name in files:
        fullname = os.path.join(dir, name)
        if(os.path.isdir(fullname)):
            # 遍历子路径，如果需要请修改pathStr获取方式，否者子路径的图片打开会有问题
            # file_names += get_files_from_dir(fullname, wildcard)
            pass
        else:
            for ext in exts:
                if(name.endswith(ext)):
                    file_names.append(name)
                    break
    return file_names

class LabelImage:
    def __init__(self, path, file):
        super().__init__()
        self.label_name = ['person', 'car', 'bus', 'truck', 'big_truck', 'tricycle']
        self.Status = Enum('Status', ('LEFT', 'RIGHT', 'DOWN', 'UP', 'MOVE'))
        self.mouse = self.Status.UP
        self.setSelect(False)
        self.create = False
        self.image_path = os.path.join(path, file)
        self.label_path = self.image_path.rsplit('.', 1)[0] + '.txt'
        self.saveStatus = False
        self.labels = []    # 标签存储列表
        self.labelLoad()

    def labelLoad(self):
        # 加载已存在的标签数据
        if os.path.isfile(self.label_path):
            with open(self.label_path, 'r') as f:
                for obj in f.readlines():
                    obj = obj.split('\n')[0].split(' ')
                    left = int(obj[1])
                    top = int(obj[2])
                    right = int(obj[3])
                    bottom = int(obj[4])
                    self.labels.append([obj[0], [left, top], [right, bottom]])

    def isSelect(self):
        return self.select[0]

    def setSelect(self, status, index=-1, num=-1):
        self.select = [status, index, num]

    def getSelect(self):
        return self.select[0], self.select[1], self.select[2]

    def save(self):
        print('save')
        with open(self.label_path, 'w+') as f:
            for label in self.labels:
                f.write('{:s} {:d} {:d} {:d} {:d}\n'.format(label[0], label[1][0], label[1][1], label[2][0], label[2][1]))
        self.saveStatus = True

    def delete(self):
        if self.isSelect():
            _, index, _ = self.getSelect()
            del self.labels[index]
            self.setSelect(False)

    # 改变标签框线位置大小
    def move(self, status):
        if self.isSelect():
            _, index, num = self.getSelect()
            if status == self.Status.LEFT:
                self.labels[index][num][0] -= 1
            elif status == self.Status.RIGHT:
                self.labels[index][num][0] += 1
            elif status == self.Status.UP:
                self.labels[index][num][1] -= 1
            elif status == self.Status.DOWN:
                self.labels[index][num][1] += 1

    # 显示图像，监控鼠标和键盘
    def show(self, name):
        cv2.namedWindow(name)
        cv2.setMouseCallback(name, self._on_mouse)
        while True:
            image = cv2.imread(self.image_path)
            for i in range(len(self.labels)):
                info, pos1, pos2 = self.labels[i]
                info = f'{i} {info}'
                cv2.rectangle(image, tuple(pos1), tuple(pos2), (0, 255, 0), 2)
                cv2.putText(image, info, tuple((pos1[0], pos1[1]-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            if self.isSelect():
                _, index, num = self.getSelect()
                cv2.circle(image, tuple(self.labels[index][num]), 6, (0, 255, 0), 1)
            elif self.create:
                cv2.rectangle(image, self.p1, self.p2, (0, 255, 0), 1)
            cv2.imshow(name, image)
            key = cv2.waitKey(1)
            if key == 27:
                break
            elif key == ord('q'):
                if self.isSelect():
                    self.setSelect(False)
                else:
                    self.save()

            elif key == ord('a'):  # left
                self.move(self.Status.LEFT)
            elif key == ord('w'):  # up
                self.move(self.Status.UP)
            elif key == ord('d'):  # right
                self.move(self.Status.RIGHT)
            elif key == ord('s'):  # down
                self.move(self.Status.DOWN)
            elif key == ord('z'):  # save
                self.save()
            elif key == 255:  # del
                self.delete()
            elif key >= 0:
                print(key)

        cv2.destroyWindow(name)

    def _on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 第一个点
            self.mouse = self.Status.DOWN
            self.p1 = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:  # 第二个点
            self.p2 = (x, y)
            if self.mouse == self.Status.DOWN:
                for i, label in enumerate(self.labels):
                    if abs(self.p1[0] - label[1][0]) < 10 and abs(self.p1[1] - label[1][1]) < 10:
                        self.setSelect(True, i, 1)
                    elif abs(self.p1[0] - label[2][0]) < 10 and abs(self.p1[1] - label[2][1]) < 10:
                        self.setSelect(True, i, 2)
            elif self.mouse == self.Status.MOVE:
                if self.isSelect():
                    self.p1 = None
                    self.p2 = None
                elif abs(self.p1[0] - self.p2[0]) > 10 and abs(self.p1[1] - self.p2[1]) > 10:
                    self.labels.append([self.label_name[0], list(self.p1), list(self.p2)])  # 转list，移动坐标需要修改单独数据
                    self.create = False
            self.mouse = self.Status.UP
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mouse == self.Status.DOWN or self.mouse == self.Status.MOVE:
                self.p2 = (x, y)
                if abs(self.p1[0] - self.p2[0]) > 10 and abs(self.p1[1] - self.p2[1]) > 10:
                    self.mouse = self.Status.MOVE
                    self.create = True


class LabelTool:
    def __init__(self):
        self.wildcard = ".png .jpg"
        page = Tk()
        page.title('标记小工具')
        self.pathStr = StringVar()

        Button(page, text='打开文件夹', background='pink', command=self.open_path, height=2).grid(pady=5)
        Label(page, textvariable=self.pathStr, anchor=W).grid(row=0, column=1, columnspan=5, padx=5, sticky='W')
        self.pathStr.set('点击按钮选择要标记的图片路径')

        tree_title = {0: ('序号', 60, CENTER), 1: ('图片名称', 200, W), 2: ('标记数', 60, CENTER)}
        self.tree_image = Treeview(page, height=10, show="headings", columns=tree_title.keys())
        for k, v in tree_title.items():
            self.tree_image.column(k, width=v[1], anchor=v[2])
            self.tree_image.heading(k, text=v[0])
        self.tree_image.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
        scrolly_image = Scrollbar(page, width=20, orient="vertical", command=self.tree_image.yview)  # 纵向绑定
        scrolly_image.grid(row=3, column=3, sticky=NS)
        self.tree_image['yscrollcommand'] = scrolly_image.set  # 绑定滚动条

        self.tree_image.bind('<Double-Button-1>', self.load_image)
        # self.listbox_label.bind('<Double-Button-1>', self.label_all)  # 双击选中所有

        page.mainloop()

    def updata_path(self):
        files = get_files_from_dir(self.pathStr.get(), self.wildcard)
        for i in range(len(files)):
            self.tree_image.insert("", "end", values=[i, files[i], -1], tags=str(i))
            self.tree_image.tag_configure(str(i), background='gray')

    # 选择图片文件夹获取图片
    def open_path(self):
        path = filedialog.askdirectory(title='标注图片路径', initialdir=os.path.dirname(os.getcwd()), mustexist=True)
        if not path:
            # showwarning("Warning", "请选择图片文件夹")
            return
        self.pathStr.set(path)
        self.updata_path()

    def load_image(self, event):
        print('_load_image ', event, )
        # 获取点击的值
        num, name, count = self.tree_image.item(self.tree_image.selection()[0], "values")
        image_path = os.path.join(self.pathStr.get(), name)
        # assert os.path.isfile(image_path)
        if not os.path.isfile(image_path):
            showwarning('警告', f'错误的图片路径，请确认选择的文件夹\n{image_path}')

        Thread(target=self._show, args=(self.pathStr.get(), name, self.tree_image, num)).start()
        print('end ', os.getpid())

    def del_image(self, event):
        print('_del_image ', event)
        name = self.file_box.get(self.file_box.curselection()[0]).split(' ')[0]
        image_path = os.path.join(self.path, name + '.jpg')
        label_path = os.path.join(self.path, name + '.txt')
        if os.path.isfile(image_path):
            os.remove(image_path)
        if os.path.isfile(label_path):
            os.remove(label_path)
        self.file_box.delete(self.file_box.curselection()[0])

    def del_label(self, event):
        pass

    @staticmethod
    def _show(path, file, tree_image, num):
        print('_show ', file, ' ', os.getpid())
        image = LabelImage(path, file)
        tree_image.tag_configure(str(num), background='yellow')
        image.show(file)
        if image.saveStatus:
            print('change')
            tree_image.set(tree_image.get_children()[num], 2, len(image.labels))
            tree_image.tag_configure(str(num), background='green')
        else:
            tree_image.tag_configure(str(num), background='gray')


if __name__ == '__main__':
    label = LabelTool()
