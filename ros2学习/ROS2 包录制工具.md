---
created: 2026-10-06
type: Note
tags:
  - ros2
---
# rosbag2 数据录播工具笔记

## 一、定位

rosbag2 是 ROS2 的数据录制与回放工具。把话题上流动的数据录成文件，之后不启动原节点也能把数据重新发布出来。

**核心价值**：把动态的、转瞬即逝的机器人数据，变成静态的、可重复的文件。

## 二、典型用途

| 场景 | 说明 |
|------|------|
| 复现 bug | 用户录一段出问题的数据发给你，不用复现现场环境，回放即可 |
| 分享数据 | 把数据录下来给别人，验证算法 |
| 算法测试 | 同一段数据反复回放，测试稳定性 |
| 数据驱动开发 | 用真实数据调试，不用每次都跑硬件 |
| 训练 AI | 录制带标注的数据做数据集 |

## 三、安装

ROS2 安装时 rosbag2 已经自带，不用单独装。

确认能用：

```bash
ros2 bag --help
```

## 四、录制

### 4.1 基本命令

```bash
# 录制单个话题
ros2 bag record /topic_name

# 录制多个话题
ros2 bag record /topic1 /topic2

# 录制所有话题
ros2 bag record -a

# 自定义输出名字（默认带时间戳）
ros2 bag record -o my_bag /topic_name
```

### 4.2 停止录制

在录制终端按 `Ctrl+C`。

停止时会看到：

```
[INFO] [rosbag2_cpp]: Writing remaining messages from cache to the bag. It may take a while
```

这说明内存缓存里的消息正在刷到磁盘。等它完成，录制才真正结束。

### 4.3 录制过程中可以做的事

| 操作 | 效果 |
|------|------|
| 空格键 | 暂停 / 恢复录制 |
| Ctrl+C | 停止录制 |

暂停功能教材没提，但在录制终端启动时会显示 `Press SPACE for pausing/resuming`，很实用。

### 4.4 录制产出

在当前目录下生成一个文件夹：

```
rosbag2_2026_10_06-16_20_34/
├── metadata.yaml
└── rosbag2_2026_10_06-16_20_34_0.db3
```

- `.db3`：SQLite3 数据库，存所有消息
- `metadata.yaml`：元数据，记录话题、类型、消息数、时长

**文件夹创建在你执行命令时的当前目录**。建议先 `cd` 到一个专门存数据的地方再录，不要把 bag 混在工作空间里。

### 4.5 存储格式

Humble 里默认用 SQLite3。可以用 `-s` 指定其他格式，但其他格式需要额外装插件，默认的够用。

## 五、查看 bag 信息

```bash
ros2 bag info <bag_folder>
```

输出示例：

```
Files:             rosbag2_xxx.db3
Bag size:          100.0 KiB
Storage id:        sqlite3
Duration:          10.5s
Start:             Oct  6 2026 15:31:41.123
End:               Oct  6 2026 15:31:51.623
Messages:          21
Topic information: Topic: /chatter | Type: std_msgs/msg/String | Count: 21 | Serialization Format: cdr
```

关键字段：

| 字段 | 含义 |
|------|------|
| Bag size | 文件大小 |
| Duration | 录制时长 |
| Messages | 总消息数 |
| Topic information | 每个话题的类型、消息数 |

## 六、回放

### 6.1 基本命令

```bash
ros2 bag play <bag_folder>
```

也可以直接指定 `.db3` 文件：

```bash
ros2 bag play <bag_folder>/xxx.db3
```

两种都行，推荐用文件夹，因为带 `metadata.yaml`，信息更完整。

### 6.2 回放时的快捷键

回放命令启动后，终端会显示：

```
Press SPACE for Pause/Resume
Press CURSOR_RIGHT for Play Next Message
Press CURSOR_UP for Increase Rate 10%
Press CURSOR_DOWN for Decrease Rate 10%
```

| 快捷键 | 效果 |
|--------|------|
| 空格 | 暂停 / 恢复 |
| 右方向键 | 逐帧播放（放一条消息） |
| 上方向键 | 速率 +10% |
| 下方向键 | 速率 -10% |
| Ctrl+C | 停止回放 |

### 6.3 常用回放选项

```bash
# 倍速播放（2 倍速）
ros2 bag play <bag> -r 2

# 慢放（半速）
ros2 bag play <bag> -r 0.5

# 循环播放
ros2 bag play <bag> -l

# 只播放某个话题
ros2 bag play <bag> --topics /topic_name

# 从录制开始后 5 秒的位置播放
ros2 bag play <bag> --start-offset 5.0

# 用仿真时间（节点需设 use_sim_time=true）
ros2 bag play <bag> --clock
```

### 6.4 回放结束

bag 里的消息放完，`ros2 bag play` 会自动退出，回到终端提示符。不会一直挂着。

加了 `-l` 则循环播放，直到 Ctrl+C。

### 6.5 验证数据流

回放时新开一个终端：

```bash
ros2 topic echo /topic_name
ros2 topic hz /topic_name
```

能看消息按原节奏重现。

## 七、实操案例：录制小乌龟动作

### 7.1 录制

```bash
# 终端一：模拟器
ros2 run turtlesim turtlesim_node

# 终端二：键盘控制
ros2 run turtlesim turtle_teleop_key

# 终端三：录制（先 cd 到一个合适的目录）
cd ~/bags
ros2 bag record /turtle1/cmd_vel /turtle1/pose
```

在小乌龟终端按方向键让乌龟动几秒，然后 Ctrl+C 停止录制。

### 7.2 查看

```bash
ros2 bag info rosbag2_xxx/
```

会看到两个话题：`/turtle1/cmd_vel` 和 `/turtle1/pose`。

### 7.3 回放

先把 turtlesim 和 teleop_key 关掉。然后：

```bash
# 启动一个干净的 turtlesim
ros2 run turtlesim turtlesim_node

# 回放，只放 cmd_vel
ros2 bag play rosbag2_xxx/ --topics /turtle1/cmd_vel
```

小乌龟**自动重演刚才你按键盘时的动作**。因为 `/turtle1/cmd_vel` 就是控制指令，回放它等于重新给小乌龟发指令。

这是 bag 最直观的价值：录一段控制指令，回放重现动作。

## 八、常见坑

### 8.1 回放时原数据源还开着

如果原节点还在发布同一个话题，回放的数据和原数据混在一起，`topic echo` 出来的内容会乱。

**回放前把原数据源关掉。**

### 8.2 录制时忘了 Ctrl+C

`ros2 bag record` 会一直录，直到你按 Ctrl+C。忘了停就一直写。

### 8.3 回放时的 ROS2 时间问题

默认情况下，bag 回放用系统真实时间，不是录制时的时间。如果节点里有和“当前时间”相关的逻辑（比如超时判断），回放时可能表现和当时不同。

要让节点用录制时的时间戳，需要：

- 回放时加 `--clock`
- 节点启动时设置 `use_sim_time=true`

```bash
ros2 bag play <bag> --clock
ros2 run <pkg> <node> --ros-args -p use_sim_time:=true
```

这是个进阶用法，用到再深入。

### 8.4 录 `-a` 会让文件变大

`ros2 bag record -a` 会把 `/rosout`、`/parameter_events` 这些系统话题也录进去，文件会变大。正式录数据时通常指定话题，不要用 `-a`。

### 8.5 bag 文件夹混在工作空间里

录 bag 前先 `cd` 到专门目录，比如：

```bash
mkdir -p ~/bags
cd ~/bags
ros2 bag record /topic_name
```

这样数据集中管理，和工作空间分开。

## 九、bag 的局限

- bag 录制的是**话题**数据，不能直接录服务、参数、Action
- 服务、Action 的通信内容如果要录，需要转成话题或另想办法
- bag 文件本身是二进制，不能直接编辑，只能查看和回放

## 十、速查表

```bash
# 录制单个话题
ros2 bag record /topic_name

# 录制多个话题
ros2 bag record /topic1 /topic2

# 录制所有话题
ros2 bag record -a

# 自定义输出名
ros2 bag record -o my_bag /topic_name

# 查看 bag 信息
ros2 bag info <bag_folder>

# 回放
ros2 bag play <bag_folder>

# 倍速播放
ros2 bag play <bag_folder> -r 10

# 循环播放
ros2 bag play <bag_folder> -l

# 只放某个话题
ros2 bag play <bag_folder> --topics /topic_name

# 从某个时间点开始
ros2 bag play <bag_folder> --start-offset 5.0

# 用仿真时间
ros2 bag play <bag_folder> --clock

# 查看帮助
ros2 bag -h
ros2 bag record -h
ros2 bag play -h
```

