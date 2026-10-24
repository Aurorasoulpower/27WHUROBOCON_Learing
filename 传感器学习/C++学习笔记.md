# C++ 学习笔记

这份笔记汇总 C++ 语言基础、面向对象、模板、异常处理、文件流、STL 容器和多线程，并结合 ROS 2 中常见的节点、消息和图像处理场景说明用法。

示例以 C++17 为主。涉及 ROS 2 的代码需要对应的 ROS 2 开发环境；示例重点是表达用法和资源管理方式，实际工程中仍应结合具体接口和版本检查。

## 一、C++ 语言基础

这一部分先建立 C++ 的基本语法、作用域、数据表示和资源管理习惯，后续的类、模板与并发代码都会反复用到这些基础。

### 1. C++ 基础语法

#### 一、 C++ 结构体 (struct)
**基本概念**：C 语言的升级版。
*   **与 C 区别**：C++ 的 `struct` 可以包含成员函数、构造函数、继承和多态。
*   **默认权限**：`class` 默认 `private`，`struct` 默认 `public`。现代 C++ 常用 `struct` 定义纯数据集合（POD），用 `class` 定义有行为的对象。

#### 二、 C++ 常量 (const / constexpr / # define)
**基本概念**：程序运行期间不可改变的值。 

| 关键字 | 特性 | 适用场景 |
| :--- | :--- | :--- |
| `const` | 运行期常量，有类型检查，有作用域。 | 修饰变量、函数参数、成员函数。 |
| `constexpr` | 编译期常量（C++11），编译器直接算结果，性能更好。 | 数组大小、模板参数、编译期计算。 |
| `#define` | 预处理宏替换，无类型检查，无作用域，极易出错。 | 仅用于条件编译（`#ifdef`），**抛弃用于定义常量**。 |

*   **const 修饰指针的三种组合**：
    *   `const int* p`：指向常量的指针（不能改值，能改指向）。
    *   `int* const p`：常量指针（能改值，不能改指向）。
    *   `const int* const p`：指向常量的常量指针（都不能改）。

#### 三、 C++ 存储类 (Storage Classes)
**基本概念**：控制变量的生命周期、作用域和链接性。

| 存储类 | 说明 |
| :--- | :--- |
| `static` | 静态存储期。局部静态变量只初始化一次；全局静态变量限制在当前文件；类静态成员属于类本身。 |
| `extern` | 声明外部变量（定义在另一个文件中），用于跨文件共享。 |
| `thread_local` | (C++11) 线程局部存储，每个线程拥有独立的数据副本。 |
| `mutable` | 突破 `const` 限制，允许在 `const` 成员函数中修改特定成员变量。 |
| `register` | (C++17 已废弃) 建议编译器放入寄存器，不要使用。 |

#### 四、 C++ 修饰符类型 (Type Modifiers)
**基本概念**：改变基本数据类型的含义、大小和符号性。

| 修饰符 | 作用 | 备注 |
| :--- | :--- | :--- |
| `signed` | 有符号（默认）。 | 通常省略。 |
| `unsigned` | 无符号。 | 处理位运算、二进制数据必备。 |
| `short` | 短整型。 | 通常 2 字节。 |
| `long` | 长整型。 | 通常 4 或 8 字节。 |
| `long long` | 超长整型（C++11）。 | 至少 8 字节。 |
| `volatile` | 禁止编译器优化该变量，每次必须从内存读取。 | 多线程、嵌入式硬件寄存器场景使用。 |

*   **字符类型大小**：`char` 通常 1 字节；`wchar_t` 宽字符（Windows 2 字节，Linux 4 字节）；`char16_t`/`char32_t`（C++11 用于 Unicode）。
*   **布尔类型**：`bool`（C++原生支持，值为 `true` / `false`）。

#### 五、 C++ 变量作用域 (Scope)
**基本概念**：变量可见和有效的范围。

| 作用域类型 | 说明 |
| :--- | :--- |
| 局部作用域 | 函数或代码块内部。同名的局部变量会遮蔽全局变量。 |
| 全局作用域 | 所有函数外部。默认外部链接。 |
| 类作用域 | 类成员变量，通过对象或 `::` 访问。 |
| 命名空间作用域 | `namespace` 内的变量，通过 `::` 访问。 |
| 块作用域 | `{}` 内的变量，C++ 允许随用随声明。 |

*   **`::`（作用域解析符）**：在局部变量遮蔽全局变量时，用 `::var` 显式访问全局变量。
*   **静态局部变量**：作用域限于函数内部，但生命周期贯穿整个程序（只初始化一次）。

#### 六、 C++ 预处理器 (Preprocessor)
**基本概念**：在编译之前对代码进行文本替换和条件处理。ROS2 源码中大量使用。

| 指令 | 说明 | 实战用途 |
| :--- | :--- | :--- |
| `#include` | 包含头文件。 | 引入 `<rclcpp/rclcpp.hpp>` 等。 |
| `#define` | 定义宏常量或宏函数。 | 定义简单的编译期常量。 |
| `#ifdef` / `#ifndef` / `#endif` | 条件编译。 | 头文件卫士（防止重复包含）、跨平台代码。 |
| `#pragma once` | 现代头文件卫士。 | 替代 `#ifndef`，更简洁，编译器广泛支持。 |
| `#` | 字符串化运算符（将参数转为字符串）。 | 宏调试输出。 |
| `##` | 标记粘贴运算符（拼接参数）。 | 生成函数名或变量名。 |

*   **ROS2 宏**：`RCLCPP_INFO`, `RCLCPP_ERROR` 均为预处理器宏，底层调用 ROS2 日志库。

#### 七、 C++ 基本语法 / 循环 / 判断 补充
**基本概念**：与 C 语言高度一致，以下是需要速查的现代 C++ 特性。

*   **变量声明**：任意位置声明（C 语言必须在块首部）。
*   **范围 for 循环 (C++11)**：`for (const auto& x : arr) { ... }`（只读推荐），`for (auto& x : arr) { ... }`（修改元素）。
*   **带初始化的 if (C++17)**：`if (int x = getValue(); x > 0) { ... }`，`x` 作用域严格限制在 `if` 内。
*   **`auto` 关键字**：自动类型推导（`auto x = 5;`）。C 语言中表示局部变量（已废弃语义）。
*   **`nullptr`**：空指针，替代 `NULL`。
*   **范围 for 与 `std::array` / `std::vector`**：直接遍历容器，无需手动管理索引和长度。

#### 八、 C++ 信号处理 (Signal Handling)
**基本概念**：处理操作系统发送的信号（如 `Ctrl+C` 的 `SIGINT`）。
*   **ROS2 关联**：**无需手写**。ROS2 内部已经处理好了 `SIGINT`，在 `rclcpp::spin()` 阻塞时按下 `Ctrl+C` 会中断阻塞，你只需要调用 `rclcpp::shutdown()` 即可优雅退出。直接跳过此章节。

#### 九、 C++ Web 编程
**基本概念**：用 C++ 写 HTTP 服务器、WebSocket 等。
*   **ROS2 关联**：**无关，直接跳过**。ROS2 的 Web 可视化通常用 `rosbridge_suite` 结合前端（React/Vue）实现，或者用 Python 写 Web 后端。C++ 写 Web 极少出现在机器人视觉开发中。


### 2. 命名空间

#### 核心思想
给代码加“姓氏”，解决不同库或不同模块之间的命名冲突。本质上，命名空间就是一个“文件夹”，不同文件夹里可以有重名的文件。

##### 1. 定义与访问命名空间
**功能**：声明一个命名空间并在其中定义变量/函数；通过 `::`（作用域解析符）访问。

```cpp
# 示例：定义并访问命名空间
namespace my_vision { // 定义命名空间
    int width = 640;
    void process() { /* ... */ }
}

namespace your_vision {
    int width = 1280;
}

int main() {
    // 使用 :: 操作符明确指定使用哪个命名空间下的变量
    std::cout << my_vision::width << std::endl;  // 输出 640
    std::cout << your_vision::width << std::endl;// 输出 1280
    my_vision::process(); // 调用 my_vision 里的函数
    return 0;
}
```

##### 2. 局部引入 `using` 声明（推荐）
**功能**：只引入命名空间中的某一个特定成员，避免全局污染。

```cpp
# 示例：局部引入特定成员
#include <iostream>

using std::cout; // 只引入 std 命名空间里的 cout
using std::endl;

int main() {
    cout << "Hello" << endl; // ✅ 合法，已引入
    // cin >> x; // ❌ 报错，未引入 cin，必须写 std::cin
    return 0;
}
```

##### 3. 全局引入 `using` 指令（慎用）
**功能**：引入整个命名空间，后续代码无需加前缀。

```cpp
# 示例：全局引入整个命名空间
using namespace std; // ⚠️ 将 std 里的所有名字暴露在当前作用域

int main() {
    cout << "Hello" << endl; // 可以直接使用，不需要 std::
    return 0;
}
```
**💡 ROS2 避坑**：**绝对不要在头文件（`.hpp`）中使用 `using namespace std;`**。头文件会被到处 `#include`，这会导致所有包含它的文件都被迫引入 `std`，极易造成命名冲突（比如 `std::count` 和自定义的 `count`），引发编译错误。

##### 4. 嵌套命名空间与 `::`
**功能**：命名空间可以嵌套定义，用于进一步的模块化分类。

```cpp
# 示例：嵌套命名空间
namespace robot {
    namespace vision {
        void detect() { /* ... */ }
    }
}

int main() {
    // 逐层访问
    robot::vision::detect(); 
    
    // 使用 using 局部引入嵌套命名空间中的特定内容
    using robot::vision::detect;
    detect(); // 直接调用
    return 0;
}
```

##### 5. 命名空间别名
**功能**：给长命名空间取短名字，简化书写。

```cpp
# 示例：命名空间别名
namespace rv = robot::vision; // 定义别名

int main() {
    rv::detect(); // 等价于 robot::vision::detect()
    return 0;
}
```

##### 6. 匿名命名空间（替代 C 语言中的 `static`）
**功能**：将内部链接性赋予变量或函数，使其只在当前源文件可见。

```cpp
# 示例：匿名命名空间
namespace { // 没有名字
    int internal_state = 42; // 仅当前 .cpp 文件可见
}

// 等同于 C 语言中：static int internal_state = 42;
```

---

#### 🔗 结合 ROS2：命名空间如何用？

##### 场景 1：理解 ROS2 消息类型的全名
ROS2 的核心消息类型都采用“包名::msg::类型名”的嵌套结构，这正是命名空间的体现。

```cpp
# 示例：ROS2 图像消息类型
#include <sensor_msgs/msg/image.hpp>

// sensor_msgs 是包名（命名空间），msg 是子命名空间，Image 是类名
sensor_msgs::msg::Image img_msg; 
```

##### 场景 2：在 ROS2 节点中使用 `using` 简化类型
ROS2 消息类型通常很长，**在 `.cpp` 文件中**可以使用 `using` 别名来简化代码。

```cpp
# 示例：ROS2 中使用类型别名
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

// 在 .cpp 文件中定义别名，安全且不污染头文件
using ImageMsg = sensor_msgs::msg::Image;
using PointCloudMsg = sensor_msgs::msg::PointCloud2;

class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // 使用别名声明订阅者
        sub_ = this->create_subscription<ImageMsg>(
            "image_topic", 10, std::bind(&VisionNode::callback, this, std::placeholders::_1));
    }
private:
    void callback(const ImageMsg::SharedPtr msg) { /* ... */ }
    rclcpp::Subscription<ImageMsg>::SharedPtr sub_;
};
```

##### 场景 3：封装自己的 ROS2 视觉模块
在开发大型视觉系统时，建议将自己的代码放入自定义的命名空间中，与 ROS2 底层库隔离。

```cpp
# 示例：自定义命名空间封装视觉模块
namespace my_robot {
namespace vision {

class ObjectDetector : public rclcpp::Node {
public:
    ObjectDetector() : Node("detector") {}
    void detect() { /* ... */ }
};

} // namespace vision
} // namespace my_robot

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    // 明确指定使用自定义命名空间下的类
    auto node = std::make_shared<my_robot::vision::ObjectDetector>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

##### 场景 4：避免 ROS2 头文件中的命名污染
```cpp
# 示例：头文件中正确的做法
// my_vision.hpp
#ifndef MY_VISION_HPP
#define MY_VISION_HPP

#include <sensor_msgs/msg/image.hpp>

namespace my_robot {
namespace vision {

class Processor {
public:
    // ✅ 明确写出完整命名空间，绝对不写 using namespace std;
    void process(const sensor_msgs::msg::Image::SharedPtr msg);
};

} // namespace vision
} // namespace my_robot

#endif
```

### 3. 字符串

#### 核心思想
彻底抛弃 C 语言的 `char[]` 和 `<cstring>`（`strcpy`、`strlen`）。`std::string` 是一个类，自动管理内存，支持动态扩容、拼接、比较，完全不需要操心 `\0` 和越界问题。

##### 1. 包含头文件与初始化
**功能**：引入字符串类，并使用多种方式初始化。

```cpp
# 示例：字符串初始化
#include <string>

std::string s1;                  // 空字符串
std::string s2 = "hello";        // 从 C 风格字符串构造
std::string s3(5, 'a');          // 5 个 'a'，即 "aaaaa"
std::string s4 = s2;             // 拷贝构造
```

##### 2. 长度与判空
**功能**：获取字符个数，判断是否为空。`size()` 和 `length()` 完全等价。

```cpp
# 示例：长度与判空
std::string s = "hello";
int len = s.size();              // 5
bool empty = s.empty();          // false（如果为空则返回 true）
s.clear();                       // 清空字符串，变为 ""
```

##### 3. 拼接字符串
**功能**：使用 `+` 或 `+=` 拼接字符串，自动处理内存扩容。

```cpp
# 示例：字符串拼接
std::string s1 = "Hello";
std::string s2 = " ROS2";
std::string s3 = s1 + s2;        // "Hello ROS2"
s1 += " World";                  // s1 变为 "Hello World"
s1.append("!!!");                // 追加到末尾，s1 变为 "Hello World!!!"
```

##### 4. 查找与替换
**功能**：查找子串或字符，返回索引位置（找不到返回 `std::string::npos`）。`replace` 用于替换指定区间。

```cpp
# 示例：查找与替换
std::string s = "image_topic";
size_t pos = s.find("topic");    // 返回索引 6
if (pos != std::string::npos) {  // npos 表示未找到
    s.replace(pos, 5, "data");   // 从 pos 开始，替换 5 个字符为 "data"
}                                // s 变为 "image_data"
```

##### 5. 截取子串：`substr`
**功能**：从指定位置截取指定长度的子串。

```cpp
# 示例：截取子串
std::string s = "camera_info.yaml";
// 从索引 0 开始，截取 7 个字符
std::string name = s.substr(0, 7);   // "camera_"
// 从索引 7 开始，截取到末尾
std::string ext = s.substr(7);       // "info.yaml"
```

##### 6. 插入与删除
**功能**：`insert` 在指定位置插入，`erase` 删除指定区间。

```cpp
# 示例：插入与删除
std::string s = "Hello";
s.insert(0, "Say: ");            // 在索引 0 插入，s 变为 "Say: Hello"
s.erase(0, 5);                   // 从索引 0 开始删除 5 个字符，s 变为 "Hello"
```

##### 7. 遍历字符串
**功能**：使用基于范围的 for 循环或下标遍历。

```cpp
# 示例：遍历字符串
std::string s = "ROS2";
// 方式1：基于范围的 for（只读推荐）
for (const char& c : s) {
    std::cout << c << " ";
}
// 方式2：下标遍历
for (size_t i = 0; i < s.size(); ++i) {
    std::cout << s[i] << " ";
}
```

##### 8. 类型转换
**功能**：`std::to_string` 将数值转为字符串，`std::stoi` / `std::stod` 将字符串转为数值。

```cpp
# 示例：类型转换
int num = 42;
std::string s = std::to_string(num); // "42"

std::string pi_str = "3.14";
double pi = std::stod(pi_str);       // 3.14
int i = std::stoi("100");            // 100
```

##### 9. 字符串视图 `std::string_view` (C++17)
**功能**：只读字符串的轻量级视图，避免拷贝开销。在只需要读取字符串时使用。

```cpp
# 示例：string_view 避免拷贝
#include <string_view>

void printString(std::string_view sv) { // 不拷贝底层字符串
    std::cout << sv << std::endl;
}

std::string s = "hello";
printString(s);                      // 隐式转换为 string_view
printString("world");                // 字面量也可以直接传入
```

---

#### 🔗 结合 ROS2：字符串如何用？

##### 场景 1：声明与读取 ROS2 参数
ROS2 参数系统底层大量使用 `std::string`。话题名、配置文件路径、算法名称通常都是字符串。

```cpp
# 示例：ROS2 字符串参数
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // 声明字符串参数，默认值为 "image_raw"
        this->declare_parameter("input_topic", "image_raw");
        // 读取参数
        std::string topic = this->get_parameter("input_topic").as_string();
        
        sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            topic, 10, std::bind(&VisionNode::callback, this, std::placeholders::_1));
    }
private:
    void callback(const sensor_msgs::msg::Image::SharedPtr msg) { /* ... */ }
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

##### 场景 2：cv_bridge 编码格式转换
`cv_bridge` 在 ROS2 图像消息和 OpenCV `cv::Mat` 之间转换时，必须传入编码格式字符串（如 `"bgr8"`, `"mono8"`）。

```cpp
# 示例：图像编码格式
try {
    // 第三个参数是编码格式字符串
    cv::Mat img = cv_bridge::toCvShare(msg, "bgr8")->image; 
    cv::cvtColor(img, gray, cv::COLOR_BGR2GRAY);
    // 转回 ROS2 消息时也需要指定编码格式
    auto out_msg = cv_bridge::CvImage(std_msgs::msg::Header(), "mono8", gray).toImageMsg();
} catch (const cv_bridge::Exception& e) {
    RCLCPP_ERROR(this->get_logger(), "cv_bridge error: %s", e.what());
}
```

##### 场景 3：读取标定文件路径拼接
在 ROS2 中读取 YAML 标定文件，通常需要将包路径和文件名拼接。使用 `std::string` 的 `+` 或 `std::filesystem` 更安全。

```cpp
# 示例：路径拼接
#include <filesystem>

std::string pkg_path = "/home/user/ros2_ws/src/vision/config/";
std::string file_name = "camera_calib.yaml";
// 方式1：字符串拼接
std::string full_path = pkg_path + file_name;

// 方式2：使用 C++17 filesystem（更安全，处理跨平台分隔符）
std::filesystem::path path = std::filesystem::path(pkg_path) / file_name;
cv::FileStorage fs(path.string(), cv::FileStorage::READ);
```

##### 场景 4：日志打印与格式化
ROS2 的日志宏 `RCLCPP_INFO` 底层使用了 C 风格的格式化字符串，但结合 `std::string` 时，需要通过 `.c_str()` 转换。

```cpp
# 示例：字符串日志打印
std::string topic_name = "image_raw";
int frame_count = 100;

// RCLCPP_INFO 使用 %s 占位符，必须传 .c_str()
RCLCPP_INFO(this->get_logger(), "Topic: %s, Frames: %d", topic_name.c_str(), frame_count);
```

##### 场景 5：解析机器人 URDF 或参数 YAML
当从 YAML 文件中读取参数时，解析出的字符串可能需要进一步处理（截取、查找、替换）。

```cpp
# 示例：处理 YAML 解析结果
std::string joint_name = "camera_joint_optical_frame";
// 判断是否包含特定前缀
if (joint_name.find("camera_") == 0) { // 索引 0 表示以 camera_ 开头
    // 截取子串，去掉前缀
    std::string sensor_type = joint_name.substr(7, 6); // "joint_"
}
```

### 4. 指针与引用

#### 核心思想
指针是一个存放内存地址的变量，可以为空、可以重新指向；引用是一个已存在变量的别名，不能为空、不能重新绑定。现代 C++（ROS2）极力推荐用引用替代指针，用智能指针替代裸指针。

##### 1. 指针的声明与解引用
**功能**：声明指针变量，存储变量地址，通过 `*` 解引用修改原值。

```cpp
# 示例：指针基础操作
int a = 10;
int* p = &a; // p 存放 a 的地址（& 取地址符）
*p = 20;     // * 解引用，将 a 的值修改为 20
```

##### 2. 空指针：`nullptr`（推荐）与 `NULL`
**功能**：表示指针不指向任何对象。C++11 推荐使用 `nullptr` 替代 C 语言的 `NULL`。

```cpp
# 示例：空指针初始化
int* p1 = nullptr; // ✅ C++11 专属空指针，类型安全
int* p2 = NULL;    // ❌ 本质是 0，容易引发函数重载歧义
```

##### 3. 指针与常量：`const` 的三种组合
**功能**：限制指针本身或被指向的数据不可修改。

```cpp
# 示例：const 与指针
int a = 10, b = 20;

// 1. 指向常量的指针（不能通过 p1 修改 a，但 p1 可以指向 b）
const int* p1 = &a; 
// *p1 = 30; // ❌ 报错
p1 = &b;     // ✅ 合法

// 2. 常量指针（p2 不能重新指向，但可以修改 a）
int* const p2 = &a;
*p2 = 30;    // ✅ 合法
// p2 = &b;  // ❌ 报错

// 3. 指向常量的常量指针（都不可以修改）
const int* const p3 = &a;
```

##### 4. 引用的声明与使用
**功能**：给变量起别名，操作引用等同于操作原变量。

```cpp
# 示例：引用基础
int a = 10;
int& ref = a; // ref 是 a 的别名，必须初始化
ref = 20;     // a 的值变为 20
```

##### 5. 引用作为函数参数（推荐替代指针传参）
**功能**：直接修改外部变量，语法比指针更清晰。

```cpp
# 示例：引用传参
void increment(int& x) { ++x; } // 不需要 & 取地址，不需要 * 解引用

int main() {
    int num = 0;
    increment(num);
    return 0;
}
```

##### 6. 常量引用作为函数参数（只读传参首选）
**功能**：避免拷贝开销，同时防止函数内部修改数据。

```cpp
# 示例：常量引用传参
void printImage(const cv::Mat& img) { // 不会拷贝 img，也不能修改它
    std::cout << img.rows << std::endl;
}
```

##### 7. 引用作为函数返回值
**功能**：返回引用可以避免拷贝，但绝对不能返回局部变量的引用。

```cpp
# 示例：返回引用
int& getElement(std::vector<int>& vec, int index) {
    return vec[index]; // 返回引用，外部可以直接修改
}

int main() {
    std::vector<int> v = {1, 2, 3};
    getElement(v, 1) = 10; // 直接修改 v[1] 为 10
    return 0;
}
```

##### 8. 右值引用与移动语义（C++11）
**功能**：`&&` 用于绑定临时对象（右值），配合 `std::move` 实现资源转移，避免深拷贝。

```cpp
# 示例：右值引用与移动
#include <utility>
#include <string>

std::string str1 = "hello";
std::string str2 = std::move(str1); // 转移所有权，str1 变为空，str2 获取数据
```

---

#### 🔗 结合 ROS2：指针与引用如何用？

##### 场景 1：彻底抛弃裸指针，全面使用智能指针
在 ROS2 中，对象的生命周期极其复杂（多线程、异步发布），绝不能使用裸指针 `new/delete`。

```cpp
# 示例：ROS2 创建节点
// ✅ 正确：使用智能指针管理节点生命周期
auto node = std::make_shared<rclcpp::Node>("vision_node"); 
// auto node = new rclcpp::Node("vision_node"); // ❌ 灾难，忘记 delete 直接内存泄漏
```

##### 场景 2：消息回调中的 `SharedPtr`
图像数据很大，ROS2 回调函数参数使用 `const SharedPtr`，既避免了拷贝，又共享了生命周期。

```cpp
# 示例：订阅回调参数传递
void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg) { 
    // 智能指针自动管理 msg，无需担心被提前释放
    cv::Mat img = cv_bridge::toCvShare(msg, "bgr8")->image;
}
```

##### 场景 3：只读参数传递使用常量引用
在 ROS2 读取参数、传递配置时，使用 `const &` 避免字符串拷贝。

```cpp
# 示例：读取 ROS2 参数
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // 声明参数
        this->declare_parameter("camera_topic", "default_topic");
    }
    
    // 常量引用接收参数，避免拷贝
    void setTopic(const std::string& topic) { 
        topic_ = topic; 
    }
private:
    std::string topic_;
};
```

##### 场景 4：回调绑定中的 `std::placeholders`
使用 `std::bind` 绑定成员函数时，必须用 `std::placeholders::_1` 占位，并传入 `this` 指针。

```cpp
# 示例：ROS2 绑定回调
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // this 指针被绑定，_1 代表回调函数的参数 msg
        sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "image_topic", 10, 
            std::bind(&VisionNode::imageCallback, this, std::placeholders::_1));
    }
private:
    void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg) { /* ... */ }
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

### 5. 动态内存与智能指针

#### 核心思想：从 C 的裸指针到 C++ 的 RAII 和智能指针
在 C 语言中，`malloc` 和 `free` 是手动挡；在 C++ 中，`new` 和 `delete` 是半自动挡；而现代 C++（C++11 及以后）强制推荐**智能指针**（全自动挡）。ROS2 的底层源码几乎完全依赖智能指针。

---

##### 1. 基础动态分配：`new` 和 `delete`
**功能**：在堆区分配/释放单个对象的内存，并自动调用构造/析构函数。

```cpp
# 示例：动态分配单个整数
int* p = new int(10); // 分配内存并初始化为10（普通括号）
delete p;             // 释放内存，p变为悬空指针，建议置空 p = nullptr;
```

**对比 C 语言**：
*   `malloc` 只分配内存，不调用构造函数，返回 `void*`。
*   `new` 分配内存并调用构造函数，返回具体类型指针。
*   `free` 只释放内存，不调用析构函数。
*   `delete` 先调用析构函数，再释放内存。

---

##### 2. 数组动态分配：`new[]` 和 `delete[]`
**功能**：在堆区分配/释放连续数组的内存。

```cpp
# 示例：动态分配数组
int* arr = new int[5]; // 分配5个int，未初始化（值为随机垃圾）
int* arr2 = new int[5](); // 分配5个int，值全部初始化为0
delete[] arr;          // 必须用 delete[]，否则只释放第一个元素（内存泄漏）
delete[] arr2;
```
*注意*：`new[]` 分配数组时，会在内存头部额外存储数组长度，`delete[]` 会读取这个长度并依次调用每个元素的析构函数。

---

##### 3. 智能指针：独占所有权 `std::unique_ptr`
**功能**：独占资源，不能拷贝，只能移动。出作用域自动释放。性能与裸指针几乎一样，零额外开销。

```cpp
# 示例：unique_ptr 独占所有权
#include <memory>

std::unique_ptr<int> uptr = std::make_unique<int>(10); // C++14 推荐写法
// std::unique_ptr<int> uptr2 = uptr; // ❌ 编译报错，不可拷贝
std::unique_ptr<int> uptr2 = std::move(uptr); // ✅ 转移所有权，uptr 变为 nullptr
```

---

##### 4. 智能指针：共享所有权 `std::shared_ptr`
**功能**：通过引用计数共享资源，最后一个指针销毁时释放内存。ROS2 的核心依赖。

```cpp
# 示例：shared_ptr 共享所有权
std::shared_ptr<int> sptr1 = std::make_shared<int>(20); // 引用计数=1
std::shared_ptr<int> sptr2 = sptr1; // 引用计数=2，两者共享同一块内存
// sptr1 和 sptr2 都离开作用域时，引用计数归零，内存才被释放
```

---

##### 5. 智能指针：打破循环引用 `std::weak_ptr`
**功能**：不增加引用计数，只观察 `shared_ptr` 管理的对象，解决循环引用导致的内存泄漏。

```cpp
# 示例：weak_ptr 观察者
std::shared_ptr<int> sptr = std::make_shared<int>(30); // 引用计数=1
std::weak_ptr<int> wptr = sptr; // 引用计数依然为1
if (auto locked = wptr.lock()) { // 尝试提升为 shared_ptr
    // 如果对象还活着，locked 不为空，引用计数临时+1
} // 出了 if 作用域，临时共享指针销毁，引用计数恢复
```

---

##### 6. RAII 机制：异常安全
**功能**：利用栈对象的析构函数，保证即使在发生异常抛出时，资源也能被正确释放。

```cpp
# 示例：RAII 自动释放内存
void processImage() {
    std::shared_ptr<int> ptr = std::make_shared<int>(10);
    // 如果下面抛出异常，栈展开，ptr 的析构函数被调用，内存自动释放
    throw std::runtime_error("图像处理失败"); 
}
```

---

#### 🔗 结合 ROS2：动态内存如何用？

在 ROS2 中，**你几乎看不到裸的 `new` 和 `delete`**。ROS2 的架构完全建立在智能指针之上，特别是 `std::shared_ptr`。

##### 场景 1：创建节点
```cpp
# 示例：在 ROS2 中创建节点
#include <rclcpp/rclcpp.hpp>

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    // 使用 make_shared 创建节点，返回 shared_ptr
    auto node = std::make_shared<rclcpp::Node>("vision_node"); 
    rclcpp::spin(node);
    rclcpp::shutdown();
}
```

##### 场景 2：创建并发布消息
```cpp
# 示例：创建和发布图像消息
auto pub = node->create_publisher<sensor_msgs::msg::Image>("image_topic", 10);
// 创建消息的 shared_ptr
auto img_msg = std::make_shared<sensor_msgs::msg::Image>(); 
img_msg->height = 480;
img_msg->width = 640;
pub->publish(*img_msg); // 发布时解引用
```

##### 场景 3：订阅回调中的参数传递
```cpp
# 示例：订阅图像话题的回调函数
// 订阅回调参数通常接收 shared_ptr，避免图像数据的深度拷贝
auto sub = node->create_subscription<sensor_msgs::msg::Image>(
    "image_topic", 10, 
    [](const sensor_msgs::msg::Image::SharedPtr msg) { // 使用 shared_ptr
        // 处理图像，此时 msg 是共享指针，引用计数安全
    }
);
```

##### 为什么 ROS2 疯狂使用 `shared_ptr`？
1. **零拷贝**：图像、点云数据量巨大。使用 `shared_ptr` 传递，多个回调、多个节点可以共享同一份数据，避免 10MB 图像内存被拷贝 10 次。
2. **生命周期安全**：ROS2 是高度异步的（多线程执行器）。如果一个消息被发布出去，还在队列里排队，而发布它的函数已经返回了，如果用裸指针，内存早没了。`shared_ptr` 确保只要有节点还在处理这个消息，内存就不会被释放。
3. **组件化**：ROS2 允许将多个节点放入同一个进程（Component），所有节点共享 `shared_ptr`，高效管理生命周期。


## 二、面向对象编程

在掌握基础语法之后，本节从对象的组织方式进入 C++ 的面向对象设计，包括封装、继承、多态和抽象接口。

### 1. 类和对象

#### 核心思想
把数据（成员变量）和操作数据的函数（成员函数）捆绑在一起，形成自定义数据类型。在 ROS2 中，每个节点本质上就是一个类，继承自 `rclcpp::Node`。

##### 1. 类的定义与访问修饰符
**功能**：定义蓝图，`public` 对外可见，`private` 仅类内部可见。

```cpp
# 示例：定义一个基础类
class VisionSensor {
public: // 公有成员，外部可以访问
    int width;
    void printInfo() { std::cout << "Width: " << width << std::endl; }
private: // 私有成员，仅类内部能访问
    int internal_id;
};
```

##### 2. 对象的创建：栈对象与堆对象
**功能**：栈对象自动管理生命周期，堆对象需要配合智能指针。

```cpp
# 示例：栈对象与堆对象
int main() {
    VisionSensor cam1; // 栈对象，出作用域自动析构
    cam1.width = 640;

    // 堆对象，使用智能指针管理（推荐，符合现代 C++）
    auto cam2 = std::make_shared<VisionSensor>(); 
    cam2->width = 1280;
    return 0;
}
```

##### 3. 构造函数与初始化列表
**功能**：对象创建时自动调用，初始化列表效率比在函数体内赋值更高。

```cpp
# 示例：带初始化列表的构造函数
class VisionSensor {
private:
    int width;
    int height;
public:
    // 初始化列表：在分配内存的同时完成初始化
    VisionSensor(int w, int h) : width(w), height(h) {} 
};
```

##### 4. 析构函数与 RAII
**功能**：对象销毁时自动调用，用于释放资源。配合智能指针实现 RAII 机制。

```cpp
# 示例：析构函数
class VisionSensor {
public:
    VisionSensor() { std::cout << "Open camera" << std::endl; }
    ~VisionSensor() { std::cout << "Close camera" << std::endl; } // 析构函数
};

int main() {
    VisionSensor cam; // 离开作用域时自动输出 "Close camera"
    return 0;
}
```

##### 5. `this` 指针
**功能**：指向当前对象自身。当成员变量与参数同名时必须使用，也可以用来返回对象本身。

```cpp
# 示例：使用 this 指针
class VisionSensor {
private:
    int width;
public:
    void setWidth(int width) {
        this->width = width; // this->width 指成员变量，width 指参数
    }
};
```

##### 6. 常量成员函数（const）
**功能**：承诺不会修改对象的任何成员变量，一般用于 Getter 方法。

```cpp
# 示例：const 成员函数
class VisionSensor {
private:
    int width = 640;
public:
    // const 放在函数末尾，表示该函数不会修改成员变量
    int getWidth() const { return width; } 
};
```

##### 7. 静态成员（static）
**功能**：属于类本身，不属于任何具体对象。所有对象共享同一份静态成员。

```cpp
# 示例：静态成员变量与函数
class VisionSensor {
public:
    static int instance_count; // 静态成员变量声明
    static void printCount() { std::cout << instance_count << std::endl; }
};
int VisionSensor::instance_count = 0; // 静态成员变量必须在类外定义
```

---

#### 🔗 结合 ROS2：类和对象如何用？

##### 场景 1：标准的 ROS2 节点就是一个类
每个 ROS2 节点都需要继承 `rclcpp::Node`，在构造函数中完成发布者、订阅者的初始化。

```cpp
# 示例：最小化 ROS2 节点类
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

class VisionNode : public rclcpp::Node {
public:
    // 构造函数初始化父类，并创建发布者
    VisionNode() : Node("vision_node") { 
        pub_ = this->create_publisher<sensor_msgs::msg::Image>("image_topic", 10);
    }
private:
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_; // 私有成员变量
};
```

##### 场景 2：使用 `this` 指针和私有成员封装
ROS2 中，将订阅者、发布者设为 `private`，并通过 `this->` 调用创建函数，是标准做法。

```cpp
# 示例：封装成员变量
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // this 指向当前节点对象
        sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "image_topic", 10, 
            std::bind(&VisionNode::callback, this, std::placeholders::_1));
    }
private:
    void callback(const sensor_msgs::msg::Image::SharedPtr msg) { /* 处理图像 */ }
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

##### 场景 3：使用智能指针实例化节点
ROS2 官方强烈推荐使用 `std::make_shared` 创建节点对象，而不是直接 `new`。

```cpp
# 示例：实例化 ROS2 节点
int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    // 使用 make_shared 创建堆对象（返回 shared_ptr）
    auto node = std::make_shared<VisionNode>(); 
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

##### 场景 4：用常量成员函数提供只读状态
在视觉节点中，经常需要查询当前节点的某些状态而不修改它，使用 `const` 保护数据。

```cpp
# 示例：const 成员函数在 ROS2 中的应用
class VisionNode : public rclcpp::Node {
private:
    int frame_count_ = 0;
public:
    VisionNode() : Node("vision_node") {}
    
    // const 保证外部查询状态时不会意外修改内部计数器
    int getFrameCount() const { return frame_count_; }
};
```

### 2. 继承

#### 核心思想
代码复用与功能扩展。一个类（派生类/子类）从另一个类（基类/父类）获取属性和方法。体现“is-a”关系。C++ 支持多重继承，但实际工程（尤其是 ROS2）中通常只使用公有单继承。

##### 1. 基本语法与公有继承
**功能**：派生类继承基类的公有和保护成员，保持原有访问权限。最常用。

```cpp
# 示例：基本继承
class Animal { // 基类
public:
    void eat() { std::cout << "Eating..." << std::endl; }
};

// public 继承：基类的 public 成员在派生类中依然是 public
class Dog : public Animal { 
public:
    void bark() { std::cout << "Woof!" << std::endl; }
};

int main() {
    Dog d;
    d.eat();  // ✅ 继承自基类
    d.bark(); // ✅ 派生类自己的方法
    return 0;
}
```

##### 2. 三种继承方式与访问权限
**功能**：`public` 保持原权限，`protected` 降为保护，`private` 降为私有。日常开发中 99% 都是 `public` 继承。

```cpp
# 示例：继承方式对权限的影响
class Base {
public:
    int a;      // public
protected:
    int b;      // protected
private:
    int c;      // private（派生类永远不可直接访问）
};

class PubDerived : public Base {
    // a: public, b: protected, c: 不可访问
};

class ProtDerived : protected Base {
    // a: protected, b: protected, c: 不可访问
};

class PrivDerived : private Base {
    // a: private, b: private, c: 不可访问
};
```

##### 3. 构造函数与析构函数的调用顺序
**功能**：基类构造 -> 派生类构造 -> 派生类析构 -> 基类析构。派生类构造函数必须调用基类构造函数。

```cpp
# 示例：构造与析构顺序
class Base {
public:
    Base() { std::cout << "Base constructed\n"; }
    ~Base() { std::cout << "Base destroyed\n"; }
};

class Derived : public Base {
public:
    // 在初始化列表中显式调用基类构造函数
    Derived() : Base() { std::cout << "Derived constructed\n"; } 
    ~Derived() { std::cout << "Derived destroyed\n"; }
};

int main() {
    Derived d;
    // 输出顺序：Base constructed -> Derived constructed
    // 退出时：Derived destroyed -> Base destroyed
    return 0;
}
```

##### 4. 函数隐藏与 `using` 恢复
**功能**：派生类定义与基类同名函数，会隐藏基类所有同名重载函数。用 `using` 可以把基类的重载函数重新引入派生类作用域。

```cpp
# 示例：函数隐藏与 using
class Base {
public:
    void func() { std::cout << "Base::func()\n"; }
    void func(int x) { std::cout << "Base::func(int)\n"; }
};

class Derived : public Base {
public:
    using Base::func; // 把基类的所有 func 重载引入
    void func(double x) { std::cout << "Derived::func(double)\n"; }
};

int main() {
    Derived d;
    d.func();      // ✅ 如果不加 using，这里会报错
    d.func(10);    // ✅ 调用 Base::func(int)
    return 0;
}
```

##### 5. 阻止继承：`final`
**功能**：C++11 引入，加在类名后，禁止其他类继承此类。

```cpp
# 示例：final 阻止继承
class Base final { // 禁止被继承
public:
    void run() {}
};

// class Derived : public Base {}; // ❌ 编译报错
```

##### 6. 多重继承与虚继承（了解即可，ROS2 中极少用）
**功能**：继承多个基类。若多个基类继承自同一个祖先，会产生菱形继承，此时必须用 `virtual` 虚继承防止成员冲突。

```cpp
# 示例：菱形继承与虚继承
class A { public: int data; };
class B : virtual public A {}; // 虚继承
class C : virtual public A {}; // 虚继承
class D : public B, public C {}; // 只保留一份 A 的成员

int main() {
    D d;
    d.data = 10; // ✅ 如果没有 virtual，这里会报“二义性”错误
    return 0;
}
```

---

#### 🔗 结合 ROS2：继承如何用？

##### 场景 1：ROS2 节点必须公有继承 `rclcpp::Node`
每一个 ROS2 节点类都必须继承自 `rclcpp::Node`。派生类的构造函数必须在初始化列表中调用基类构造函数。

```cpp
# 示例：ROS2 节点继承
#include <rclcpp/rclcpp.hpp>

// public 继承基类 Node
class VisionNode : public rclcpp::Node {
public:
    // 初始化列表中调用基类 Node 的构造函数，传入节点名
    VisionNode() : Node("vision_node") { 
        RCLCPP_INFO(this->get_logger(), "Node initialized");
    }
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<VisionNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

##### 场景 2：基于继承实现视觉算法插件
使用继承和多态配合，定义一个视觉算法基类，然后让不同的视觉算法（YOLO、传统滤波等）去继承它，实现插件化架构。

```cpp
# 示例：视觉算法基类与派生
class VisionAlgorithm {
public:
    virtual void initialize() = 0;
    virtual cv::Mat process(const cv::Mat& input) = 0;
    virtual ~VisionAlgorithm() = default;
};

// 继承基类，实现具体逻辑
class YoloAlgorithm : public VisionAlgorithm {
public:
    void initialize() override { /* 加载权重 */ }
    cv::Mat process(const cv::Mat& input) override { /* YOLO 推理 */ return input; }
};

class TraditionalAlgorithm : public VisionAlgorithm {
public:
    void initialize() override { /* 初始化滤波参数 */ }
    cv::Mat process(const cv::Mat& input) override { /* 传统视觉处理 */ return input; }
};
```

##### 场景 3：ROS2 生命周期节点中的继承
ROS2 生命周期节点（`LifecycleNode`）继承自 `rclcpp::Node`。自定义的生命周期节点需要继承 `rclcpp_lifecycle::LifecycleNode`，并利用 `override` 重写基类的状态转换函数。

```cpp
# 示例：生命周期节点继承
#include <rclcpp_lifecycle/lifecycle_node.hpp>

class VisionLifecycleNode : public rclcpp_lifecycle::LifecycleNode {
public:
    VisionLifecycleNode() : LifecycleNode("vision_lifecycle") {}

    // 重写基类的虚函数
    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
    on_configure(const rclcpp_lifecycle::State&) override {
        return CallbackReturn::SUCCESS;
    }
};
```

##### 场景 4：ROS2 硬件抽象层（HAL）继承
在 ROS2 Control 中，真实硬件和仿真硬件都继承自同一个硬件接口基类（如 `SystemInterface`），主控程序只调用基类接口，无需关心底层是真实电机还是 Gazebo 仿真。

```cpp
# 示例：ROS2 硬件接口继承
#include <hardware_interface/system_interface.hpp>

class RealRobotHardware : public hardware_interface::SystemInterface {
public:
    hardware_interface::return_type read(const rclcpp::Time&, const rclcpp::Duration&) override {
        // 读取真实串口/CAN 数据
        return hardware_interface::return_type::OK;
    }
};

class SimRobotHardware : public hardware_interface::SystemInterface {
public:
    hardware_interface::return_type read(const rclcpp::Time&, const rclcpp::Duration&) override {
        // 从仿真器读取虚拟数据
        return hardware_interface::return_type::OK;
    }
};
```

### 3. 多态与虚函数

#### 核心思想
一个接口，多种形态。通过基类的指针或引用调用虚函数，程序在运行时根据对象的实际类型来决定调用哪个版本的函数，实现代码解耦和插件化。

##### 1. 虚函数与重写（`virtual` 与 `override`）
**功能**：基类加 `virtual` 允许被重写，派生类加 `override` 让编译器检查是否拼写错误。

```cpp
# 示例：虚函数与重写
class Shape {
public:
    // virtual 关键字告诉编译器，这个函数允许派生类重写
    virtual void draw() const { std::cout << "Shape" << std::endl; }
};

class Circle : public Shape {
public:
    // override 显式声明重写，若函数名拼错编译器直接报错（强烈建议加）
    void draw() const override { std::cout << "Circle" << std::endl; }
};
```

##### 2. 通过基类指针或引用触发多态
**功能**：必须使用指针或引用才能触发动态绑定，直接赋值对象会触发“对象切片”，导致多态失效。

```cpp
# 示例：指针与引用触发多态
int main() {
    Circle c;
    Shape* ptr = &c;    // 基类指针指向派生类对象
    Shape& ref = c;     // 基类引用绑定派生类对象
    
    ptr->draw();        // 输出 Circle（动态绑定）
    ref.draw();         // 输出 Circle（动态绑定）
    
    Shape s = c;        // ❌ 对象切片：派生类特有部分被切掉
    s.draw();           // 输出 Shape（多态失效，调用了基类版本）
    return 0;
}
```

##### 3. 虚析构函数（内存安全必须掌握）
**功能**：当基类指针指向派生类对象并执行 `delete` 时，保证派生类的析构函数被正确调用。

```cpp
# 示例：虚析构函数防内存泄漏
class Base {
public:
    virtual ~Base() { std::cout << "Base destroyed" << std::endl; } // 必须加 virtual
};

class Derived : public Base {
public:
    ~Derived() { std::cout << "Derived destroyed" << std::endl; }
};

int main() {
    Base* ptr = new Derived();
    delete ptr; // ✅ 先调用 Derived 析构，再调用 Base 析构，内存安全
    return 0;
}
```
**原则**：只要类中有一个虚函数，就必须把析构函数也写成 `virtual`。

##### 4. 纯虚函数与抽象类
**功能**：`= 0` 声明纯虚函数，含有纯虚函数的类叫抽象类，不能实例化，强制子类实现接口。

```cpp
# 示例：抽象类定义接口
class VisionBase {
public:
    virtual void process() = 0; // 纯虚函数，没有函数体，只定义规范
    virtual ~VisionBase() = default;
};

class YoloVision : public VisionBase {
public:
    void process() override { /* YOLO 推理逻辑 */ }
};

int main() {
    // VisionBase b; // ❌ 编译报错，抽象类不能实例化
    std::unique_ptr<VisionBase> algo = std::make_unique<YoloVision>();
    algo->process(); // 调用 YoloVision 的实现
    return 0;
}
```

##### 5. `final` 关键字（C++11）
**功能**：阻止类被继承，或阻止虚函数被重写。

```cpp
# 示例：final 修饰函数与类
class Base {
public:
    virtual void run() final { /* 禁止派生类重写此函数 */ }
};

class Derived final : public Base { // 禁止其他类继承 Derived
    // void run() override {} // ❌ 报错，无法重写 final 函数
};
```

##### 6. 动态绑定底层原理（V-Table）
**功能**：对象内存头部包含一个虚函数指针（V-Ptr），指向该类的虚函数表（V-Table）。查表决定调用哪个函数。

```cpp
# 示例：无需手写，编译器自动生成 V-Table
// 只要类有 virtual 函数，编译器就会为该类创建一张静态的虚函数表
// 每个对象中会隐式增加一个指针（V-Ptr），指向这张表
// 运行时通过 ptr 找到对象 -> 找到 V-Ptr -> 找到 V-Table -> 查表执行对应函数
```

---

#### 🔗 结合 ROS2：多态（虚函数）如何用？

##### 场景 1：视觉算法插件化（抽象类实践）
在视觉开发中，你可能需要随时切换 YOLO、传统滤波、轻量级网络等不同算法。多态可以完美解耦主程序与具体算法。

```cpp
# 示例：ROS2 视觉算法切换
#include <rclcpp/rclcpp.hpp>
#include <memory>

class VisionAlgorithm {
public:
    virtual void initialize() = 0; // 纯虚函数，规定必须实现
    virtual cv::Mat process(const cv::Mat& input) = 0;
    virtual ~VisionAlgorithm() = default;
};

class VisionNode : public rclcpp::Node {
private:
    std::unique_ptr<VisionAlgorithm> algorithm_; // 基类指针持有算法
public:
    VisionNode() : Node("vision_node") {
        // 假设根据参数动态选择算法
        std::string algo_type = this->declare_parameter("algorithm", "yolo");
        if (algo_type == "yolo") {
            algorithm_ = std::make_unique<YoloAlgorithm>();
        } else {
            algorithm_ = std::make_unique<TraditionalAlgorithm>();
        }
        algorithm_->initialize();
    }
};
```

##### 场景 2：ROS2 生命周期节点（Lifecycle Node）
ROS2 的生命周期节点（`rclcpp_lifecycle::LifecycleNode`）底层大量使用了虚函数。用户通过重写基类的虚函数来实现状态转换。

```cpp
# 示例：生命周期节点重写虚函数
#include <rclcpp_lifecycle/lifecycle_node.hpp>

class VisionLifecycleNode : public rclcpp_lifecycle::LifecycleNode {
public:
    VisionLifecycleNode() : LifecycleNode("vision_lifecycle") {}

    // 重写基类的虚函数，规定配置状态下该做什么
    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
    on_configure(const rclcpp_lifecycle::State&) override {
        // 初始化相机、加载标定参数
        return CallbackReturn::SUCCESS;
    }

    rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
    on_activate(const rclcpp_lifecycle::State&) override {
        // 激活发布者，开始处理图像
        return CallbackReturn::SUCCESS;
    }
};
```

##### 场景 3：智能指针配合虚析构函数（防止内存泄漏）
ROS2 中节点、算法模块均使用智能指针管理。必须确保基类有虚析构函数，否则 `std::shared_ptr<Base>` 析构派生类对象时会资源泄漏。

```cpp
# 示例：ROS2 中使用智能指针管理多态对象
class BaseSensor {
public:
    virtual ~BaseSensor() = default; // 虚析构，保证派生类资源被释放
};

class CameraSensor : public BaseSensor {
public:
    ~CameraSensor() { /* 关闭相机、释放 SDK 内存 */ }
};

// 在 ROS2 中使用
std::shared_ptr<BaseSensor> sensor = std::make_shared<CameraSensor>();
// sensor 超出作用域时，会正确调用 CameraSensor 的析构函数
```

##### 场景 4：硬件抽象层（HAL）
ROS2 Control 框架中，所有硬件驱动（真实电机、仿真电机）都继承自 `hardware_interface::SystemInterface`。开发者只需重写 `read()` 和 `write()` 等虚函数。

```cpp
# 示例：ROS2 硬件接口多态
#include <hardware_interface/system_interface.hpp>

class MyRobotHardware : public hardware_interface::SystemInterface {
public:
    // 重写虚函数，实现具体的读写逻辑
    hardware_interface::return_type read(const rclcpp::Time&, const rclcpp::Duration&) override {
        // 读取真实传感器数据
        return hardware_interface::return_type::OK;
    }
};
```

### 4. 接口与抽象类

#### 核心思想
接口只规定“能做什么”，不关心“怎么做”。在 C++ 中，接口通过**纯虚函数**（`= 0`）的抽象类来实现。它强制派生类遵守契约，是实现模块解耦、插件化架构的核心工具。

##### 1. 纯虚函数与抽象类定义
**功能**：声明没有实现的函数，含有纯虚函数的类即为抽象类。

```cpp
# 示例：定义接口
class VisionBase {
public:
    // 纯虚函数：末尾的 = 0 表示只定义规范，不提供实现
    virtual void initialize() = 0; 
    virtual cv::Mat process(const cv::Mat& input) = 0;
};
```

##### 2. 抽象类不能实例化
**功能**：抽象类只能作为基类被继承，不能直接创建对象。

```cpp
# 示例：禁止实例化抽象类
int main() {
    // VisionBase base; // ❌ 编译报错，抽象类不能实例化
    VisionBase* ptr;    // ✅ 合法，可以定义基类指针
    return 0;
}
```

##### 3. 强制派生类实现所有纯虚函数
**功能**：派生类必须实现接口中的所有纯虚函数，否则派生类也会变成抽象类，依然无法实例化。

```cpp
# 示例：派生类实现接口
class YoloVision : public VisionBase {
public:
    // 重写并实现纯虚函数
    void initialize() override { /* 加载 YOLO 权重 */ }
    cv::Mat process(const cv::Mat& input) override { /* 推理 */ return input; }
};

int main() {
    YoloVision yolo; // ✅ 合法，所有纯虚函数已实现
    return 0;
}
```

##### 4. 接口必须包含虚析构函数
**功能**：确保通过基类指针删除派生类对象时，派生类的析构函数能被正确调用，防止内存泄漏。

```cpp
# 示例：虚析构函数
class VisionBase {
public:
    virtual void process() = 0;
    // 接口必须提供虚析构函数
    virtual ~VisionBase() = default; 
};

// 使用智能指针管理，超出作用域时安全释放派生类资源
std::unique_ptr<VisionBase> algo = std::make_unique<YoloVision>();
```

##### 5. 多重接口继承（C++ 独有）
**功能**：一个类可以继承多个接口，从而具备多种行为规范，这是 C++ 模拟“多接口实现”的方式。

```cpp
# 示例：多重接口继承
class Serializable {
public:
    virtual std::string serialize() = 0;
    virtual ~Serializable() = default;
};

class Loggable {
public:
    virtual void log() = 0;
    virtual ~Loggable() = default;
};

// 同时继承两个接口，必须实现所有纯虚函数
class VisionNode : public Serializable, public Loggable {
public:
    std::string serialize() override { return "data"; }
    void log() override { /* 记录日志 */ }
};
```

---

#### 🔗 结合 ROS2：接口（抽象类）如何用？

##### 场景 1：视觉算法插件化（核心场景）
在机器人视觉开发中，经常需要切换不同的视觉算法（如 YOLO、传统 CV、轻量级网络）。通过接口可以实现完全解耦，主程序不需要知道具体使用的是哪个算法。

```cpp
# 示例：基于接口的视觉算法切换
#include <rclcpp/rclcpp.hpp>
#include <memory>

class VisionAlgorithm {
public:
    virtual void initialize() = 0;
    virtual cv::Mat process(const cv::Mat& input) = 0;
    virtual ~VisionAlgorithm() = default;
};

class VisionNode : public rclcpp::Node {
private:
    std::unique_ptr<VisionAlgorithm> algorithm_; // 持有接口指针
public:
    VisionNode() : Node("vision_node") {
        // 根据 ROS2 参数动态选择具体算法
        std::string algo_type = this->declare_parameter("algorithm", "yolo");
        if (algo_type == "yolo") {
            algorithm_ = std::make_unique<YoloAlgorithm>();
        } else {
            algorithm_ = std::make_unique<TraditionalAlgorithm>();
        }
        algorithm_->initialize(); // 多态调用，统一接口
    }
};
```

##### 场景 2：ROS2 硬件抽象层（HAL）
ROS2 Control 框架中，所有的硬件接口（真实电机、Gazebo 仿真、Isaac Sim 仿真）都继承自抽象类 `hardware_interface::SystemInterface`。主控程序只面向接口编程，完全忽略底层硬件差异。

```cpp
# 示例：ROS2 硬件接口（抽象基类）
#include <hardware_interface/system_interface.hpp>

class RealRobotHardware : public hardware_interface::SystemInterface {
public:
    // 实现基类的纯虚函数，读取真实串口/CAN数据
    hardware_interface::return_type read(const rclcpp::Time&, const rclcpp::Duration&) override {
        return hardware_interface::return_type::OK;
    }
};
// ROS2 控制管理器只需要持有 SystemInterface* 指针，即可操作所有硬件
```

##### 场景 3：自定义视觉消息转换器接口
在 ROS2 中处理不同的相机厂商（海康、大恒、USB相机）时，可以定义一个通用的 `CameraDriver` 接口，统一将不同格式的图像转为 ROS2 的 `sensor_msgs::msg::Image`。

```cpp
# 示例：通用相机驱动接口
class CameraDriver {
public:
    virtual bool open() = 0;
    virtual bool capture(cv::Mat& frame) = 0;
    virtual void close() = 0;
    virtual ~CameraDriver() = default;
};

class HikCamera : public CameraDriver {
public:
    bool open() override { /* 调用海康SDK */ return true; }
    bool capture(cv::Mat& frame) override { /* 取流 */ return true; }
    void close() override { /* 释放资源 */ }
};
```

##### 场景 4：生命周期节点回调接口
ROS2 生命周期节点中的 `on_configure`、`on_activate`、`on_deactivate` 等函数，本质上就是基类 `rclcpp_lifecycle::LifecycleNode` 提供的虚函数接口。开发者通过重写它们，将自定义逻辑注入到 ROS2 标准的状态机中。

```cpp
# 示例：重写 ROS2 生命周期接口
rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
on_configure(const rclcpp_lifecycle::State&) override {
    // 实现自己的配置逻辑，返回 SUCCESS 或 FAILURE
    return CallbackReturn::SUCCESS;
}
```

## 三、泛型与程序健壮性

本节介绍如何编写与具体类型解耦的代码，以及如何通过异常处理和文件流提高程序的复用性与可靠性。

### 1. 模板

#### 核心思想
泛型编程，编写与具体数据类型无关的代码。一套代码骨架，适用于多种数据类型。ROS2 的发布者、订阅者、消息容器全部依赖模板实现。

##### 1. 函数模板
**功能**：定义一个通用的函数骨架，编译器根据传入参数的类型自动生成对应的具体函数。

```cpp
# 示例：函数模板基础
// template <typename T> 声明一个通用类型 T
template <typename T>
T maxValue(T a, T b) {
    return (a > b) ? a : b;
}

int main() {
    int i = maxValue(10, 20);       // 编译器自动推导 T 为 int
    double d = maxValue(3.14, 2.71); // 编译器自动推导 T 为 double
    return 0;
}
```

##### 2. 类模板
**功能**：定义一个通用的类骨架，实例化时指定具体类型。

```cpp
# 示例：类模板基础
template <typename T>
class Box {
private:
    T content;
public:
    void set(T val) { content = val; }
    T get() { return content; }
};

int main() {
    Box<int> intBox;      // 指定 T 为 int
    intBox.set(10);
    
    Box<std::string> strBox; // 指定 T 为 std::string
    strBox.set("hello");
    return 0;
}
```

##### 3. 多个模板参数
**功能**：模板可以接受多个类型参数，用逗号分隔。

```cpp
# 示例：多类型模板
template <typename KeyType, typename ValueType>
class Pair {
public:
    KeyType key;
    ValueType value;
};

int main() {
    Pair<int, std::string> p; // KeyType=int, ValueType=std::string
    p.key = 1;
    p.value = "one";
    return 0;
}
```

##### 4. 非类型模板参数
**功能**：模板参数不只是类型，还可以是编译期常量（整数、指针等）。

```cpp
# 示例：非类型模板参数
template <typename T, int Size>
class FixedArray {
private:
    T data[Size]; // 数组大小由编译期常量决定
public:
    int size() const { return Size; }
};

int main() {
    FixedArray<int, 5> arr; // 创建大小为 5 的 int 数组
    return 0;
}
```

##### 5. 模板特化
**功能**：为特定的类型提供特殊实现，覆盖通用模板的逻辑。

```cpp
# 示例：全特化
template <typename T>
void print(T val) { std::cout << "General: " << val << std::endl; }

// 针对 bool 类型的特化版本
template <>
void print<bool>(bool val) { std::cout << "Bool: " << (val ? "true" : "false") << std::endl; }
```

##### 6. 可变参数模板（C++11）
**功能**：接受任意数量和类型的参数，是 C++11 泛型编程的高级特性。

```cpp
# 示例：可变参数模板基础
template <typename... Args>
void printAll(Args... args) {
    // 递归展开参数包（C++17 后可用折叠表达式简化）
    (std::cout << ... << args) << std::endl; // C++17 折叠表达式
}

int main() {
    printAll(1, 2.5, "hello"); // 输出 12.5hello
    return 0;
}
```

---

#### 🔗 结合 ROS2：模板如何用？

##### 场景 1：创建发布者与订阅者
ROS2 最核心的 API `create_publisher<T>` 和 `create_subscription<T>` 全部是函数模板，`T` 就是消息类型。

```cpp
# 示例：ROS2 发布者与订阅者模板
#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>

class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // create_publisher<消息类型>(话题名, QoS)
        pub_ = this->create_publisher<sensor_msgs::msg::Image>("image_topic", 10);
        
        // create_subscription<消息类型>(话题名, QoS, 回调)
        sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "input_topic", 10, std::bind(&VisionNode::callback, this, std::placeholders::_1));
    }
private:
    void callback(const sensor_msgs::msg::Image::SharedPtr msg) { /* 处理图像 */ }
    // 模板实例化后的智能指针类型
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr pub_;
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

##### 场景 2：自定义泛型视觉处理器
在开发视觉模块时，你可以写一个模板类，让它既能处理 `cv::Mat` 图像，也能处理 `pcl::PointCloud` 点云。

```cpp
# 示例：泛型视觉处理类
template <typename DataType>
class VisionProcessor {
public:
    void process(const DataType& input) {
        // 通用处理逻辑
    }
};

int main() {
    VisionProcessor<cv::Mat> img_processor;
    VisionProcessor<pcl::PointCloud<pcl::PointXYZ>> cloud_processor;
    return 0;
}
```

##### 场景 3：OpenCV 中的模板应用
OpenCV 大量使用模板。例如 `cv::Point_<T>`、`cv::Rect_<T>`、`cv::Mat_<T>`。在 ROS2 中处理图像坐标时，模板让代码更加灵活。

```cpp
# 示例：OpenCV 模板类
cv::Point2i p_int(10, 20);    // 整数坐标
cv::Point2f p_float(10.5, 20.5); // 浮点坐标

// 在 ROS2 中发布检测结果时，常用 cv::Point2f
std::vector<cv::Point2f> corners; // 模板实例化为 float 类型的点
```

##### 场景 4：通用数据记录器
在机器人调试时，你可能需要记录不同类型的数据（图像、点云、IMU），可以用模板写一个通用的记录工具。

```cpp
# 示例：通用数据记录器
template <typename MsgType>
class DataLogger {
public:
    void log(const MsgType& msg, const std::string& topic) {
        // 将消息序列化并保存到文件
    }
};

int main() {
    DataLogger<sensor_msgs::msg::Image> img_logger;
    DataLogger<sensor_msgs::msg::Imu> imu_logger;
    return 0;
}
```

### 2. 异常处理

#### 核心思想
将正常业务逻辑与错误处理逻辑分离。C 语言用返回值或 `errno` 层层传递错误，C++ 用 `try-catch-throw` 在发生错误时直接中断当前流程，向上层寻找捕获点。这是一种强制性的错误处理机制。

##### 1. 抛出异常：`throw`
**功能**：当检测到无法处理的错误时，抛出异常对象。强烈建议抛出对象（携带上下文），而不是基本数据类型。

```cpp
# 示例：抛出异常
#include <stdexcept>

void processImage(int width, int height) {
    if (width <= 0 || height <= 0) {
        // 抛出一个 std::invalid_argument 对象，携带错误信息
        throw std::invalid_argument("图像尺寸无效");
    }
}
```

##### 2. 捕获异常：`try-catch`
**功能**：划定危险区域，捕获并处理特定类型的异常。catch 块按顺序匹配，建议捕获 `const` 引用。

```cpp
# 示例：捕获异常
int main() {
    try {
        processImage(-1, 480); // 抛出异常
    } catch (const std::invalid_argument& e) { // 捕获类型匹配
        std::cerr << "参数错误: " << e.what() << std::endl;
    } catch (const std::exception& e) { // 兜底捕获所有标准异常
        std::cerr << "未知错误: " << e.what() << std::endl;
    }
    return 0;
}
```

##### 3. 捕获所有异常：`catch(...)`
**功能**：捕获任何类型的异常，通常作为最后的防线。无法获取异常具体信息。

```cpp
# 示例：捕获所有异常
try {
    // 危险代码
} catch (...) {
    std::cerr << "发生了未知异常" << std::endl;
}
```

##### 4. 标准异常体系（`<stdexcept>`）
**功能**：C++ 标准库提供了一系列异常类，均继承自 `std::exception`。

```cpp
# 示例：常用标准异常
std::runtime_error("运行时错误");       // 运行期才能检测到的错误（如相机掉线）
std::invalid_argument("无效参数");     // 参数非法（如空图像）
std::out_of_range("越界访问");         // 越界（如 vector::at 越界）
std::bad_alloc();                      // 内存分配失败（new 抛出）
```

##### 5. 自定义异常类
**功能**：继承 `std::exception` 或 `std::runtime_error`，重写 `what()` 方法，携带更详细的业务信息。

```cpp
# 示例：自定义视觉异常
#include <stdexcept>
#include <string>

class VisionException : public std::runtime_error {
public:
    // 调用父类构造函数，传入错误信息
    VisionException(const std::string& msg) : std::runtime_error(msg) {}
};

// 使用
try {
    throw VisionException("相机初始化失败，请检查USB连接");
} catch (const VisionException& e) {
    std::cerr << e.what() << std::endl; // 输出自定义的错误信息
}
```

##### 6. 异常安全与 RAII（栈展开）
**功能**：当异常被抛出时，局部对象（包括智能指针、锁）的析构函数会被自动调用，确保资源不泄漏。

```cpp
# 示例：栈展开自动释放资源
void process() {
    std::shared_ptr<int> ptr = std::make_shared<int>(10); // 智能指针
    throw std::runtime_error("处理失败"); // 抛出异常
    // 函数退出，ptr 的析构函数自动被调用，内存被释放
}
```

##### 7. `noexcept` 关键字（C++11）
**功能**：声明函数不会抛出异常。如果函数内部真的抛出了异常，程序会直接调用 `std::terminate()` 终止。

```cpp
# 示例：noexcept 声明
void safeFunction() noexcept { // 承诺不抛出异常
    // 移动构造函数和析构函数通常声明为 noexcept，以保证性能
}
```

---

#### 🔗 结合 ROS2：异常处理如何用？

##### 场景 1：保护 ROS2 回调函数（防止节点崩溃）
ROS2 的执行器（Executor）如果在回调函数中遇到未捕获的异常，会直接终止整个节点进程。必须在回调中加 `try-catch`。

```cpp
# 示例：订阅回调中的异常保护
void imageCallback(const sensor_msgs::msg::Image::SharedPtr msg) {
    try {
        cv::Mat img = cv_bridge::toCvShare(msg, "bgr8")->image;
        // 进行耗时的图像处理...
    } catch (const cv_bridge::Exception& e) {
        // 捕获 cv_bridge 转换异常
        RCLCPP_ERROR(this->get_logger(), "图像转换失败: %s", e.what());
    } catch (const std::exception& e) {
        // 捕获所有其他标准异常
        RCLCPP_ERROR(this->get_logger(), "处理图像时发生未知错误: %s", e.what());
    }
}
```

##### 场景 2：处理 OpenCV 专属异常（`cv::Exception`）
OpenCV 在矩阵尺寸不匹配、类型错误时会抛出 `cv::Exception`。视觉节点必须专门捕获它。

```cpp
# 示例：捕获 OpenCV 异常
try {
    cv::Mat result;
    cv::add(img1, img2, result); // 假设 img1 和 img2 尺寸不一致
} catch (const cv::Exception& e) {
    RCLCPP_ERROR(node->get_logger(), "OpenCV 错误: %s", e.what());
}
```

##### 场景 3：读取参数与标定文件的错误处理
读取 ROS2 参数或 YAML 标定文件时，如果键不存在或文件损坏，应抛出并捕获异常，而不是默默使用默认值。

```cpp
# 示例：读取相机标定文件
try {
    cv::FileStorage fs("camera_calib.yaml", cv::FileStorage::READ);
    if (!fs.isOpened()) {
        throw std::runtime_error("标定文件打开失败");
    }
    // 读取参数...
} catch (const std::exception& e) {
    RCLCPP_FATAL(node->get_logger(), "致命错误: %s", e.what());
    rclcpp::shutdown(); // 标定失败，优雅退出节点
}
```

##### 场景 4：ROS2 生命周期节点中的错误处理
在 ROS2 生命周期节点（Lifecycle Node）中，回调函数（如 `on_configure`）**不推荐直接抛出异常**，而是返回 `CallbackReturn::FAILURE` 来告知系统状态转换失败。

```cpp
# 示例：生命周期节点中的失败处理
rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn
on_configure(const rclcpp_lifecycle::State&) override {
    try {
        // 初始化相机、加载标定参数
        return CallbackReturn::SUCCESS;
    } catch (const std::exception& e) {
        RCLCPP_ERROR(this->get_logger(), "配置失败: %s", e.what());
        return CallbackReturn::FAILURE; // 通知系统配置失败，不抛出异常
    }
}
```

### 3. 文件和流

#### 核心思想
将文件抽象为“流”。C 语言使用 `FILE*` + `fopen/fclose`，C++ 使用 `fstream` 系列类。现代 C++ 依赖 RAII 机制，对象离开作用域时自动关闭文件，无需手动调用 `close()`。

##### 1. 包含头文件
**功能**：引入文件流相关的类。`<iostream>` 用于标准输入输出，`<fstream>` 用于文件操作。

```cpp
# 示例：包含头文件
#include <iostream> // std::cout, std::cerr
#include <fstream>  // std::ofstream, std::ifstream, std::fstream
```

##### 2. 写入文件：`std::ofstream`
**功能**：创建或打开文件，使用流插入运算符 `<<` 写入数据。默认模式为 `ios::out | ios::trunc`（覆盖并清空）。

```cpp
# 示例：写入文本文件
std::ofstream outfile("data.txt"); // 构造即打开，默认截断已有内容
outfile << "Hello ROS2" << std::endl; // 使用 << 写入
// 函数结束，outfile 析构，文件自动关闭 (RAII)
```

##### 3. 读取文件：`std::ifstream`
**功能**：打开文件，使用流提取运算符 `>>` 或 `std::getline` 读取数据。

```cpp
# 示例：读取文本文件
std::ifstream infile("data.txt");
if (infile.is_open()) { // 检查文件是否成功打开
    std::string line;
    // 使用 getline 读取整行（包括空格）
    while (std::getline(infile, line)) { 
        std::cout << line << std::endl;
    }
}
```

##### 4. 追加模式：`std::ios::app`
**功能**：在文件末尾追加内容，不覆盖原有数据。

```cpp
# 示例：追加写入日志
// 显式指定 app 模式
std::ofstream logfile("robot.log", std::ios::app); 
logfile << "New log entry" << std::endl;
```

##### 5. 二进制读写：`std::ios::binary` 与 `read/write`
**功能**：处理图像原始数据、AI 模型权重等二进制文件。必须指定 `ios::binary`。

```cpp
# 示例：二进制写入
std::ofstream out("model.bin", std::ios::binary);
float weights[100] = {1.0, 2.0};
// 强转为 char*，写入字节数
out.write(reinterpret_cast<const char*>(weights), sizeof(weights)); 
```

```cpp
# 示例：二进制读取
std::ifstream in("model.bin", std::ios::binary);
float buffer[100];
// 强转为 char*，读取字节数
in.read(reinterpret_cast<char*>(buffer), sizeof(buffer)); 
```

##### 6. 文件位置指针：`seekg` 与 `seekp`
**功能**：随机访问文件。`seekg` 移动读指针，`seekp` 移动写指针。

```cpp
# 示例：定位文件指针
std::ifstream infile("data.bin", std::ios::binary);
// 移动到文件末尾（获取文件大小）
infile.seekg(0, std::ios::end); 
// 获取当前指针位置（即文件字节数）
std::streampos file_size = infile.tellg(); 
// 重新定位到文件开头
infile.seekg(0, std::ios::beg); 
```

---

#### 🔗 结合 ROS2：文件和流如何用？

##### 场景 1：读取相机标定参数（YAML）
ROS2 视觉节点启动时，通常需要从 YAML 文件中读取相机内参和畸变系数。

```cpp
# 示例：读取标定文件
#include <opencv2/opencv.hpp>
#include <rclcpp/rclcpp.hpp>

void loadCalibration(const std::string& path) {
    try {
        cv::FileStorage fs(path, cv::FileStorage::READ);
        if (!fs.isOpened()) {
            throw std::runtime_error("标定文件打开失败: " + path);
        }
        cv::Mat camera_matrix;
        fs["camera_matrix"] >> camera_matrix; // OpenCV 底层封装了文件流
    } catch (const std::exception& e) {
        RCLCPP_ERROR(rclcpp::get_logger("vision"), "%s", e.what());
    }
}
```

##### 场景 2：记录运行日志
在机器人调试时，将视觉算法的耗时、识别结果写入日志文件，方便事后复盘。使用 `ios::app` 追加模式。

```cpp
# 示例：ROS2 运行日志记录
class VisionNode : public rclcpp::Node {
private:
    std::ofstream log_file_;
public:
    VisionNode() : Node("vision_node") {
        // 追加模式打开日志文件
        log_file_.open("vision_runtime.log", std::ios::app); 
    }
    
    void processCallback(const cv::Mat& img) {
        auto start = std::chrono::high_resolution_clock::now();
        // ... 处理图像 ...
        auto end = std::chrono::high_resolution_clock::now();
        
        // 写入耗时（毫秒）
        log_file_ << "Frame processed in " 
                  << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() 
                  << " ms" << std::endl;
    }
};
```

##### 场景 3：保存 AI 模型权重与加载
深度学习模型（如 ONNX、TensorRT 引擎）的权重文件通常是二进制格式。需要使用 `ios::binary` 和 `read/write`。

```cpp
# 示例：读取 TensorRT 引擎文件
std::vector<char> loadEngineFile(const std::string& engine_path) {
    std::ifstream file(engine_path, std::ios::binary | std::ios::ate); // ate：打开后定位到末尾
    if (!file.is_open()) {
        throw std::runtime_error("无法打开引擎文件");
    }
    // 获取文件大小（因为 ate 定位到了末尾）
    std::streamsize size = file.tellg(); 
    // 重新定位到开头准备读取
    file.seekg(0, std::ios::beg); 
    
    std::vector<char> buffer(size);
    file.read(buffer.data(), size); // 读取二进制数据到缓冲区
    return buffer;
}
```

##### 场景 4：保存视觉检测结果（CSV格式）
在视觉算法测试阶段，通常需要将检测框坐标、类别、置信度保存为 CSV 文件，供 Python 或 MATLAB 做后续分析。

```cpp
# 示例：保存检测结果到 CSV
void saveDetections(const std::vector<Detection>& detections) {
    std::ofstream csv("detections.csv", std::ios::app);
    for (const auto& det : detections) {
        // 使用逗号分隔写入
        csv << det.x << "," << det.y << "," 
            << det.w << "," << det.h << "," 
            << det.conf << "," << det.class_id << "\n";
    }
}
```

## 四、STL 容器与并发

最后一部分进入实际工程中最常用的动态数据容器和多线程工具，并结合 ROS 2 的节点执行、消息处理和共享数据场景理解它们的用途。

### 1. vector 容器

#### 核心思想
`std::vector` 是能动态自动扩容的数组，替代 C 语言中 `malloc/realloc` 手动管理的内存。它保证连续内存空间，支持 O(1) 随机访问，是 ROS2 中最常用的数据载体。

##### 1. 创建与初始化
**功能**：声明并初始化不同状态的 vector。

```cpp
# 示例：vector 初始化
std::vector<int> v1;             // 空 vector，size=0, capacity=0
std::vector<int> v2(5);          // 5个元素，默认初始化为0
std::vector<int> v3(5, 10);      // 5个元素，全部初始化为10
std::vector<int> v4 = {1, 2, 3}; // 列表初始化 (C++11)
```

##### 2. 添加元素
**功能**：向尾部添加元素。`emplace_back` 原地构造，性能优于 `push_back`（避免临时对象拷贝）。

```cpp
# 示例：添加元素
std::vector<int> v;
v.push_back(10);      // 传入对象，发生拷贝或移动
v.emplace_back(20);   // 直接在 vector 内存中构造，效率更高
```

##### 3. 访问元素
**功能**：获取 vector 中的元素。`[]` 不检查越界，`at()` 越界会抛出 `std::out_of_range` 异常。

```cpp
# 示例：访问元素
std::vector<int> v = {10, 20, 30};
int a = v[1];       // 20，不检查越界（快，但危险）
int b = v.at(1);    // 20，检查越界（安全，建议调试期使用）
int c = v.front();  // 10，第一个元素
int d = v.back();   // 30，最后一个元素
```

##### 4. 大小与容量
**功能**：`size` 是当前元素个数，`capacity` 是底层分配的内存空间。`reserve` 预分配内存，避免多次扩容拷贝。

```cpp
# 示例：容量管理
std::vector<int> v;
v.reserve(100);              // 预先分配100个元素的内存，capacity=100，size=0
v.push_back(1);              // size=1，无扩容开销
int s = v.size();            // 1
int c = v.capacity();        // 100
v.resize(5);                 // 改变 size 为5，多出的元素默认初始化为0
```

##### 5. 删除元素
**功能**：移除元素。`pop_back` 删除尾部，`erase` 删除指定位置，`clear` 清空所有。

```cpp
# 示例：删除元素
std::vector<int> v = {1, 2, 3, 4};
v.pop_back();                // 删除最后一个元素，v 变为 {1, 2, 3}
v.erase(v.begin() + 1);      // 删除索引为1的元素，v 变为 {1, 3}
v.clear();                   // 清空所有元素，size 变为 0，capacity 不变
```

##### 6. 遍历元素
**功能**：三种遍历方式。推荐使用基于范围的 for 循环（C++11）。

```cpp
# 示例：遍历 vector
std::vector<int> v = {1, 2, 3};

// 方式1：传统下标（C 风格）
for (size_t i = 0; i < v.size(); ++i) {
    std::cout << v[i] << std::endl;
}

// 方式2：迭代器
for (auto it = v.begin(); it != v.end(); ++it) {
    std::cout << *it << std::endl;
}

// 方式3：基于范围的 for（推荐，只读遍历）
for (const auto& x : v) {
    std::cout << x << std::endl;
}
```

##### 7. 在循环中安全删除元素
**功能**：遍历中删除元素时，`erase` 会返回下一个有效迭代器。

```cpp
# 示例：安全删除特定值
std::vector<int> v = {1, 2, 3, 2, 4};
for (auto it = v.begin(); it != v.end(); ) {
    if (*it == 2) {
        it = v.erase(it); // erase 返回被删元素的下一个位置
    } else {
        ++it;
    }
}
```

---

#### 🔗 结合 ROS2：vector 如何用？

##### 场景 1：处理 AI 模型的输出结果
深度学习模型（如 YOLO）输出的检测框通常是一组向量，ROS2 节点常用 `vector` 存储并转为 ROS2 自定义消息。

```cpp
# 示例：存储 AI 检测结果
struct Detection {
    float x, y, w, h, conf;
    int class_id;
};

std::vector<Detection> detections; // 存储一帧图像的所有目标
detections.push_back({100.0, 200.0, 50.0, 80.0, 0.95, 0}); // 存入结果
```

##### 场景 2：接收点云数据
点云数据量极大，使用 `vector` 配合 `reserve` 预分配内存，避免接收时频繁扩容。

```cpp
# 示例：接收点云数据
void pointCloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg) {
    std::vector<float> points;
    points.reserve(msg->width * msg->height); // 预分配，避免多次扩容
    // ... 解析点云并 push_back 到 points
}
```

##### 场景 3：传递 ROS2 参数
ROS2 允许参数为数组类型，接收时底层就是 `std::vector`。

```cpp
# 示例：读取 ROS2 数组参数
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // 声明一个字符串数组参数
        this->declare_parameter("camera_topics", std::vector<std::string>{"cam0", "cam1"});
        std::vector<std::string> topics;
        this->get_parameter("camera_topics", topics); // 读取为 vector
    }
};
```

##### 场景 4：避免 vector 扩容带来的迭代器失效
在 ROS2 回调中处理 vector 时，如果中途 `push_back` 导致扩容，之前的迭代器或指针会失效。

```cpp
# 示例：规避迭代器失效
std::vector<int> data = {1, 2, 3};
int* ptr = &data[0]; // 保存了底层指针
data.push_back(4);   // 触发扩容，内存搬家
// std::cout << *ptr; // ❌ 灾难！ptr 指向已被释放的旧内存

// ✅ 正确做法：提前 reserve，或者不用裸指针保存 vector 元素地址
```

### 2. 多线程

#### 核心思想
让程序同时执行多个任务。C 语言用 `pthread`，C++11 之后用 `std::thread`。ROS2 高度依赖多线程来处理传感器并发数据，单线程执行器会被耗时任务（如图像处理）阻塞。

##### 1. 创建线程：Lambda 表达式（首选）
**功能**：通过匿名函数创建线程，可以直接捕获上下文变量，最灵活。

```cpp
# 示例：使用 Lambda 创建线程
#include <thread>
#include <iostream>

int main() {
    int count = 5;
    // [count] 捕获外部变量，() 是线程函数参数列表
    std::thread t([count]() { 
        for (int i = 0; i < count; ++i) {
            std::cout << "Thread running: " << i << std::endl;
        }
    });
    t.join(); // 主线程阻塞等待 t 执行完毕
    return 0;
}
```

##### 2. 线程管理：`join()` vs `detach()`
**功能**：决定主线程与子线程的生命周期关系。

```cpp
# 示例：join 与 detach 的区别
std::thread t1([](){ /* 任务1 */ });
t1.join(); // 主线程等待 t1 结束（安全，推荐）

std::thread t2([](){ /* 任务2 */ });
t2.detach(); // 分离线程，主线程不再等待（危险，ROS2 严禁使用，极易导致段错误）
```
**注意**：如果 `std::thread` 对象销毁时既没有 `join()` 也没有 `detach()`，程序会直接调用 `std::terminate()` 崩溃。

##### 3. 引用传参：`std::ref`
**功能**：线程默认按值拷贝参数，如需传递引用必须用 `std::ref` 包装。

```cpp
# 示例：传递引用参数
#include <thread>
#include <iostream>

void increment(int& x) { ++x; }

int main() {
    int num = 0;
    // 如果不加 std::ref，会拷贝 num，原始 num 不会被修改
    std::thread t(increment, std::ref(num)); 
    t.join();
    std::cout << num << std::endl; // 输出 1
    return 0;
}
```

##### 4. 互斥量：`std::mutex` 与 `std::lock_guard`（RAII）
**功能**：保护共享资源，防止多个线程同时修改导致数据竞争（Data Race）。`lock_guard` 自动加锁/解锁，异常安全。

```cpp
# 示例：使用 lock_guard 保护共享数据
#include <mutex>
#include <thread>
#include <vector>

std::mutex mtx; // 全局互斥量
int shared_counter = 0;

void safe_increment() {
    // 构造时自动加锁，出作用域自动解锁（推荐）
    std::lock_guard<std::mutex> lock(mtx); 
    ++shared_counter; // 受保护的代码
}

int main() {
    std::thread t1(safe_increment);
    std::thread t2(safe_increment);
    t1.join(); t2.join();
    return 0;
}
```

##### 5. 原子操作：`std::atomic`
**功能**：对于简单的数值操作（自增、赋值），提供无锁的线程安全操作，性能远高于 mutex。

```cpp
# 示例：原子计数器
#include <atomic>
#include <thread>

std::atomic<int> frame_count(0); // 原子整型

void count_frame() {
    frame_count++; // 多线程安全的无锁自增
}

int main() {
    std::thread t1(count_frame);
    std::thread t2(count_frame);
    t1.join(); t2.join();
    return 0;
}
```

##### 6. 条件变量：`std::condition_variable`
**功能**：实现线程间的等待与通知，经典应用于生产者-消费者模型。必须配合 `std::unique_lock` 使用。

```cpp
# 示例：条件变量等待
#include <mutex>
#include <condition_variable>
#include <thread>

std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void worker() {
    std::unique_lock<std::mutex> lock(mtx); // unique_lock 支持手动解锁
    // wait 会释放锁并阻塞，直到 ready 变为 true
    cv.wait(lock, []{ return ready; }); 
    // 被唤醒后继续执行
}

void main_thread() {
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true; // 修改条件
    } // 解锁
    cv.notify_one(); // 唤醒一个等待的线程
}
```

##### 7. 异步任务：`std::async` 与 `std::future`
**功能**：比手动创建线程更高级的抽象，直接获取异步任务的返回值。

```cpp
# 示例：使用 async 获取异步结果
#include <future>
#include <iostream>

int heavy_compute() { return 42; }

int main() {
    // std::launch::async 强制创建新线程执行
    std::future<int> fut = std::async(std::launch::async, heavy_compute);
    // 主线程可以干别的事...
    int result = fut.get(); // 阻塞等待结果，获取返回值 42
    std::cout << result << std::endl;
    return 0;
}
```

---

#### 🔗 结合 ROS2：多线程如何用？

##### 场景 1：必须使用 `MultiThreadedExecutor`
ROS2 默认的 `rclcpp::spin()` 是单线程的。如果图像处理回调耗时 50ms，其他所有传感器回调都会被阻塞。必须使用多线程执行器。

```cpp
# 示例：ROS2 多线程执行器
#include <rclcpp/rclcpp.hpp>
#include <memory>

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    
    auto node = std::make_shared<rclcpp::Node>("vision_node");
    
    // 创建多线程执行器
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(node);
    executor.spin(); // 底层自动开启线程池并发执行回调
    
    rclcpp::shutdown();
    return 0;
}
```

##### 场景 2：回调组（Callback Groups）控制并发
即使使用了多线程执行器，默认情况下同一个节点的回调是互斥的（不能同时执行）。需要修改回调组为 `Reentrant` 才能并发。

```cpp
# 示例：设置可重入回调组
class VisionNode : public rclcpp::Node {
public:
    VisionNode() : Node("vision_node") {
        // 创建一个可重入回调组（允许不同回调同时执行）
        auto reentrant_group = this->create_callback_group(
            rclcpp::CallbackGroupType::Reentrant);
        
        rclcpp::SubscriptionOptions options;
        options.callback_group = reentrant_group;
        
        // 图像订阅者使用可重入回调组
        sub_ = this->create_subscription<sensor_msgs::msg::Image>(
            "image_topic", 10, 
            std::bind(&VisionNode::image_cb, this, std::placeholders::_1),
            options);
    }
private:
    void image_cb(const sensor_msgs::msg::Image::SharedPtr msg) { /* 耗时处理 */ }
    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr sub_;
};
```

##### 场景 3：共享数据的锁粒度控制（性能关键）
不要把耗时操作（如图像推理）放在锁里面，否则多线程退化为单线程。

```cpp
# 示例：锁粒度优化
std::mutex data_mtx;
cv::Mat shared_frame;

void process_callback(const sensor_msgs::msg::Image::SharedPtr msg) {
    cv::Mat local_frame;
    {
        // 只在拷贝数据时加锁，耗时极短
        std::lock_guard<std::mutex> lock(data_mtx);
        local_frame = cv_bridge::toCvCopy(msg)->image; 
    } // 立刻解锁
    
    // 在锁外面进行耗时的图像处理（深度学习推理等）
    cv::Mat result = heavy_inference(local_frame);
    
    {
        // 再次加锁，更新最终结果
        std::lock_guard<std::mutex> lock(data_mtx);
        shared_frame = result;
    }
}
```

##### 场景 4：避免在 ROS2 回调中死锁
如果在回调 A 中加了锁，然后等待回调 B 的结果，而回调 B 也需要同一把锁，就会直接死锁。多线程执行器下必须避免嵌套加锁。ROS2 推荐使用 `std::lock_guard` 划定严格的作用域来规避。
