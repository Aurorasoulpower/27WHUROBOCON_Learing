---
created: 2026-10-02
type: Note
tags:
  - "#ros2"
---

### 1. CMake 关键字拼写错误（3 次）
CMake 关键字大小写敏感，手敲容易错：

| 错误 | 正确 |
|------|------|
| `TARGETs` | `TARGETS` |
| `DESTINANTION` | `DESTINATION` |
| `TARGES` | `TARGETS` |

正确写法：
```cmake
install(TARGETS
  example_cpp
  DESTINATION lib/${PROJECT_NAME}
)
```

### 2. C++ 用了中文引号
```cpp
RCLCPP_INFO(node->get_logger(),"node_01节点已经启动.“);
                                            ^^^ 中文引号
```
开头英文 `"`，结尾中文 `“` → 编译报 `missing terminating " character`。
**代码里标点必须英文半角，中文只能放字符串内容里。**

### 3. 在错误目录 build
在 `src/example_py` 里跑了 `colcon build`，应该在工作空间根目录 `chapt2_ws`。

> **在哪个目录 build，build/install/log 就生成在哪个目录。**

后果：环境变量被污染，之后每次 build 刷一堆 `WARNING: ... doesn't exist`。**新开终端**可解决。

### 4. setup.py 漏逗号
```python
# 错误：字符串自动拼接
'node_02 = example_py.node_02:main'
'node_04 = example_py.node_04:main',

# 正确
'node_02 = example_py.node_02:main',
'node_04 = example_py.node_04:main',
```
Python 相邻字符串会自动拼成一个，导致 `node_02mainnode_04`。

---

## 二、核心规则
### 目录
| 目录 | 作用 | 能否删 |
|------|------|--------|
| `src/` | 源码 | ❌ 别碰 |
| `build/` `install/` `log/` | 编译产物 | ✅ 可删 |

### 标准流程（永远在根目录）
```bash
cd ~/d2lros2/chapt2/chapt2_ws
colcon build --packages-select 包名
source install/setup.bash
ros2 run 包名 可执行名
```

### 改动后万能重置
```bash
cd ~/d2lros2/chapt2/chapt2_ws
rm -rf build install log
colcon build
source install/setup.bash
```
