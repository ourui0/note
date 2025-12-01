

# Programming in C++

http://www.tiobe.com/tiobe-index/

http://survey.stackoverflow.co/

http://www.stroustrup.com/

## language

特定的**字母表上**按照**一定的规则**（语法）形成的符号串的集合

语言三要素——语法、语义、语用

### BNF 的核心组成

BNF 主要由一系列**产生式规则** 组成。每条规则都像是一个定义，告诉我们如何构建一个更大的结构。

每条规则包含三个部分：

1. **非终结符**：用尖括号括起来的名称，例如 `<digit>`, `<expression>`。它表示一个语法类别或结构，可以被进一步分解。
2. **终结符**：是语言中实际的字符或字符串（词法单元），例如 `+`, `if`, `(`， `"hello"`。它们是语法树的“叶子”，无法再被分解。
3. **定义符号**：通常写成 `::=`，意思是“被定义为”或“由...组成”。

**运算符**：

- **`|`** ： 表示“或”。用于列出多个可能的选项。
- **连接**： 符号的简单排列表示“接着”，即顺序必须严格匹配。

### 一个简单的例子：定义整数

让我们用 BNF 来定义一个简单的无符号整数（例如 1, 123, 0）。

```bnf
<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<integer> ::= <digit> | <digit> <integer>
```

### BNF 的扩展：EBNF

原始的 BNF 非常基础，为了更方便地表示语法，人们创建了**扩展的巴科斯-瑙尔范式**。

EBNF 引入了额外的运算符，使规则更简洁：

- **`?`**： 可选元素。例如 `"+" <expression>?` 表示加号和一个可选的表达式。
- **`\*`**： 重复零次或多次。例如 `<digit>*` 表示零个或多个数字。
- **`+`**： 重复一次或多次。例如 `<digit>+` 表示至少一个数字（这直接定义了我们的 `<integer>`）。
- **`[ ]`**： 分组，常用于与 `|`, `?`, `*`, `+` 结合。

**使用 EBNF 重写上面的例子：**

ebnf

```
digit = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
integer = digit+ ; (* 使用 + 表示一个或多个数字 *)
expression = number
           | expression "+" expression
           | expression "*" expression
           | "(" expression ")" ;
```

*(注意：EBNF 中也常用 `=` 代替 `::=`)*

可以看到，`integer` 的定义变得异常简洁。

## 内联函数

内联函数是一种编译器优化技术，它的核心思想是：**在编译时，将函数调用语句直接替换为函数体本身的代码**。

### 一个简单的比喻：

- **普通函数调用**：就像你在读一本书，看到一个术语“光合作用”，下面写着“（详见附录A）”。你需要翻到书后的附录A去阅读定义，然后再翻回来继续读。这个过程有“跳转”的开销。
- **内联函数调用**：而内联函数则直接在这个术语“光合作用”的后面，用括号把附录A里的定义全文抄写一遍。这样你就不需要翻页了，阅读更流畅，但代价是这段定义文字重复出现了，使得当前页面变长了一点。

### 优点：主要目的是减少开销，提升性能

1. **消除函数调用开销**：每次调用普通函数，CPU都需要执行一系列操作：将返回地址、参数等压入栈（Stack），跳转到函数地址，执行函数代码，然后将结果返回，最后从栈中弹出数据并跳回调用处。对于非常小的函数，这个“准备工作”和“收尾工作”的开销可能比函数本身执行的开销还要大。内联函数直接省去了这些步骤。
2. **便于编译器优化**：因为代码被展开在调用处，编译器可以看到更大段的、连续的代码。这为编译器提供了更大的优化空间，例如**常量传播（Constant Propagation）**、**死代码消除（Dead Code Elimination）** 等优化可以更有效地进行。
   - *例子*：如果内联函数的一个参数是常量，编译器在展开后可以直接把这个常量代入计算，甚至直接算出结果。

### 缺点：不能滥用，否则会产生反效果

1. **代码膨胀（Code Bloat）**：这是内联函数最主要的缺点。如果一个函数很大又被多次调用，那么它的函数体会被复制很多次，导致最终编译出的可执行文件体积显著增大。这可能会降低CPU缓存（Cache）的命中率，反而导致性能下降。
2. **增加编译时间**：因为编译器需要处理并复制更多的代码。
3. **可能增加维护难度**：过度内联会使代码变得冗长，因为相同的逻辑分散在多个地方。
4. **对调试不友好**：调试器（Debugger）在处理内联函数时会比较困难，因为你可能无法像普通函数那样清晰地设置断点或查看调用栈。

### 使用

在C++中，主要有两种方式声明一个函数为内联函数：

1. **使用 `inline` 关键字**：
   在函数声明或定义前加上 `inline` 关键字。

   ```c++
   // 头文件 example.h
   #ifndef EXAMPLE_H
   #define EXAMPLE_H
   
   // 声明为内联函数
   inline int max(int a, int b) {
       return (a > b) ? a : b;
   }
   
   #endif
   ```

   

   **重要提示**：内联函数的定义（函数体）通常必须放在头文件（.h）中。因为编译时，编译器需要在每个调用它的源文件（.c）中看到它的完整定义才能进行“替换”。如果只放在某个源文件中，其他文件就无法内联它。

2. **在类定义内部直接定义函数**：
   在类内部直接实现的成员函数，会自动被视为建议内联的（但最终决定权仍在编译器）。

   ```c++
   class MyClass {
   public:
       // 构造函数在类内定义，默认为内联建议
       MyClass() : value(0) {}
   
       // Getter 函数在类内定义，默认为内联建议
       int getValue() const { return value; }
   
       // Setter 函数在类内定义，默认为内联建议
       void setValue(int v) { value = v; }
   
   private:
       int value;
   };
   ```

### 总结：何时使用内联函数？

遵循以下准则：

- **适合内联**：**小而频繁调用的函数**。通常是只有几行代码的“getter/setter”函数、简单的工具函数（如上面的 `max` 函数）。
- **不适合内联**：**大函数**（例如超过10行）、递归函数、虚函数（因为需要在运行时决定调用哪个函数，内联通常无法进行）。
- **核心原则**：**不要盲目使用内联**。首先应该编写清晰、可维护的代码，然后使用性能分析工具（Profiler）找出程序的性能瓶颈（Hotspots）。如果发现某个小函数的调用开销确实成为了瓶颈，再考虑将其内联。**基于性能分析数据来做优化，而不是凭感觉。**

## 作用域

### 为什么需要作用域？

1. **避免命名冲突**：允许在不同的上下文中使用相同的名字（例如，在不同的函数里都可以定义一个叫 `i` 的循环计数器），而不会相互干扰。
2. **数据封装与保护**：限制对变量的访问，防止程序的某些部分意外修改另一部分正在使用的数据，提高了程序的可靠性和安全性。
3. **管理内存生命周期**：与变量的生命周期密切相关。局部变量在离开作用域时会被自动销毁，从而释放内存。

### 主要类型（从常见到少见）

1. **局部作用域（块作用域）**

   - **在哪**： inside任何一对大括号 `{}` 里（比如函数、循环、if语句内部）。

   - **特点**： 在这里定义的变量（局部变量）只在当前 `{}` 内有效。括号结束，变量就被销毁。

   - **例子**：

     c++

     ```c++
     void func() {
         int x = 10; // x 的作用域开始
         if (true) {
             int y = 20; // y 只在这个if块里有效
         } // y 的作用域结束，被销毁
         // cout << y; // 错误！y 已经没了
     } // x 的作用域结束
     ```

     

2. **全局作用域**

   - **在哪**： 在所有函数和代码块**之外**。

   - **特点**： 在这里定义的变量（全局变量）在整个程序中都有效，任何函数都能使用它。

   - **例子**：

     c++

     ```c++
     #include <iostream>
     int globalVar = 50; // 全局变量，作用域开始
     
     void printIt() {
         std::cout << globalVar; // ✅ 任何函数都能访问
     }
     
     int main() {
         std::cout << globalVar; // ✅
         return 0;
     }
     // globalVar 的作用域到此文件末尾结束
     ```

     

3. **命名空间作用域**

   - **目的**： 用来管理和隔离全局名字，防止命名冲突。

   - **如何使用**： 用 `namespace` 定义，用 `::` 或 `using` 来访问。

   - **例子**：

     c++

     ```c++
     namespace MyStuff {
         int value = 100;
     }
     int main() {
         std::cout << MyStuff::value; // 用 :: 访问
         return 0;
     }
     ```

     

4. **类作用域**

   - **在哪**： 在 `class` 或 `struct` 的内部。

   - **特点**： 类的成员（变量和函数）属于类的作用域。需要通过类的对象（`.`）或类名（`::` for静态成员）来访问。

   - **例子**：

     ```c++
     class MyClass {
     public:
         int data; // 成员变量，在类作用域内
         void func() { } // 成员函数
     };
     int main() {
         MyClass obj;
         obj.data = 10; // 通过对象 . 访问
         obj.func();
         return 0;
     }
     ```

- **隐藏规则**： 内层作用域的变量会**遮盖**外层同名的变量。

  c++

  ```c++
  int x = 1; // 全局变量 x
  int main() {
      int x = 2; // 局部变量 x，遮盖了全局的 x
      cout << x; // 输出 2（使用的是局部变量）
      cout << ::x; // 输出 1（使用 :: 显式访问全局变量）
      return 0;
  }
  ```

## namespace（**命名空间**）

namespace 是一种作用域，用于将代码（如变量、函数、类）组织到逻辑组中，以防止**命名冲突**。相当于公司里的**部门**，以对**张三**，就有比如**“研发部的张三”**和**“销售部的张三”**。

**核心目的：解决全局命名空间污染问题。**

### 定义与使用

#### 1. 定义命名空间

使用 `namespace` 关键字来定义。

c++

```c++
namespace MyNamespace {
    // 可以包含变量、函数、类、嵌套命名空间等
    int value = 42;

    void myFunction() {
        // ... 函数实现
    }

    class MyClass {
        // ... 类定义
    };

    // 甚至可以嵌套
    namespace InnerNamespace {
        int innerValue = 100;
    }
}
```



#### 2. 使用命名空间中的成员

有几种方法来访问命名空间里的内容：

**a) 使用作用域解析运算符 `::`（最明确，最推荐）**
直接指明你要访问的成员属于哪个命名空间。

c++

```c++
int main() {
    std::cout << MyNamespace::value << std::endl; // 输出 42
    MyNamespace::myFunction();
    MyNamespace::MyClass obj;

    std::cout << MyNamespace::InnerNamespace::innerValue << std::endl; // 输出 100
    return 0;
}
```



**b) 使用 `using` 声明**
将某个特定的名称引入当前作用域，之后就可以直接使用它。

c++

```c++
int main() {
    using MyNamespace::value; // 声明：后面可以直接用 value
    using MyNamespace::myFunction; // 声明：后面可以直接用 myFunction

    std::cout << value << std::endl; // ✅ 不需要前缀了
    myFunction(); // ✅

    // MyClass obj; // ❌ 错误！没有对 MyClass 使用 using 声明
    MyNamespace::MyClass obj; // ✅ 仍需使用 ::
    return 0;
}
```



**c) 使用 `using namespace` 指令（慎用！）**
将整个命名空间的所有名称都引入当前作用域。**这是一种偷懒的方式，虽然方便，但容易重新引入命名冲突的风险，违背了使用命名空间的初衷。**

c++

```c++
// 在函数内部使用：只在该函数内生效
int main() {
    using namespace MyNamespace; // 引入整个 MyNamespace

    std::cout << value << std::endl; // ✅
    myFunction(); // ✅
    MyClass obj; // ✅

    return 0;
}

// 在全局使用：在整个文件内生效（非常不推荐！）
// using namespace MyNamespace;
```



**最佳实践：** 在头文件中**绝对不要**使用 `using namespace ...;`，在源文件中也**尽量限制在函数内部使用**，优先选择 `::` 和 `using` 声明。

### 总结

| 特性                           | 描述                   | 推荐度         |
| :----------------------------- | :--------------------- | :------------- |
| **`Namespace::member`**        | 最清晰，完全避免冲突   | ⭐⭐⭐⭐⭐ **首选** |
| **`using Namespace::member;`** | 对单个成员很方便       | ⭐⭐⭐⭐ **良好**  |
| **`using namespace Name;`**    | 方便但危险，易引起冲突 | ⭐ **尽量避免** |

## 引用

**引用是一个变量的别名（Alias）**。它为已存在的变量提供了另一个名字。一旦一个引用被初始化为某个变量，那么就可以通过这个引用名称来操作该变量，就像使用原变量名一样。

**核心思想：** 一个变量，两个名字。

### 基本语法

#### 1. 创建引用

使用 `&` 符号来声明引用。**注意：这里的 `&` 是类型标识的一部分，不是取地址运算符。**

c++

```c++
int main() {
    int original_var = 10;
    
    // 创建引用：语法是 `类型& 引用名 = 原变量名;`
    int& ref = original_var; // ref 现在是 original_var 的别名

    // 通过 ref 操作，就是在操作 original_var
    ref = 20; // 修改 ref 的值
    std::cout << original_var << std::endl; // 输出 20，original_var 也被改变了

    original_var = 30; // 修改 original_var
    std::cout << ref << std::endl; // 输出 30，ref 也跟着变了

    return 0;
}
```



#### 2. 关键特性

1. **必须初始化**：引用在创建时必须被初始化，指明它是哪个变量的别名。它不能像指针一样先声明为 `NULL` 再赋值。

   c++

   ```c++
   int& ref; // ❌ 错误！引用必须初始化
   int& ref = original_var; // ✅ 正确
   ```

   

2. **不可重新绑定**：一旦引用初始化指向某个变量，它就不能再成为另一个变量的别名。它“从一而终”。

   c++

   ```c++
   int a = 10;
   int b = 20;
   int& ref = a;
   ref = b; // 这行代码的意思不是让 ref 变成 b 的别名。
            // 而是将 b 的值（20）赋值给 ref 所引用的对象（a）。
            // 所以现在 a 的值变成了 20。
   ```

   

3. **没有空引用**：引用必须指向一个有效的对象，不能存在“空引用”（类似 `NULL` 指针的概念）。这使得引用比指针更安全。

### 应用

参数传递

```c++
c++
// 1. 按值传递（失败）
void swap_fail(int a, int b) {
    int temp = a;
    a = b;
    b = temp;
    // 这里交换的只是函数内部的副本，外面的变量没变
}

// 2. 按指针传递（C风格，有效但繁琐）
void swap_pointer(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

// 3. 按引用传递（C++风格，有效且简洁）✅
void swap_ref(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

int main() {
    int x = 5, y = 10;
    
    swap_fail(x, y);
    std::cout << x << ", " << y << std::endl; // 输出 5, 10，没变

    swap_pointer(&x, &y); // 需要传地址
    std::cout << x << ", " << y << std::endl; // 输出 10, 5，成功但麻烦

    swap_ref(x, y); // 直接传变量，语法清晰
    std::cout << x << ", " << y << std::endl; // 输出 5, 10，成功且方便

    return 0;
}
```

### 与指针对比

### 四、引用 vs. 指针 🥊

这是一个核心区别。引用通常被实现为一种“自动解引用的指针”，但语法和安全性上有很大不同。

| 特性         | **引用 (Reference)**                   | **指针 (Pointer)**                        |
| :----------- | :------------------------------------- | :---------------------------------------- |
| **语法**     | ⭐ 像普通变量一样操作，更简洁           | 🔄 需要使用 `*` 和 `&` 运算符，更复杂      |
| **初始化**   | ⚠️ **必须初始化**                       | ✅ 可以稍后初始化，甚至可以初始化为 `NULL` |
| **可重绑定** | 🔒 **不可以**，始终是同一变量的别名     | 🔄 **可以**，可以指向不同的变量            |
| **空值**     | 🚫 **不能为空**，必须指向有效对象       | ✅ 可以为 `nullptr`                        |
| **安全性**   | 🛡️ **更安全**，不存在空引用和野引用     | ☠️ 风险较高，可能产生空指针、野指针        |
| **内存操作** | 🎭 无法获取引用自身的地址（它就是别名） | 🔍 可以获取指针变量自身的地址              |

**简单比喻：** ✨

- **指针** 像是一张**名片** 📇，上面写着别人的地址。你可以换一张名片（指向不同的人），也可以有一张空名片（`NULL`）。
- **引用** 像是一个人的**外号** 🏷️。一旦这个外号给了某个人，它就一辈子跟着这个人，不能转给别人。而且一个人不能没有外号（必须初始化）。

### 其他类型的引用

1. **常量引用（const Reference）**：
   主要用于函数参数，表示函数不会通过这个引用修改值，如上面 `printStringEfficiently` 的例子。

2. **右值引用（Rvalue Reference）**：
   使用 `&&` 声明，是 C++11 引入的高级特性，用于实现**移动语义（Move Semantics）** 和**完美转发（Perfect Forwarding）**，能极大提升性能。这是更深入的话题。

   c++

   ```c++
   void handleValue(int&& rval_ref) {
       // 这个函数知道它接收的是一个“即将消亡”的临时值
       // 可以安全地“偷”它的资源，而不是拷贝
   }
   handleValue(42); // 可以传递临时值（右值）
   ```

   

### 总结

- **用途1（主要）**：作为函数参数（**按引用传递**），用于修改外部变量或**避免大型数据拷贝**（用 `const T&`）。
- **用途2**：作为函数返回值（返回引用允许函数调用出现在赋值语句左边，如 `cout <<` 或 `operator[]`）。
- **核心优势**：比指针更安全、语法更简洁清晰。
- **核心限制**：必须初始化且不能更换目标。


# C++面向对象编程（Part 2）详细总结与代码示例

## 一、面向对象基础

### 1.1 封装与信息隐藏

```c++
#include <iostream>
using namespace std;

class Stack {
private:
    int top;
    int buffer[100];  // 固定大小栈
    
public:
    Stack() { top = -1; }
    
    bool push(int i) {
        if (top == 99) {
            cout << "Stack is overflow.\n";
            return false;
        } else {
            top++;
            buffer[top] = i;
            return true;
        }
    }
    
    bool pop(int &i) {
        if (top == -1) {
            cout << "Stack is empty.\n";
            return false;
        } else {
            i = buffer[top];
            top--;
            return true;
        }
    }
};

int main() {
    Stack st1, st2;
    int x;
    
    st1.push(12);
    st1.pop(x);
    
    // st1.buffer[2] = -1;  // 错误：无法访问private成员
    return 0;
}
```

### 1.2 类定义与实现分离

**TDate.h**
```c++
class TDate {
public:
    void SetDate(int y, int m, int d);
    int IsLeapYear();
private:
    int year, month, day;
};
```

**TDate.c++**
```c++
#include "TDate.h"

void TDate::SetDate(int y, int m, int d) {
    year = y;
    month = m;
    day = d;
}

int TDate::IsLeapYear() {
    return (year%4 == 0 && year%100 != 0) || (year%400 == 0);
}
```

**内联实现**
```c++
class TDate {
public:
    void SetDate(int y, int m, int d) {
        year = y; month = m; day = d;
    }
    int IsLeapYear() {
        return (year%4 == 0 && year%100 != 0) || (year%400 == 0);
    }
private:
    int year, month, day;
};
```

## 二、构造函数与析构函数

### 2.1 构造函数类型

```c++
class MyClass {
private:
    int x, y;
    
public:
    // 默认构造函数
    MyClass() : x(0), y(0) {}
    
    // 带参构造函数
    MyClass(int x_val, int y_val) : x(x_val), y(y_val) {}
    
    // 拷贝构造函数
    MyClass(const MyClass& other) : x(other.x), y(other.y) {}
    
    // 委托构造函数
    MyClass(int val) : MyClass(val, val) {}  // 委托给双参数构造函数
    
    // =default 和 =delete
    MyClass() = default;                    // 使用编译器生成的默认构造函数
    MyClass(const MyClass&) = delete;       // 禁用拷贝构造
    
    // 析构函数
    ~MyClass() {
        cout << "Destructor called\n";
    }
};
```

### 2.2 成员初始化表

```c++
class ComplexClass {
private:
    const int const_member;
    int& ref_member;
    int normal_member;
    
public:
    // 必须使用成员初始化表初始化const和引用成员
    ComplexClass(int cm, int& rm, int nm) 
        : const_member(cm), ref_member(rm), normal_member(nm) {
        // 构造函数体
    }
};

class String {
private:
    char* str;
    int size;
    
public:
    // 使用成员初始化表提高效率
    String(int x) : size(x), str(new char[size]) {}
    
    ~String() { delete[] str; }
};
```

### 2.3 包含成员对象的类

```c++
class A {
private:
    int x, y;
public:
    A() { x = y = 0; }
    A(int x1, int y1) : x(x1), y(y1) {}
    void inc() { x++; y++; }
    void show() const { cout << "x=" << x << ", y=" << y << endl; }
};

class B {
private:
    int z;
    A a;  // 成员对象
    
public:
    B() : z(0) {}  // 调用A的默认构造函数
    
    // 错误：自定义拷贝构造函数但没有初始化成员对象a
    B(const B& b) { z = b.z; }  // a使用默认构造
    
    // 正确：在成员初始化表中初始化a
    B(const B& b) : a(b.a) { z = b.z; }
    
    void inc() { z++; a.inc(); }
    void show() const { 
        cout << "z=" << z << ", "; 
        a.show(); 
    }
};
```

## 三、拷贝控制

### 3.1 拷贝构造函数

```c++
class String {
private:
    char* p;
    
public:
    // 构造函数
    String(const char* str) {
        p = new char[strlen(str) + 1];
        strcpy(p, str);
    }
    
    // 拷贝构造函数（深拷贝）
    String(const String& s) {
        p = new char[strlen(s.p) + 1];
        strcpy(p, s.p);
        cout << "Deep copy performed\n";
    }
    
    // 析构函数
    ~String() { 
        delete[] p; 
    }
    
    const char* c_str() const { return p; }
};

void demonstrateShallowCopyProblem() {
    String s1("abcd");
    String s2 = s1;  // 调用拷贝构造函数
    
    // 如果没有深拷贝，s1和s2会指向同一内存
    // 析构时会导致双重释放错误
}
```

### 3.2 移动语义
#### 右值引用
在介绍移动语义之前我们需要介绍右值引用

首先我们需要介绍左值

##### 左值
左值有两个要素

+ 有名字、有地址的对象

+ 可以出现在赋值符号的左边

#### 右值
右值也有两个要素
+ 临时的、即将销毁的值
+ 不能出现在赋值号左边


#### 右值引用

用&&表示，专门用于绑定优右值

```c++
int&& rref = 42;           // 正确：绑定到右值
int&& rref2 = x;           // 错误：x是左值

string&& sref = getString();  // 正确：函数返回右值
```

#### 移动语义 -- 右值引用主要用法
```c++
class MyArray {
private:
    int size;
    int* arr;

public:
    // 默认构造函数
    MyArray() : size(0), arr(nullptr) {}
    
    // 带参构造函数
    MyArray(int sz) : size(sz), arr(new int[sz]) {
        for (int i = 0; i < size; i++) {
            arr[i] = i;
        }
    }
    
    // 拷贝构造函数
    MyArray(const MyArray& other) : size(other.size), arr(new int[other.size]) {
        for (int i = 0; i < size; i++) {
            arr[i] = other.arr[i];
        }
        cout << "Copy constructor\n";
    }
    
    // 移动构造函数
    MyArray(MyArray&& other) noexcept : size(other.size), arr(other.arr) {
        other.arr = nullptr;  // 置空原对象指针
        other.size = 0;
        cout << "Move constructor\n";
    }
    
    // 拷贝赋值运算符
    MyArray& operator=(const MyArray& other) {
        if (this != &other) {
            delete[] arr;
            size = other.size;
            arr = new int[size];
            for (int i = 0; i < size; i++) {
                arr[i] = other.arr[i];
            }
        }
        return *this;
    }
    
    // 移动赋值运算符
    MyArray& operator=(MyArray&& other) noexcept {
        if (this != &other) {
            delete[] arr;
            size = other.size;
            arr = other.arr;
            other.arr = nullptr;
            other.size = 0;
        }
        return *this;
    }
    
    ~MyArray() {
        delete[] arr;
    }
};

// 返回临时对象的函数
MyArray createArray(int size) {
    return MyArray(size);  // 返回临时对象（右值）
}

void demonstrateMoveSemantics() {
    MyArray arr1 = createArray(5);  // 可能调用移动构造函数
    
    MyArray arr2(10);
    MyArray arr3 = std::move(arr2);  // 显式移动
    
    MyArray arr4;
    arr4 = createArray(8);  // 移动赋值
}
```

## 四、动态内存管理

### 4.1 new/delete 操作符

```c++
class A {
private:
    int value;
public:
    A() : value(0) { cout << "A()\n"; }
    A(int v) : value(v) { cout << "A(" << v << ")\n"; }
    ~A() { cout << "~A()\n"; }
    void show() { cout << "value=" << value << endl; }
};

void demonstrateDynamicObjects() {
    A *p, *q;
    
    p = new A;           // 调用默认构造函数
    q = new A(10);       // 调用带参构造函数
    
    p->show();
    q->show();
    
    delete p;            // 调用析构函数
    delete q;            // 调用析构函数
}
```

### 4.2 动态数组

```c++
void demonstrateDynamicArrays() {
    // 动态基本类型数组
    int* intArray = new int[10];
    for (int i = 0; i < 10; i++) {
        intArray[i] = i;
    }
    delete[] intArray;
    
    // 动态对象数组（类必须有默认构造函数）
    A* objArray = new A[5];  // 调用5次默认构造函数
    delete[] objArray;       // 调用5次析构函数
}
```

### 4.3 二维动态数组

```c++
void demonstrate2DArray() {
    const int ROWS = 3;
    const int COLS = 4;
    
    // 创建二维数组
    int** matrix = new int*[ROWS];
    for (int i = 0; i < ROWS; i++) {
        matrix[i] = new int[COLS];
    }
    
    // 初始化
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            matrix[i][j] = i * COLS + j;
        }
    }
    
    // 释放内存
    for (int i = 0; i < ROWS; i++) {
        delete[] matrix[i];
    }
    delete[] matrix;
}
```

## 五、const成员

### 5.1 const成员变量

```c++
class ConstMemberDemo {
private:
    const int const_member;
    int normal_member;
    
public:
    // const成员必须在初始化列表中初始化
    ConstMemberDemo(int cm, int nm) : const_member(cm), normal_member(nm) {}
    
    // 错误：不能在构造函数体内初始化const成员
    // ConstMemberDemo(int cm, int nm) {
    //     const_member = cm;  // 错误！
    //     normal_member = nm; //可行但是不推荐
    // }
    
    void show() const {
        cout << "const_member=" << const_member 
             << ", normal_member=" << normal_member << endl;
    }
};
```

### 5.2 const成员函数

```c++
class ConstFunctionDemo {
private:
    int x, y;
    
public:
    ConstFunctionDemo(int x1, int y1) : x(x1), y(y1) {}
    
    // 非const成员函数
    void modify() { x++; y++; }
    
    // const成员函数 - 承诺不修改对象状态
    void show() const {
        cout << "x=" << x << ", y=" << y << endl;
        // x = 10;  // 错误：不能在const成员函数中修改成员
    }
    
    // const重载
    int getX() { return x; }           // 非const版本
    int getX() const { return x; }     // const版本
};

void demonstrateConstFunctions() {
    ConstFunctionDemo obj1(1, 2);
    const ConstFunctionDemo obj2(3, 4);
    
    obj1.modify();  // OK
    obj1.show();    // OK非const对象也可以调用const成员函数
    
    // obj2.modify();  // 错误：const对象不能调用非const成员函数
    obj2.show();      // OK：const对象可以调用const成员函数
}
```

### 5.3 mutable成员
mutable是一类特殊的成员，由其修饰的变量允许在const成员函数中修改
```c++
class Fib {
private:
    int n_;
    mutable bool cached = false;    // 缓存标志
    mutable int cache = 0;          // 缓存值
    
    int fib(int n) const {
        if (n <= 1) return n;
        return fib(n-1) + fib(n-2);
    }
    
public:
    Fib(int n) : n_(n) {}
    
    int value() const {
        if (!cached) {
            cache = fib(n_);        // 在const函数中修改mutable成员
            cached = true;
        }
        return cache;
    }
};
```

## 六、静态成员

### 6.1 静态成员变量
**静态成员变量特点**：
+ 静态成员变量属于类本身，而不是某个类的特定对象
+ 其在程序开始的时候就存在，不依赖于任何独享的创建
+ 储存在静态存储区
+ 支持public、private、protected
+ 需要在类外定义和初始化
```c++
class ObjectCounter {
private:
    static int obj_count;    // 静态成员变量声明，所有对象共用
    int id;
    
public:
    ObjectCounter() {
        obj_count++;
        id = obj_count;
        cout << "Object " << id << " created. Total: " << obj_count << endl;
    }
    
    ~ObjectCounter() {
        obj_count--;
        cout << "Object " << id << " destroyed. Total: " << obj_count << endl;
    }
    
    static int getCount() {  // 静态成员函数
        return obj_count;
    }
};

// 静态成员变量定义
int ObjectCounter::obj_count = 0;

void demonstrateStaticMembers() {
    ObjectCounter obj1, obj2;
    {
        ObjectCounter obj3;
        cout << "Current count: " << ObjectCounter::getCount() << endl;
    }
    cout << "Final count: " << ObjectCounter::getCount() << endl;
}
```

### 6.2 单例模式
**单例模式**是一种创建型设计模式，它确保一个类只有一个实例，并提供一个全局访问点来获取这个实例。

**核心思想**：
+ 唯一性：一个类只能有一个实例
+ 全局访问：该实例可以被全局访问
+ 受控创建：该实例的创建由类本身控制
```c++
class Singleton {
private:
    static Singleton* instance;
    
    // 私有构造函数，防止外部创建实例
    Singleton() {}
    
    // 禁用拷贝
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
    
public:
    static Singleton* getInstance() {
        if (instance == nullptr) {
            instance = new Singleton();
        }
        return instance;
    }
    
    static void destroy() {
        delete instance;
        instance = nullptr;
    }
    
    void showMessage() {
        cout << "Singleton instance: " << this << endl;
    }
};

// 静态成员初始化
Singleton* Singleton::instance = nullptr;

void demonstrateSingleton() {
    Singleton* s1 = Singleton::getInstance();
    Singleton* s2 = Singleton::getInstance();
    
    s1->showMessage();
    s2->showMessage();  // 两个指针指向同一实例
    
    Singleton::destroy();
}
```
### 6.3 静态成员函数
**静态成员函数特点**：
+ 静态成员函数属于类本身，而不是某个类的特定对象
+ 没有this指针，不能直接访问非静态成员变量
+ 可以通过类名直接调用，不需要创建对象
+ 主要用于操作静态成员变量或提供工具函数
+ 支持public、private、protected访问控制

```c++
class MathUtilities {
private:
    static int operation_count;  // 静态成员变量
    
public:
    // 静态工具函数
    static double add(double a, double b) {
        operation_count++;
        return a + b;
    }
    
    static double multiply(double a, double b) {
        operation_count++;
        return a * b;
    }
    
    static double power(double base, double exponent) {
        operation_count++;
        return pow(base, exponent);
    }
    
    // 静态成员函数访问静态成员变量
    static int getOperationCount() {
        return operation_count;
    }
    
    static void resetCounter() {
        operation_count = 0;
        cout << "Counter reset" << endl;
    }
    
    // 错误示例：静态函数不能访问非静态成员
    // static void errorFunction() {
    //     int x = normal_member;  // 编译错误！
    // }
};

// 静态成员变量定义
int MathUtilities::operation_count = 0;

void demonstrateStaticFunctions() {
    // 通过类名直接调用静态函数，无需创建对象
    cout << "5 + 3 = " << MathUtilities::add(5, 3) << endl;
    cout << "4 * 2.5 = " << MathUtilities::multiply(4, 2.5) << endl;
    cout << "2^8 = " << MathUtilities::power(2, 8) << endl;
    
    cout << "Total operations: " << MathUtilities::getOperationCount() << endl;
    
    MathUtilities::resetCounter();
    cout << "After reset: " << MathUtilities::getOperationCount() << endl;
    
    // 也可以通过对象调用（但不推荐）
    MathUtilities util;
    cout << "Via object: " << util.add(2, 2) << endl;
}
```

## 七、友元

### 7.1 友元函数
**友元函数**是c++的一种特殊机制，他允许非成员函数访问类的private和protected
**友元函数的特点**：
+ 突破封装:
    - 可以访问类的私有成员
    - 不受访问权限限制
    - 破坏了类的封装
+ 非成员函数:
    - 没有**this**指针
    - 不需要通过对象调用
    - 定义在类外部
```c++
class Vector;  // 前向声明

class Matrix {
private:
    int* data;
    int rows, cols;
    
public:
    Matrix(int r, int c) : rows(r), cols(c) {
        data = new int[rows * cols];
    }
    
    ~Matrix() { delete[] data; }
    
    int& element(int i, int j) {
        return data[i * cols + j];
    }
    
    void display() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                cout << element(i, j) << " ";
            }
            cout << endl;
        }
    }
    
    // 声明友元函数
    friend void multiply(const Matrix& m, const Vector& v, Vector& result);
};

class Vector {
private:
    int* data;
    int size;
    
public:
    Vector(int s) : size(s) {
        data = new int[size];
    }
    
    ~Vector() { delete[] data; }
    
    int& element(int i) {
        return data[i];
    }
    
    void display() {
        for (int i = 0; i < size; i++) {
            cout << element(i) << " ";
        }
        cout << endl;
    }
    
    // 声明友元函数
    friend void multiply(const Matrix& m, const Vector& v, Vector& result);
};

// 友元函数实现 - 可以访问两个类的私有成员
void multiply(const Matrix& m, const Vector& v, Vector& result) {
    for (int i = 0; i < m.rows; i++) {
        result.data[i] = 0;
        for (int j = 0; j < m.cols; j++) {
            result.data[i] += m.data[i * m.cols + j] * v.data[j];
        }
    }
}
```

### 7.2 友元类和友元成员函数
#### 友元类
一个类可以将另外一个类生命为自己的友元。这样，这个友元类的所有成员函数都可以访问那个类的private与protected

关键点:
+ 单向性：A是B的友元不代表B是A的友元
+ 不可传递性：如果B是A的友元，C是B的友元不代表C是A的友元

### 友元成员函数
有时候并不需要将整个类设置为友元，只需要将其中一个成员函数设置为友元就可以了（注意友元函数的声明）

关键点与注意事项：
+ 精确控制：只开放必要的权限给特定的函数，比开放整个类更加安全
+ 声明顺序至关重要：
   - 必须首先对class C进行前向声明
   - 然后在class A中声明class C中的某个成员函数为友元
     - ```friend void C::accessA(A& a);```
   - 最后，才能给出class c的完整定义。
```c++
class C;  // 前向声明

class A {
private:
    int secret;
    
public:
    A() : secret(42) {}
    
    // 友元函数
    friend void friendFunction(A& a);
    
    // 友元类
    friend class B;
    
    // 友元成员函数
    friend void C::accessA(A& a);
    // 注意：这里需要用到 ClassC，所以前面必须要有 ClassC 的前向声明
};

class B {
public:
    void accessA(A& a) {
        cout << "B accessing A's secret: " << a.secret << endl;
    }
};

class C {
public:
    void accessA(A& a);  // 需要在A之后定义
};

void C::accessA(A& a) {
    cout << "C accessing A's secret: " << a.secret << endl;
}

void friendFunction(A& a) {
    cout << "Friend function accessing A's secret: " << a.secret << endl;
}
```


## 八、常量表达式（constexpr和consteval）
**常量表达式**是指在编译器就可以计算出结果的表达式。 
### constexpr 
constexpr表示一个值或函数可以在编译器求值，但也可以在运行期求值
```c++
class ConstExprDemo {
private:
    static constexpr int MAX_SIZE = 100;  // 编译期常量
    
public:
    // constexpr构造函数 - 可以在编译期调用
    constexpr ConstExprDemo(int x, int y) : x_(x), y_(y) {}
    
    // constexpr成员函数 - 编译期可求值
    constexpr int area() const { return x_ * y_; }
    
    // consteval函数（C++20）- 必须在编译期求值
    consteval int doubleArea() const { return 2 * area(); }
    
private:
    int x_, y_;
};

void demonstrateConstexpr() {
    constexpr int size = 10;                    // 编译期常量
    constexpr int array[size] = {1, 2, 3};      // 用于数组大小
    
    constexpr ConstExprDemo rect(5, 8);
    constexpr int rect_area = rect.area();      // 编译期计算
    
    // 编译期计算的应用场景
    static_assert(rect_area == 40, "Area should be 40");
    
    // constexpr if - 编译期条件判断
    if constexpr (sizeof(int) == 4) {
        // 只在32位系统编译的代码
    }
}
```
### consteval
consteval创建立即函数，表示该函数必须在编译器求值，如果在运行期间调用就会编译错误
```c++
// consteval函数 - 必须编译期求值
consteval int compile_time_square(int x) {
return x * x;
}

// constexpr函数 - 可以编译期或运行期求值
constexpr int flexible_square(int x) {
return x * x;
}

void demonstrateConsteval() {
constexpr int a = compile_time_square(5);  // ✅ 正确
int runtime_value = 5;

    // int b = compile_time_square(runtime_value);  // ❌ 错误！参数不是常量
    
    int c = flexible_square(runtime_value);     // ✅ 正确，运行期计算
    constexpr int d = flexible_square(5);       // ✅ 正确，编译期计算
}
```
## 九、继承

### 9.1 继承基础
**继承**是面对对象编程的重要特性，它允许我们在已有的类的基础上创建新的类。新的类（派生类）继承原有类的属性与方法
，并允许创建新的方法与修改原有方法

```c++
class Person {
protected:
    int id;
    char name[50];
    
public:
    Person(int id_val, const char* name_val) : id(id_val) {
        strcpy(name, name_val);
    }
    
    void setID(int x) { id = x; }
    void setName(const char* s) { strcpy(name, s); }
    void showInfo() { 
        cout << name << " : " << id << endl; 
    }
};

class Student : public Person {  // public继承
private:
    char major[50];
    
public:
    Student(int id, const char* name, const char* major_val) 
        : Person(id, name) {  // 调用基类构造函数
        strcpy(major, major_val);
    }
    
    void setMajor(const char* m) { strcpy(major, m); }
    void showInfo() {  // 重写基类方法
        cout << name << " : " << id << " - " << major << endl;
    }
};
```
**关键概念解释**：
+ 访问控制符protected：
  - protected不可以在类外访问（类似private）
  - 但可以在派生类里访问（类似public）
  - 这提供了访问控制
- 构造函数调用：
  - 派生类构造函数必须调用基类构造函数
  - 通过初始化列表（: Person(id, name) ）调用
- 方法重写：

  - 派生类可以重新定义基类的方法

  - 这里 Student::showInfo() 重写了 Person::showInfo()

  - 注意：这不是多态，如需多态需使用 virtual 关键字
### 9.2 继承中的构造函数

```c++
class A {
private:
    int x;
public:
    A() : x(0) { cout << "A()" << endl; }
    A(int i) : x(i) { cout << "A(" << i << ")" << endl; }
    A(const A& other) : x(other.x) { cout << "A copy" << endl; }
};

class B : public A {
private:
    int y;
public:
    // 默认调用A::A()
    B() : y(0) { cout << "B()" << endl; }
    
    // 调用A::A()，然后B::B(int)
    B(int i) : y(i) { cout << "B(" << i << ")" << endl; }
    
    // 显式调用A::A(int)，然后B::B(int,int)
    B(int i, int j) : A(i), y(j) { 
        cout << "B(" << i << "," << j << ")" << endl; 
    }
    
    // 拷贝构造函数 - 需要显式调用基类拷贝构造
    B(const B& other) : A(other), y(other.y) {
        cout << "B copy" << endl;
    }
    
    // 继承构造函数（C++11）
    using A::A;  // 继承A的所有构造函数
};

void demonstrateInheritance() {
    B b1;       // 输出: A() B()
    B b2(1);     // 输出: A() B(1)
    B b3(2, 3);  // 输出: A(2) B(2,3)
    B b4 = b3;   // 输出: A copy B copy
}
```
**关键概念解释**：
+ 构造顺序：

  + 基类构造函数 → 派生类成员初始化 → 派生类构造函数体

  + 析构顺序正好相反：派生类析构 → 基类析构

+ 默认基类构造：

  + 如果没有显式调用基类构造函数，编译器会自动调用基类的默认构造函数

  + 如果基类没有默认构造函数，必须显式调用

+ 拷贝构造的特殊性：

  + 派生类拷贝构造需要显式调用基类拷贝构造

  + 否则会调用基类的默认构造函数，可能导致错误

+ 继承构造函数（C++11）：

  + using A::A 让派生类继承基类的所有构造函数

  + 方便但不常用，因为可能不适合派生类的特殊需求
### 9.3 继承方式与访问控制

```c++
class Base {
private:
    int private_member;
protected:
    int protected_member;
public:
    int public_member;
    
    void baseMethod() {
        private_member = 1;    // OK
        protected_member = 2;  // OK
        public_member = 3;     // OK
    }
};

class PublicDerived : public Base {
public:
    void derivedMethod() {
        // private_member = 1;    // 错误：不能访问private
        protected_member = 2;     // OK
        public_member = 3;        // OK
    }
};

class PrivateDerived : private Base {
public:
    void derivedMethod() {
        protected_member = 2;     // OK
        public_member = 3;        // OK（但在类外不可访问）
    }
};

void demonstrateAccessControl() {
    PublicDerived pub;
    pub.public_member = 10;       // OK
    
    PrivateDerived priv;
    // priv.public_member = 10;   // 错误：private继承使public成员变为private
}
```
**访问权限表格**

| 基类中的访问权限 | 公有继承后 | 保护继承后 | 私有继承后 |
|:---------------:|:----------:|:----------:|:----------:|
| public          | public     | protected  | private    |
| protected       | protected  | protected  | private    |
| private         | 不可访问   | 不可访问   | 不可访问   |
## 十、虚函数与多态

### 10.1 虚函数基础
**虚函数**是C++中实现**多态**的核心机制，他允许在基类中声明一个函数为虚函数，然后在派生类里重写该函数
从而实现**运行时多态**

**核心思想**：
+ 静态绑定：编译时确认调用哪个函数
+ 动态绑定：运行时根据对象的实际类型确认调用哪个函数
```c++
class Shape {
protected:
    int x, y;
public:
    Shape(int x_val, int y_val) : x(x_val), y(y_val) {}
    
    // 虚函数 - 支持动态绑定
    virtual double area() const {
        cout << "Shape::area()" << endl;
        return 0;
    }
    
    // 普通函数 - 静态绑定
    void move(int dx, int dy) {
        x += dx;
        y += dy;
    }
    
    // 虚析构函数 - 确保正确调用派生类析构函数
    virtual ~Shape() {
        cout << "Shape destructor" << endl;
    }
};

class Circle : public Shape {
private:
    double radius;
public:
    Circle(int x, int y, double r) : Shape(x, y), radius(r) {}
    
    // 重写虚函数
    double area() const override {
        cout << "Circle::area()" << endl;
        return 3.14159 * radius * radius;
    }
    
    ~Circle() override {
        cout << "Circle destructor" << endl;
    }
};

class Rectangle : public Shape {
private:
    double width, height;
public:
    Rectangle(int x, int y, double w, double h) 
        : Shape(x, y), width(w), height(h) {}
    
    double area() const override {
        cout << "Rectangle::area()" << endl;
        return width * height;
    }
    
    ~Rectangle() override {
        cout << "Rectangle destructor" << endl;
    }
};

void demonstratePolymorphism() {
    Shape* shapes[3];
    shapes[0] = new Circle(0, 0, 5);
    shapes[1] = new Rectangle(1, 1, 4, 6);
    shapes[2] = new Shape(2, 2);
    
    // 多态调用 - 根据实际对象类型调用相应函数
    for (int i = 0; i < 3; i++) {
        cout << "Area: " << shapes[i]->area() << endl;
        delete shapes[i];  // 正确调用派生类析构函数
    }
}
```

### 10.2 虚函数表机制

```c++
class BaseWithVTable {
public:
    virtual void func1() { cout << "Base::func1" << endl; }
    virtual void func2() { cout << "Base::func2" << endl; }
    void func3() { cout << "Base::func3" << endl; }  // 非虚函数
};

class DerivedWithVTable : public BaseWithVTable {
public:
    void func1() override { cout << "Derived::func1" << endl; }
    void func3() { cout << "Derived::func3" << endl; }  // 隐藏，不是重写
};

void demonstrateVTable() {
    BaseWithVTable base;
    DerivedWithVTable derived;
    
    BaseWithVTable* ptr = &derived;
    
    ptr->func1();  // 输出: Derived::func1 (动态绑定)
    ptr->func2();  // 输出: Base::func2 (动态绑定)  
    ptr->func3();  // 输出: Base::func3 (静态绑定)
}
```

#### 详细解释

##### 虚函数表（vtable）概念
虚函数表是c++实现多态的机制：
+ 每个包含虚函数类的都有一个虚函数表
+ 虚函数表是一个函数指针数组，存储该类所有虚函数的地址
+ 每个对象包含一个指向其类的虚函数表的指针（vptr）

##### 内存分配示意图
```
BaseWithVTable 对象：
+----------------+
| vptr           | --> 指向 BaseWithVTable 的虚函数表
+----------------+
| 其他数据成员    |
+----------------+

BaseWithVTable 虚函数表：
+----------------+
| &Base::func1   |
+----------------+
| &Base::func2   |
+----------------+

DerivedWithVTable 对象：
+----------------+
| vptr           | --> 指向 DerivedWithVTable 的虚函数表
+----------------+
| 基类数据成员    |
+----------------+
| 派生类数据成员  |
+----------------+

DerivedWithVTable 虚函数表：
+---------------------+
| &Derived::func1     |  // 重写了基类的func1
+---------------------+
| &Base::func2        |  // 继承基类的func2
+---------------------+
```

##### 函数调用分析
```ptr->func1()``` - **动态绑定**
```cpp
ptr->func1();  // 输出: Derived::func1
```
+ ptr 的类型是 BaseWithVTable*，但指向 DerivedWithVTable 对象

+ 通过对象的vptr找到虚函数表

+ 在虚函数表中查找 func1 的位置，调用对应的函数

+ 由于 DerivedWithVTable 重写了 func1，所以调用派生类版本

```ptr->func2()``` - **动态绑定**
```cpp
ptr->func2();  // 输出: Base::func2
```
+ 同样通过虚函数表查找

+ DerivedWithVTable 没有重写 func2，所以虚函数表中仍然是基类的函数地址

+ 调用基类版本的 func2

```ptr->func3()``` - **静态绑定**
```cpp
ptr->func3();  // 输出: Base::func3
```
+ func3 是非虚函数，不通过虚函数表调用

+ 编译器根据指针的静态类型（BaseWithVTable*）决定调用哪个函数

+ 总是调用 BaseWithVTable::func3，无论实际指向什么对象
### 10.3 final和override

```c++
class BaseFinalOverride {
public:
    virtual void mustOverride() = 0;  // 纯虚函数
    virtual void canOverride() { cout << "Base" << endl; }
    virtual void cannotOverride() final { cout << "Final" << endl; }
};

class DerivedFinalOverride : public BaseFinalOverride {
public:
    void mustOverride() override {  // 必须重写纯虚函数
        cout << "Derived implementation" << endl;
    }
    
    void canOverride() override {   // 显式声明重写
        cout << "Derived override" << endl;
    }
    
    // void cannotOverride() { }  // 错误：final函数不能重写
};

class FinalClass final {  // final类，不能被继承
public:
    void method() { }
};

// class CannotInherit : public FinalClass { };  // 错误：final类不能继承
```

**说明**：
+ final：
  + 阻止类被继承
  + 阻止虚函数被重写
+ override：用于明确表示函数重写基类的虚函数
### 10.4 类型兼容与对象切片

```c++
void demonstrateObjectSlicing() {
    Circle circle(0, 0, 5);
    //类型兼容
    Shape shape = circle;  // 对象切片 - 只复制基类部分
    
    cout << "Circle area: " << circle.area() << endl;  // Circle::area()
    cout << "Sliced area: " << shape.area() << endl;   // Shape::area()
    
    // 引用和指针避免切片
    Shape& shape_ref = circle;
    Shape* shape_ptr = &circle;
    
    cout << "Reference area: " << shape_ref.area() << endl;  // Circle::area()
    cout << "Pointer area: " << shape_ptr->area() << endl;   // Circle::area()
}
```
**对象切片**：当**派生类**对象赋值给**基类**对象时，只复制基类部分，派生类**特有**的部分被"切掉"。
+ 可以使用使用指针或引用保持多态性
+ 只发生在值拷贝时
+ 函数参数传递时容易发生切片
  + ``` cpp
    void badFunction(Shape shape) { ... }  // 可能切片！
    void goodFunction(Shape& shape) { ... } // 安全
    void goodFunction(Shape* shape) { ... } // 安全 
    ``` 
## 十一、访问控制深入

### 11.1 继承中的访问权限变化

```c++
class AccessBase {
private:
    int private_var;
protected:
    int protected_var;
public:
    int public_var;
};

class PublicDerived : public AccessBase {
    // public继承：访问权限不变
    // public_var -> public
    // protected_var -> protected  
    // private_var -> 不可访问
};

class ProtectedDerived : protected AccessBase {
    // protected继承：public变为protected
    // public_var -> protected
    // protected_var -> protected
    // private_var -> 不可访问
};

class PrivateDerived : private AccessBase {
    // private继承：所有都变为private
    // public_var -> private
    // protected_var -> private
    // private_var -> 不可访问
};
```

### 11.2 using声明改变访问权限

```c++
class BaseWithHidden {
public:
    void method(int x) { cout << "Base::method(int)" << endl; }
};

class DerivedWithUsing : public BaseWithHidden {
private:
    using BaseWithHidden::method;  // 将method设为private
};

class BaseWithOverload {
public:
    void func() { cout << "Base::func()" << endl; }
    void func(int) { cout << "Base::func(int)" << endl; }
};

class DerivedHiding : public BaseWithOverload {
public:
    using BaseWithOverload::func;  // 引入所有重载版本
    void func(double) { cout << "Derived::func(double)" << endl; }
};

void demonstrateUsing() {
    DerivedWithUsing d1;
    // d1.method(1);  // 错误：method现在是private
    
    DerivedHiding d2;
    d2.func();      // Base::func()
    d2.func(1);     // Base::func(int) 
    d2.func(1.0);   // Derived::func(double)
}
```
**注**：使用 using 声明改变的是派生类中对基类成员的访问权限，而不是基类本身。
## 十二、友元与继承
在c++中友元关系是不能被继承的，这说明：
+ 基类的友元不是派生类的友元
+ 派生类的友元不是基类的友元
+ 有缘的关系是单向的、不可传递的
```c++
class BaseFriend {
protected:
    int prot_mem;
};

class Sneaky : public BaseFriend {
    friend void clobber(Sneaky&);   // 可以访问Sneaky::prot_mem
    friend void clobber(BaseFriend&); // 错误：不能访问BaseFriend::prot_mem
    
private:
    int j;
};

void clobber(Sneaky& s) {
    s.j = s.prot_mem = 0;  // OK：可以访问Sneaky的protected成员
}

// void clobber(BaseFriend& b) {
//     b.prot_mem = 0;  // 错误：不能访问BaseFriend的protected成员
// }
```