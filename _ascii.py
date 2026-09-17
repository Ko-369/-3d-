from PIL import Image
import numpy as np
img = Image.open(r"D:\陈铭志\新建文件夹\v3\参考1.png").convert("L")
a = np.asarray(img).astype(np.float32)
H,W = a.shape
cols, rows = 90, 36
chars = " .:-=+*#%@"
for r in range(rows):
    y0,y1 = int(r*H/rows), int((r+1)*H/rows)
    line=[]
    for c in range(cols):
        x0,x1 = int(c*W/cols), int((c+1)*W/cols)
        v = a[y0:y1,x0:x1].mean()
        idx = int(np.clip(v/255*len(chars), 0, len(chars)-1))
        line.append(chars[idx])
    print("".join(line))
