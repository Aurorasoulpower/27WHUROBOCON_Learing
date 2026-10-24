# AprilTag 定位数学推导

> 对照阅读：
> [AprilTag 定位原理](视觉基础_02_AprilTag定位原理.md) ·
> [针孔相机成像原理](视觉基础_01_针孔相机成像原理.md) ·
> [相机标定原理与操作](视觉基础_04_相机标定原理与操作.md)
>
> 本文不假设某一种 AprilTag 库的固定内部实现，而是推导从平面标签角点到相机位姿、
> 再到机器人交接坐标的标准数学过程。OpenCV 的 `estimatePoseSingleMarkers()` 可能使用
> 平面 PnP 或迭代求解器，但输入、几何约束和最终位姿含义与本文一致。

## 1. 推导目标

已知：

- AprilTag 是边长为 $L$ 的正方形；
- 检测器给出四个图像角点 $m_i=(u_i,v_i)$；
- 相机内参 $K$ 和畸变参数 $D$ 已知；
- 相机相对机器人以及标签相对 TR 的安装关系已知或可标定。

要求：

1. 求标签相对相机的旋转矩阵 $R_{ca}$；
2. 求标签相对相机的平移向量 $t_{ca}$；
3. 把结果表示为 OpenCV 的 `rvec/tvec`；
4. 换算到机器人底盘和交接机构坐标；
5. 定义可检查的重投影误差和有效姿态。

## 2. 坐标和符号

| 符号 | 含义 |
| --- | --- |
| $A$ | AprilTag 标签坐标 |
| $C$ | 相机坐标 |
| $B$ | BR 底盘坐标 |
| $TR$ | TR 底盘坐标 |
| $H$ | TR 交接机构坐标 |
| $p_a$ | 标签坐标中的三维点 |
| $p_c$ | 相机坐标中的三维点 |
| $m_i$ | 第 $i$ 个角点的像素坐标 |
| $L$ | 标签实际边长 |
| $K$ | 相机内参 |
| $D$ | 畸变参数 |
| $R_{ca}$ | 标签坐标到相机坐标的旋转 |
| $t_{ca}$ | 标签原点在相机坐标中的位置 |

齐次变换记为：

$$
T_{ca}
=
\begin{bmatrix}
R_{ca}&t_{ca}\\
0&1
\end{bmatrix}
$$

它满足：

$$
\begin{bmatrix}p_c\\1\end{bmatrix}
=
T_{ca}
\begin{bmatrix}p_a\\1\end{bmatrix}
$$

这里 $T_{ca}$ 的方向是“标签到相机”，避免只写 $T$ 导致方向混淆。

## 3. 标签角点的三维模型

把标签中心设为原点，标签平面设为 $Z=0$，标签坐标轴与检测器模型一致。

OpenCV ArUco 单标签位姿使用四个方形角点，常见内部顺序为：

```text
0: 左上
1: 右上
2: 右下
3: 左下
```

按“左/上为正”的内部模型，四个点可以写成：

$$
P_0=\left(-\frac L2,\frac L2,0\right)
$$

$$
P_1=\left(\frac L2,\frac L2,0\right)
$$

$$
P_2=\left(\frac L2,-\frac L2,0\right)
$$

$$
P_3=\left(-\frac L2,-\frac L2,0\right)
$$

注意：

- $L$ 必须和检测器使用的标记模型尺寸一致；
- 四个点必须保持固定顺序；
- 角点顺序一旦与图像角点对应错误，PnP 会得到错误甚至镜像的位姿。

实际工程最重要的是使用与 `estimatePoseSingleMarkers()` 相同定义的对象点。若不使用该
封装而直接调用 `solvePnP()`，应显式构造并使用相同的角点模型。

## 4. 相机投影模型

对任意标签点 $P_i$：

$$
P_{c,i}=R_{ca}P_i+t_{ca}
$$

写成分量：

$$
P_{c,i}=
\begin{bmatrix}X_i\\Y_i\\Z_i\end{bmatrix}
$$

理想归一化坐标为：

$$
x_i=\frac{X_i}{Z_i},
\qquad
y_i=\frac{Y_i}{Z_i}
$$

这里要求 $Z_i>0$，即点在相机前方。

设：

$$
r_i^2=x_i^2+y_i^2
$$

OpenCV 五参数畸变模型为：

$$
x_{d,i}
=
x_i(1+k_1r_i^2+k_2r_i^4+k_3r_i^6)
+2p_1x_iy_i+p_2(r_i^2+2x_i^2)
$$

$$
y_{d,i}
=
y_i(1+k_1r_i^2+k_2r_i^4+k_3r_i^6)
+p_1(r_i^2+2y_i^2)+2p_2x_iy_i
$$

最终像素投影为：

$$
\hat m_i=
\begin{bmatrix}
f_x x_{d,i}+c_x\\
f_y y_{d,i}+c_y
\end{bmatrix}
$$

把它简写为投影函数：

$$
\hat m_i=\pi(K,D,R_{ca},t_{ca},P_i)
$$

## 5. 位姿估计问题

检测到的实际角点为：

$$
m_i=
\begin{bmatrix}u_i\\v_i\end{bmatrix},
\qquad i=0,1,2,3
$$

PnP 的目标是求 $R_{ca},t_{ca}$，使重投影点尽量接近检测点：

$$
\min_{R_{ca},t_{ca}}
\sum_{i=0}^{3}
\left\|
m_i-\pi(K,D,R_{ca},t_{ca},P_i)
\right\|^2
$$

因为四个点都位于同一个平面，直接线性求解可以借助平面单应矩阵。

## 6. 平面单应矩阵

标签平面满足 $Z_a=0$，因此：

$$
\begin{bmatrix}X_i\\Y_i\\Z_i\end{bmatrix}
=
R_{ca}
\begin{bmatrix}X_i\\Y_i\\0\end{bmatrix}
+t_{ca}
$$

把旋转矩阵按列拆分：

$$
R_{ca}=[r_1\ r_2\ r_3]
$$

则：

$$
P_{c,i}=
r_1X_i+r_2Y_i+t_{ca}
$$

在理想针孔模型下：

$$
s_i
\begin{bmatrix}u_i\\v_i\\1\end{bmatrix}
=
K
\begin{bmatrix}
X_i\\Y_i\\1
\end{bmatrix}
$$

定义：

$$
H=K[r_1\ r_2\ t_{ca}]
$$

于是：

$$
\begin{bmatrix}u_i\\v_i\\1\end{bmatrix}
\sim
H
\begin{bmatrix}X_i\\Y_i\\1\end{bmatrix}
$$

$H$ 描述标签平面到图像平面的二维射影映射，只确定到一个尺度。

## 7. 用 DLT 求解单应矩阵

把 $H$ 写成分量：

$$
H=
\begin{bmatrix}
h_{11}&h_{12}&h_{13}\\
h_{21}&h_{22}&h_{23}\\
h_{31}&h_{32}&h_{33}
\end{bmatrix}
$$

令：

$$
\begin{bmatrix}u'\\v'\\w'\end{bmatrix}
=
H
\begin{bmatrix}X\\Y\\1\end{bmatrix}
$$

实际像素坐标为：

$$
u=\frac{u'}{w'},
\qquad
v=\frac{v'}{w'}
$$

展开后得到：

$$
\frac{h_{11}X+h_{12}Y+h_{13}}
{h_{31}X+h_{32}Y+h_{33}}=u
$$

$$
\frac{h_{21}X+h_{22}Y+h_{23}}
{h_{31}X+h_{32}Y+h_{33}}=v
$$

交叉相乘并整理：

$$
Xh_{11}+Yh_{12}+h_{13}
-uXh_{31}-uYh_{32}-uh_{33}=0
$$

$$
Xh_{21}+Yh_{22}+h_{23}
-vXh_{31}-vYh_{32}-vh_{33}=0
$$

令：

$$
h=
[h_{11},h_{12},h_{13},
h_{21},h_{22},h_{23},
h_{31},h_{32},h_{33}]^T
$$

每对二维对应点产生两行约束：

$$
\begin{bmatrix}
X&Y&1&0&0&0&-uX&-uY&-u\\
0&0&0&X&Y&1&-vX&-vY&-v
\end{bmatrix}
h=0
$$

把四个点叠加得到 $8\times9$ 矩阵 $M$：

$$
Mh=0
$$

对 $M$ 做 SVD：

$$
M=U\Sigma V^T
$$

最小奇异值对应的右奇异向量就是 $h$ 的解。把它重新排列为 $3\times3$ 的 $H$，
并归一化，例如令 $h_{33}=1$，或令 $\|H\|_F=1$。

四个对应点正好提供 8 个独立方程，理论上足以求解 $H$ 的 8 个自由度。检测角点有误差时，
通常通过 SVD 最小二乘得到近似解。

## 8. 从 $H$ 分解旋转和平移

已知：

$$
H=\lambda K[r_1\ r_2\ t_{ca}]
$$

记 $H$ 的三列为 $h_1,h_2,h_3$：

$$
h_1=\lambda Kr_1
$$

$$
h_2=\lambda Kr_2
$$

$$
h_3=\lambda Kt_{ca}
$$

先计算：

$$
\tilde r_1=K^{-1}h_1
$$

$$
\tilde r_2=K^{-1}h_2
$$

由于旋转矩阵列向量长度为 1，尺度因子可以近似取：

$$
\lambda
\approx
\frac{2}
{\|\tilde r_1\|+\|\tilde r_2\|}
$$

然后：

$$
r_1=\frac{\tilde r_1}{\|\tilde r_1\|}
$$

$$
r_2=\frac{\tilde r_2}{\|\tilde r_2\|}
$$

第三列由叉乘得到：

$$
r_3=r_1\times r_2
$$

平移为：

$$
t_{ca}=\frac{1}{\lambda}K^{-1}h_3
$$

旋转矩阵为：

$$
R_{ca}=[r_1\ r_2\ r_3]
$$

### 8.1 尺度符号

$H$ 的符号整体翻转不影响图像映射，因此分解后可能得到符号相反的一组解。
应通过以下条件选解：

- 所有标签角点的 $Z_c>0$；
- 重投影误差更小；
- 角点方向与标签模型一致；
- 相邻帧姿态连续。

## 9. 把矩阵投影回旋转群

有噪声时，直接组成的 $[r_1,r_2,r_3]$ 未必严格满足：

$$
R^TR=I,
\qquad
\det(R)=1
$$

可以先对近似矩阵 $R_0$ 做 SVD：

$$
R_0=U\Sigma V^T
$$

再得到最近的旋转矩阵：

$$
R=U
\begin{bmatrix}
1&0&0\\
0&1&0\\
0&0&\det(UV^T)
\end{bmatrix}
V^T
$$

这保证结果落在合法旋转群上，并消除反射矩阵。

## 10. 非线性优化

单应分解提供较好的初值，但没有完整考虑畸变和角点噪声。实际系统通常继续做非线性优化。

定义第 $i$ 个角点的残差：

$$
e_i=
m_i-
\pi(K,D,R_{ca},t_{ca},P_i)
$$

把四个角点的残差堆成向量：

$$
e=
\begin{bmatrix}
e_0\\e_1\\e_2\\e_3
\end{bmatrix}
$$

优化目标为：

$$
\min_{R_{ca},t_{ca}}
e^Te
$$

把旋转增量表示为李代数小量 $\delta\omega$，平移增量为 $\delta t$，
在初值附近线性化：

$$
e(\xi+\delta\xi)
\approx
e(\xi)+J\delta\xi
$$

其中：

$$
\xi=[\omega,t]^T,
\qquad
\delta\xi=[\delta\omega,\delta t]^T
$$

Gauss-Newton 更新为：

$$
\delta\xi
=
-\left(J^TJ\right)^{-1}J^Te
$$

Levenberg-Marquardt 为了避免不稳定，使用：

$$
\delta\xi
=
-\left(J^TJ+\mu I\right)^{-1}J^Te
$$

旋转更新使用指数映射：

$$
R\leftarrow R\exp([\delta\omega]_\times)
$$

$$
t\leftarrow t+\delta t
$$

迭代直到残差或增量足够小。

## 11. 罗德里格斯向量与旋转矩阵

OpenCV 的 PnP 通常输出旋转向量 `rvec`，而不是直接的旋转矩阵。

设：

$$
\omega=
\begin{bmatrix}
\omega_x\\\omega_y\\\omega_z
\end{bmatrix},
\qquad
\theta=\|\omega\|
$$

其反对称矩阵为：

$$
[\omega]_\times=
\begin{bmatrix}
0&-\omega_z&\omega_y\\
\omega_z&0&-\omega_x\\
-\omega_y&\omega_x&0
\end{bmatrix}
$$

罗德里格斯公式为：

$$
R=
I+
\frac{\sin\theta}{\theta}[\omega]_\times
+
\frac{1-\cos\theta}{\theta^2}[\omega]_\times^2
$$

当 $\theta$ 接近 0 时，使用极限形式：

$$
\frac{\sin\theta}{\theta}\rightarrow1,
\qquad
\frac{1-\cos\theta}{\theta^2}\rightarrow\frac12
$$

因此：

$$
R\approx I+[\omega]_\times
$$

OpenCV 中：

```cpp
cv::Rodrigues(rvec, R);
```

完成 $rvec\rightarrow R$。

## 12. 平面位姿的歧义

四点平面 PnP 在数学上可能出现两个位姿解，它们在二维投影上都很接近，但三维姿态不同。
常见原因包括：

- 标签很小、像素太少；
- 视角很斜；
- 角点误差大；
- 镜头畸变未准确建模；
- 标签接近正面但旋转信息不足。

这称为平面位姿歧义或“翻转”现象。

可选解需要比较：

1. 重投影误差；
2. 所有点在相机前方；
3. 标签法向是否符合安装约束；
4. 与上一帧的姿态连续性；
5. 多帧统计结果。

单帧重投影误差小并不一定能排除错误镜像解，因此运动和安装先验很重要。

## 13. 重投影误差

得到位姿后，把标签模型角点重新投影：

$$
\hat m_i=
\pi(K,D,R_{ca},t_{ca},P_i)
$$

定义均方根重投影误差：

$$
e_{rms}
=
\sqrt{
\frac{1}{4}
\sum_{i=0}^{3}
\left\|
m_i-\hat m_i
\right\|^2
}
$$

有些实现使用平均欧氏距离：

$$
e_{mean}
=
\frac{1}{4}
\sum_{i=0}^{3}
\left\|
m_i-\hat m_i
\right\|_2
$$

两者都是像素单位。工程阈值应根据实际相机、分辨率和标签尺寸测量，不应照搬一个
跨场景通用的数字。

## 14. 从相机坐标换到前左上坐标

旧工程使用的轴换向矩阵为：

$$
S=
\begin{bmatrix}
0&0&1\\
-1&0&0\\
0&-1&0
\end{bmatrix}
$$

对于相机坐标中的点 $p_c$：

$$
p_{flup}=S p_c
=
\begin{bmatrix}
z_c\\
-x_c\\
-y_c
\end{bmatrix}
$$

结果为：

- x 向前；
- y 向左；
- z 向上。

若同时对旋转两端的坐标基进行相同换向，则：

$$
R_{fa}=S R_{ca} S^T
$$

这里 $S^T$ 是因为新坐标轴定义同时作用于源坐标和目标坐标，不能只乘一次。

必须区分：

```text
轴换向：方向变，原点仍在相机光心
相机安装外参：还要移动和旋转到车体坐标
```

## 15. 从标签到交接机构

设完整固定外参为：

- $T_{bc}$：相机相对 BR 底盘；
- $T_{atr}$：TR 底盘相对标签；
- $T_{trh}$：交接机构相对 TR 底盘。

则交接机构相对 BR 底盘的位姿为：

$$
T_{bh}
=
T_{bc}
T_{ca}
T_{atr}
T_{trh}
$$

这里的乘法顺序必须与变换方向一致。每个矩阵都表示“从右侧坐标到左侧坐标”。

如果只需要标签相对 BR 底盘：

$$
T_{ba}=T_{bc}T_{ca}
$$

若已知目标是标签上的另一个固定点 $G$，其相对标签的齐次变换为 $T_{ag}$，则：

$$
T_{bg}=T_{bc}T_{ca}T_{ag}
$$

这一步解释为什么“标签位姿正确”仍可能“交接机构位置不正确”。

## 16. 从旋转矩阵取 yaw

在 $x$ 前、$y$ 左、$z$ 上的坐标中，绕 z 轴的 yaw 为：

$$
\psi=
\operatorname{atan2}
\left(R_{21},R_{11}\right)
$$

角度形式：

$$
\psi^\circ=\psi\frac{180}{\pi}
$$

为了把角度限制在 $[-\pi,\pi]$：

$$
\psi_{wrapped}
=
\operatorname{atan2}(\sin\psi,\cos\psi)
$$

如果业务只关心模 180° 的方向，可能还会额外折叠；但这种折叠会改变角度含义，
不能与完整朝向混用。

## 17. 结果怎样导出

### 17.1 PnP 直接结果

常见形式：

```text
rvec: 3×1 旋转向量
tvec: 3×1 平移，单位与标签边长一致
```

若标签边长为米，则 `tvec` 通常为米。工程输出常转换为毫米：

$$
t_{mm}=1000t_m
$$

### 17.2 齐次矩阵

```text
T_ca = [R_ca  t_ca]
       [0     1  ]
```

### 17.3 工程结果

一个可检查的结果至少应包含：

```text
valid
stamp
tag_id
frame_id
R or quaternion
t
reprojection_error
```

只输出 `x/y/z` 会丢失完整旋转、坐标系和质量信息。

## 18. 用实测输出对照

一次手机显示 AprilTag 的测试结果：

```text
valid=1 target_id=0
x_c_mm=31.36 y_c_mm=-46.88 z_c_mm=292.27
x_fwd_mm=292.27 y_left_mm=-31.36 z_up_mm=46.88
yaw_z_deg=158.88 reproj_px=3.52
```

可解释为：

- 原始相机坐标平移约为 $[31.36,-46.88,292.27]$ mm；
- 前左上轴换向后约为 $[292.27,-31.36,46.88]$ mm；
- 标签在相机前方约 292 mm；
- yaw 约为 158.88°，需要结合旋转矩阵和画面判断具体朝向；
- 重投影误差约 3.52 像素；
- 这说明该帧通过最低几何门槛，但不能证明标定、标签尺寸和安装外参都正确。

由于手机显示尺寸、屏幕反光和间歇检测，该数据只能用于链路验证。

## 19. 完整求解流程

```text
1. 读取 K、D 和标签模型边长 L
2. 检测 ID 和四个像素角点
3. 建立四个标签平面三维模型点
4. 构造平面单应 H
5. 由 SVD 求 H
6. 由 K^-1 H 的列提取 R、t 初值
7. 正交化并消去镜像
8. 用带畸变的投影模型做非线性优化
9. 得到 rvec/tvec
10. 计算重投影误差并判断有效性
11. 串联相机、标签和交接机构外参
12. 输出带时间戳、ID 和坐标系的相对位姿
```

## 20. 最终结论

AprilTag 位姿估计的核心不是“从 ID 查一个位置”，而是：

1. 用已知标签几何提供三维模型；
2. 用检测角点提供二维观测；
3. 用相机内参和畸变建立投影关系；
4. 通过平面 PnP 求相机与标签的相对变换；
5. 再通过外参链把标签位姿转换为机器人交接位姿。

原理层面的系统流程见 [AprilTag 定位原理](视觉基础_02_AprilTag定位原理.md)；
内参和畸变怎样获得见 [相机标定原理与操作](视觉基础_04_相机标定原理与操作.md)。
