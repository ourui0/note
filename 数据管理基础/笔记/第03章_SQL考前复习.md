# 第03章 SQL 语言考前复习

参考：第03章讲义、SQL复习思考题参考答案、数据管理基础期末练习（2026）。

## 一、样卷考法

样卷 SQL 大题主要考查询，不重点考完整 DDL。高频题型：

- 字符串匹配：`LIKE`
- 多表连接查询
- 否定语义：`NOT EXISTS` / `NOT IN`
- “只……”：反例不存在
- “所有……”：双重 `NOT EXISTS`
- 每组最大值：`>= ALL` / `NOT EXISTS`
- 分组统计：`GROUP BY`、`HAVING`、聚集函数
- 排序：`ORDER BY`

样卷涉及的教务数据库：

```text
Student(sno, sname, dept)
Teacher(tno, tname, dept)
Course(cno, cname, dept, opt, credit)
Courseclass(clsno, cno, tno, tyear)
Enrollment(sno, clsno, grade)
```

## 二、SQL 基本结构

基本查询：

```sql
select 目标列
from 表1, 表2
where 连接条件 and 筛选条件;
```

多表连接常见套路：

```sql
select s.sno, s.sname
from student s, enrollment e, courseclass cc, course c
where s.sno = e.sno
  and e.clsno = cc.clsno
  and cc.cno = c.cno
  and c.cname = '数据管理基础';
```

易错点：

- 多表查询必须写连接条件，否则会产生笛卡尔积。
- 查询目标列如果来自多个表，最好加表别名。
- SQL 中字符串用单引号。

## 三、字符串匹配 LIKE

`LIKE` 用于模糊匹配：

- `%`：任意长度字符串。
- `_`：任意一个字符。

例题：查询课程名中含有“数据库”的课程名和开课院系。

```sql
select cname, dept
from course
where cname like '%数据库%';
```

## 四、多表连接查询

例题：查询修读了“智软学院”开设的“数据管理基础”课的学生学号和姓名。

```sql
select s.sno, s.sname
from student s, course c, enrollment e, courseclass cc
where s.sno = e.sno
  and e.clsno = cc.clsno
  and cc.cno = c.cno
  and c.dept = '智软学院'
  and c.cname = '数据管理基础';
```

分析：

- 学生到课程不能直接连。
- 路径是：`Student -> Enrollment -> Courseclass -> Course`。

## 五、否定查询

关系代数中的“差”在 SQL 中通常用：

- `NOT IN`
- `NOT EXISTS`
- `EXCEPT`

例题：查询没有通过纽约市供应商购买过商品的顾客。

```sql
select c.cid, c.cname
from customers c
where not exists (
  select *
  from orders o, agents a
  where o.aid = a.aid
    and o.cid = c.cid
    and a.city = '纽约'
);
```

也可写成：

```sql
select cid, cname
from customers
where cid not in (
  select o.cid
  from orders o, agents a
  where o.aid = a.aid
    and a.city = '纽约'
);
```

建议考试优先用 `NOT EXISTS`，语义更稳。

## 六、“只……”查询

“只讲授过自己工作所在院系开设的课程”意思是：不存在一门他讲授过的课，其开课院系不等于教师工作院系。

例题：查询只讲授过自己工作所在院系开设课程的教师。

```sql
select t.tno, t.tname
from teacher t
where t.tno in (
  select tno
  from courseclass
)
and not exists (
  select *
  from courseclass cc, course c
  where cc.tno = t.tno
    and cc.cno = c.cno
    and t.dept <> c.dept
);
```

说明：

- `t.tno in (...)` 表示至少讲授过课程。
- `not exists (...)` 排除“讲过外院课程”的教师。

模板：

```sql
where 至少做过
  and not exists (违反“只……”条件的记录)
```

## 七、“所有……”查询：双重 NOT EXISTS

关系代数中的除法，在 SQL 中通常用双重 `NOT EXISTS`。

通用模板：

```sql
select A
from 外层对象 x
where not exists (
  select *
  from 需要全部覆盖的对象 y
  where not exists (
    select *
    from 已完成记录 z
    where z 与 x 对应
      and z 与 y 对应
  )
);
```

例题：查询修读了自己就读院系开设的所有“核心”课的学生。

```sql
select s.sno, s.sname
from student s
where not exists (
  select *
  from course c
  where c.dept = s.dept
    and c.opt = '核心'
    and not exists (
      select *
      from enrollment e, courseclass cc
      where e.sno = s.sno
        and e.clsno = cc.clsno
        and cc.cno = c.cno
    )
);
```

读法：

- 外层学生 `s`。
- 中层找该学生院系开设的核心课 `c`。
- 内层检查学生是否修过这门课。
- 如果不存在“某门核心课没修过”，则说明修读了全部核心课。

## 八、每组最大值

方法一：`>= ALL`

例题：在每个“数据管理基础”课程班上，查询成绩最高的学生，返回课程班号、授课年份、学号、成绩，并按成绩降序输出。

```sql
select cc.clsno, cc.tyear, e.sno, e.grade
from enrollment e, courseclass cc, course c
where e.clsno = cc.clsno
  and cc.cno = c.cno
  and c.cname = '数据管理基础'
  and e.grade >= all (
    select e2.grade
    from enrollment e2
    where e2.clsno = cc.clsno
  )
order by e.grade desc;
```

注意：样卷参考答案少写了最后的 `order by e.grade desc`，考试时要补上。

方法二：`NOT EXISTS`

```sql
select cc.clsno, cc.tyear, e.sno, e.grade
from enrollment e, courseclass cc, course c
where e.clsno = cc.clsno
  and cc.cno = c.cno
  and c.cname = '数据管理基础'
  and not exists (
    select *
    from enrollment e2
    where e2.clsno = e.clsno
      and e2.grade > e.grade
  )
order by e.grade desc;
```

两个写法都能保留并列第一名。

## 九、分组统计 GROUP BY / HAVING

常用聚集函数：

- `count(*)`
- `sum(...)`
- `avg(...)`
- `max(...)`
- `min(...)`

`where` 与 `having` 区别：

- `where`：分组前筛选元组。
- `having`：分组后筛选分组。

例题：针对所有课程都及格的学生，统计学号、姓名、平均成绩、总学分数，按平均成绩降序输出。

```sql
select s.sno, s.sname, avg(e.grade), sum(c.credit)
from student s, enrollment e, courseclass cc, course c
where s.sno = e.sno
  and e.clsno = cc.clsno
  and cc.cno = c.cno
group by s.sno, s.sname
having min(e.grade) >= 60
order by avg(e.grade) desc;
```

分析：

- `min(e.grade) >= 60` 表示该学生所有已修课程都及格。
- 若题目要求“所有应修课程都及格”，还要结合课程集合判断；样卷语义是统计已修课程。

## 十、子查询分类

子查询：一个 `SELECT-FROM-WHERE` 查询块嵌套在另一个查询块中。

独立子查询：

- 子查询条件不依赖父查询。
- 执行方式通常由里向外。

相关子查询：

- 子查询条件依赖父查询中的当前元组。
- 执行方式类似嵌套循环。

例：相关子查询。

```sql
select c.cid, c.cname
from customers c
where not exists (
  select *
  from orders o
  where o.cid = c.cid
);
```

子查询中 `o.cid = c.cid` 引用了外层 `c`，所以是相关子查询。

## 十一、数据定义与约束速查

虽然第04、05章不作为考试要求，但样卷选择题出现了约束常识。

建表常用约束：

```sql
create table Student (
  sno char(10) primary key,
  sname varchar(50) not null,
  dept varchar(50)
);
```

外键：

```sql
foreign key (sno) references Student(sno)
```

常见约束：

- `primary key`
- `foreign key`
- `unique`
- `not null`
- `check`

外码违约处理常见规则：

- `cascade`
- `restrict`
- `set null`

不是外码违约处理规则的是：`check`。

## 十二、事务与游标速查

事务结束命令：

```sql
commit;
rollback;
```

样卷选择题中，“用于结束当前事务”的命令选 `rollback`。

权限回收：

```sql
revoke ...
```

游标基本命令：

- `declare`：声明游标。
- `open`：打开游标。
- `fetch`：取回一条结果元组。
- `close`：关闭游标。

样卷选择题中，用于返回一条结果元组的是 `fetch`。

## 十三、考前模板汇总

没有做过：

```sql
where not exists (
  select *
  from 记录表 r
  where r.外键 = 外层.主键
)
```

只做过满足条件的：

```sql
where exists (至少一条记录)
  and not exists (违反条件的记录)
```

做过所有：

```sql
where not exists (
  select *
  from 目标集合 t
  where not exists (
    select *
    from 完成记录 r
    where r 匹配外层对象
      and r 匹配目标对象
  )
)
```

每组最大：

```sql
and value >= all (
  select value
  from 同表 x
  where x.group_id = 当前.group_id
)
```

分组统计：

```sql
select 分组列, 聚集函数
from ...
where 分组前条件
group by 分组列
having 分组后条件
order by 排序表达式;
```

