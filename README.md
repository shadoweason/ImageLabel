# ImageLabel
深度学习标记小工具，使用python tkinter+cv2实现
python 3.7
opencv-python 4.1.1

tkinter界面比较粗糙，优化可以使用pyQt去做
输出的文件时txt，格式是 （类型 left top right bottom）不喜可使用josn或xml格式化

使用：
  图片treeview部分
    1. 双击图片名打开图片，图片上点击拖动框选目标，放开记录数据
    2. 打开图片更新标记数量，保存数据背景颜色变粉红，不保存不变色
    3. 在图片界面按Q或鼠标中间不保存退出，按保存按钮保存退出
  标记数据listbox部分
    1. 双击标记数据将数据导入到修改输入框，修改后按按钮保存更新标记框的位置和显示数据
    2. 右键删除数据
