#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File  : label.py
# @Author: shadow
# @Date  : 2020/11/17
# @Desc  :  label image

import cv2
from tkinter import *
import threading, os
from enum import Enum
import tkinter.filedialog as filedialog
from tkinter.ttk import Combobox, Treeview
from tkinter.messagebox import showwarning, askyesno



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


class ImageLabel:
    def __init__(self):
        self.type = ['car', 'bus', 'person', 'ashcan']
        self.image_info = {"Run": False, 'name': "", 'labels': [], 'file': "", 'num': 0}

    # 保存标签数据
    def label_save(self, flag):
        if flag:
            with open(self.image_info['file'], 'w+', encoding='utf-8') as df:
                for label in self.image_info['labels'][:-1]:
                    df.write(f'{label[0]} {label[1]} {label[2]} {label[3]} {label[4]}\n')
            tree_image.tag_configure(str(self.image_info['num']), background='green')
        else:
            self.image_info['Run'] = False  # 退出图片的标记，不保存信息
        useStr.set('双击左侧图片名打开图片开始标记')
        self.image_info['labels'].clear()    # 初始化标签值
        listbox_label.delete(0, END)    # 清空listbox
        cv2.destroyAllWindows()

    # 从文件夹获取图片列入图片listbox
    def point_get_from_image(self):
        name = pathStr.get() + '/' + self.image_info['name']
        if not os.path.isfile(name):
            showwarning('警告', f'文件不存在，请核查后再试\n {name}')
            return
        img = cv2.imread(name)
        mouse = [0, 0]
        cv2.namedWindow(self.image_info['name'])
        cv2.setMouseCallback(self.image_info['name'], on_mouse, param=(self.image_info['labels'], mouse, self.type))
        flag = True
        # 打开要校准的基准图片，选取测试基准点
        while self.image_info['Run']:
            img_bak = img.copy()
            # print(mouse)
            for box in self.image_info['labels']:
                if box[1] * box[2]:
                    cv2.circle(img_bak, tuple(box[1:3]), 4, (0, 0, 255), -1)  # 描左上点
                    if box[3] * box[4]:
                        cv2.putText(img_bak, str(self.image_info['labels'].index(box)), (box[1], box[2] - 8),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 200), 2)
                        cv2.rectangle(img_bak, (box[1], box[2]), (box[3], box[4]), (0, 255, 0), 2)  # 画区域框
                        cv2.circle(img_bak, tuple(box[3:]), 4, (0, 0, 255), -1)  # 描右下点
                    else:
                        cv2.rectangle(img_bak, tuple(box[1:3]), tuple(mouse), (0, 255, 0), 1)  # 动态区域显示
            cv2.putText(img_bak, 'Press Q to exit or Save button to save and exit!', (1, 20), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (0, 0, 200), 2)
            cv2.imshow(self.image_info['name'], img_bak)
            # cv2.line(img, (640, 0), (640, 720), (0, 255, 0), 1)
            if cv2.waitKey(1) == ord('q') or not mouse:  # 按Q或鼠标中键退出，不保存数据
                flag = False
                break

        # 线程结束，保存文件
        self.label_save(flag)

    # 选择图片文件夹获取图片
    def load_files(self):
        # 清空treeView
        for _ in map(tree_image.delete, tree_image.get_children("")):
            pass
        file_dir = filedialog.askdirectory(title='标注图片路径', initialdir=os.path.dirname(os.getcwd()), mustexist=True)
        if not file_dir:
            # showwarning("Warning", "请选择图片文件夹")
            return
        wildcard = ".png .jpg"
        files = get_files_from_dir(file_dir, wildcard)
        pathStr.set(file_dir)
        for i in range(len(files)):
            # tree_image.insert('end', file)
            tree_image.insert("", "end", values=[i, files[i], -1], tags=str(i))
            tree_image.tag_configure(str(i), background='#808080')

    # 刷新标签信息
    def label_update(self):
        listbox_label.delete(0, END)
        for i in range(len(self.image_info['labels'])):
            info = self.image_info['labels'][i]
            if info[0] * info[1] and info[2] * info[3]:
                listbox_label.insert(END, f'{i} {info[0]} {info[1]} {info[2]} {info[3]} {info[4]}')

    # 修改标签值
    def label_change(self):
        infos = posStr.get()
        # print(infos)
        if not infos:
            showwarning("提示", "请先双击选择要修改的标签数据")
            return
        infos = infos.split(' ')
        if len(infos) != 6:
            showwarning("提示", "修改数据错误，请确认空格分开\n 格式：序号 类型 四个点位置")
            return
        pos = list(map(int, infos[2:]))
        for i in range(4):
            self.image_info['labels'][int(infos[0])][i + 1] = pos[i]
        self.image_info['labels'][int(infos[0])][0] = infos[1]
        self.label_update()

    # 结束线程，保存数据
    def save(self):
        self.image_info['Run'] = False


# 鼠标事件处理
def on_mouse(event, x, y, flags, param):
    labels, mouse, label_type = param
    pos = labels[-1]
    # print(event, x, y, pos)
    if event == cv2.EVENT_LBUTTONDOWN:  # 第一个点
        pos[1], pos[2] = x, y
    elif event == cv2.EVENT_LBUTTONUP:  # 第二个点
        pos[3], pos[4] = x, y
        pos[0] = label_type[cb_bt.current()]  # 添加类型
        listbox_label.insert('end', f'{len(labels) - 1} {pos[0]} {pos[1]} {pos[2]} {pos[3]} {pos[4]}')
        tree_image.set(tree_image.selection()[0], 2, len(labels))
    elif event == cv2.EVENT_MBUTTONDOWN:  # 退出循环
        mouse.clear()
    elif event == cv2.EVENT_MOUSEMOVE:
        mouse[0], mouse[1] = x, y
        if pos[0] * pos[1] and pos[2] * pos[3]:
            labels.append(['', 0, 0, 0, 0])


# 使用线程打开图片，实时检测鼠标选择标签区域
def load_image(event, label):
    if label.image_info['Run']:
        showwarning('警告', '请先结束上一张图片的标记')
        return
    # 获取点击的值
    num, name, count = tree_image.item(tree_image.selection()[0], "values")
    # 读取已经画好的标签文件
    file = pathStr.get() + '/' + name.rsplit('.', 1)[0] + '.txt'
    # print(file, num, name, count)

    if os.path.isfile(file):
        with open(file, 'r+', encoding='utf-8') as df:
            n = 0
            for line in df.readlines():
                labels = line.split()
                listbox_label.insert('end', str(n) + " " + line)
                label.image_info['labels'].append([labels[0]] + list(map(int, labels[1:])))
                n += 1
    tree_image.set(tree_image.selection()[0], 2, len(label.image_info['labels']))
    # print(image_info['labels'])
    label.image_info['num'] = num    # 图片编号
    # label.image_info['count'] = count  # 标记数量
    label.image_info['name'] = name  # 图片名称
    label.image_info['labels'].append(["", 0, 0, 0, 0])   # 标记具体信息
    label.image_info['file'] = file  # 标记保存文件名
    label.image_info['Run'] = True  # 是否在运行
    useStr.set('双击修改数据, 右键删除标签, 按上面按钮保存')

    threading.Thread(target=label.point_get_from_image, daemon=True).start()


# 获取标签数据写入list方便修改
def label_get(event):
    index = listbox_label.curselection()
    posStr.set(listbox_label.get(index[0]))


# 删除标签值
def label_delete(event, label):
    index = listbox_label.curselection()
    # print(index)
    if not len(index):
        showwarning('提示', '请选选中一个标签才能键删除')
        return

    infos = listbox_label.get(index[0])
    num, info = infos.split(' ', 1)
    if YES == askyesno('删除标签', f'确定是否要删除标签【{num}】: \n{info}'):
        label.image_info['labels'].pop(int(num))
        label.label_update()


# 事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧
def handlerAdaptor(fun, **kwds):
    return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)


if __name__ == '__main__':
    root = Tk()
    root.title("图像标记")
    root.geometry('680x400+10+400')  # 位置设置
    root.wm_resizable(False, False)  # 不允许修改长宽
    posStr = StringVar()    # 位置信息，用于修改标签值
    pathStr = StringVar()   # 图片路径
    useStr = StringVar()    # 使用方法提示

    # label_type = ['car', 'bus', 'person', 'ashcan']
    # image_info = {"Run": False, 'name': "", 'labels': [], 'file': ""}
    label = ImageLabel()

    Label(root, text='标签类型').grid(row=0, column=0, padx=5)
    cb_bt = Combobox(root, width=12)
    cb_bt["values"] = label.type
    cb_bt.current(0)
    cb_bt.grid(row=0, column=1, padx=5)

    Label(root, text='标签信息').grid(row=0, column=2, padx=5)
    Entry(root, textvariable=posStr, width=20, justify="left").grid(row=0, column=3, columnspan=2, sticky='W')
    Button(root, text='修改标签', background='pink', command=label.label_change).grid(row=0, column=5, padx=10)

    Button(root, text='选择图片文件夹', background='pink', command=label.load_files, height=2).grid(row=1, column=1, pady=5)
    Button(root, text='保存标签数据', background='pink', command=label.save, height=2).grid(row=1, column=4, columnspan=2)

    Label(root, textvariable=pathStr, width=36, anchor=W).grid(row=2, column=0, columnspan=3, padx=5, sticky='W')
    Label(root, textvariable=useStr, width=30, anchor=W).grid(row=2, column=4, columnspan=2, pady=5, sticky='W')
    pathStr.set('点击上面选择按钮选择要标记的图片路径')
    useStr.set('双击左侧图片名打开图片开始标记')

    tree = {0: ('序号', 66, CENTER), 1: ('图片名称', 200, W), 2: ('标记数', 66, CENTER)}
    tree_image = Treeview(root, height=10, show="headings", columns=tree.keys())
    for k, v in tree.items():
        tree_image.column(k, width=v[1], anchor=v[2])
        tree_image.heading(k, text=v[0])
    tree_image.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
    scrolly_h = Scrollbar(root, width=20, orient="vertical", command=tree_image.yview)  # 纵向, 绑定listbox
    scrolly_h.grid(row=3, column=3, sticky=NS)
    # scrolly_w = Scrollbar(root, width=20, orient='horizontal', command=tree_image.xview)  # 横向
    # scrolly_w.grid(row=4, column=0, columnspan=3, sticky=EW)
    tree_image['yscrollcommand'] = scrolly_h.set  # 绑定滚动条
    # tree_image['xscrollcommand'] = scrolly_w.set

    listbox_label = Listbox(root, height=10, width=30, selectbackground='red')
    listbox_label.grid(row=3, column=4,  columnspan=2, padx=5)
    scrolly_h1 = Scrollbar(root, width=20, orient="vertical", command=listbox_label.yview)  # 纵向
    scrolly_h1.grid(row=3, column=6, sticky=NS)
    listbox_label['yscrollcommand'] = scrolly_h1.set

    # 有event存在不能直接传参，需传参时要调用中间函数，注意指定参数名, 以下两种方式待参考
    # tree_image.bind('<Double-Button-1>', handlerAdaptor(load_image, label=label))  # 左键双击选择图片
    tree_image.bind('<Double-Button-1>', lambda event: load_image(event, label))
    listbox_label.bind('<Double-Button-1>', label_get)   # 双击获取修改标签值
    listbox_label.bind('<Button-3>', handlerAdaptor(label_delete, label=label))  # 右键删除标签值e

    root.mainloop()
