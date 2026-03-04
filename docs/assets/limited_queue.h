#pragma once

#include <cstddef>
#include <iterator>
#include <memory>
#include <stdexcept>
#include <type_traits>

template <typename T>
class LimitedDeque {
private:
  std::unique_ptr<T> m_Buffer;         // 缓冲区指针
  std::size_t m_Capacity;              // 最大容量
  std::size_t m_Head;                  // 指向第一个有效元素
  std::size_t m_Tail;                  // 指向下一个可插入位置（尾后）
  std::size_t m_Size;                  // 当前元素个数

  // 内部辅助：安全索引计算（模运算）
  size_t index(std::ptrdiff_t i) const {
    return (m_Head + static_cast<size_t>(i % static_cast<std::ptrdiff_t>(m_Capacity)) + m_Capacity) % m_Capacity;
  }

public:
  template <bool IsConst>
  class IteratorImpl {
  public:
    using value_type = typename std::conditional<IsConst, const T, T>::type;
    using reference = value_type &;
    using pointer = value_type *;
    using difference_type = std::ptrdiff_t;
    using iterator_category = std::random_access_iterator_tag;
    using deque_ptr_type = typename std::conditional<IsConst, const LimitedDeque *, LimitedDeque *>::type;

    IteratorImpl() : m_Deque(nullptr), m_Pos(0) {}
    IteratorImpl(deque_ptr_type deque, ptrdiff_t pos) : m_Deque(deque), m_Pos(pos) {}
    IteratorImpl(const IteratorImpl &other) : m_Deque(other.m_Deque), m_Pos(other.m_Pos) {}

    // 解引用
    reference operator*() const {
      if (m_Pos < 0 || m_Pos >= static_cast<ptrdiff_t>(m_Deque->m_Size)) {
        throw std::out_of_range("LimitedDeque::Iterator: out of range");
      }
      return m_Deque->m_Buffer[m_Deque->index(m_Pos)]; // 环形索引
    }

    pointer operator->() const { return &(*(*this)); }
    friend IteratorImpl operator+(difference_type n, const IteratorImpl &it) { return it + n; }

    // 前缀自增
    IteratorImpl &operator++() {
      ++m_Pos;
      return *this;
    }

    // 后缀自增
    IteratorImpl operator++(int) {
      IteratorImpl tmp = *this;
      ++(*this);
      return tmp;
    }

    // 前缀自减
    IteratorImpl &operator--() {
      --m_Pos;
      return *this;
    }

    // 后缀自减
    IteratorImpl operator--(int) {
      IteratorImpl tmp = *this;
      --(*this);
      return tmp;
    }

    // 随机访问
    reference operator[](difference_type n) const { return *(*this + n); }

    // 算术运算
    IteratorImpl operator+(difference_type n) const {
      IteratorImpl tmp = *this;
      tmp.m_Pos += n;
      return tmp;
    }

    IteratorImpl operator-(difference_type n) const {
      IteratorImpl tmp = *this;
      tmp.m_Pos -= n;
      return tmp;
    }

    // 指针差值
    difference_type operator-(const IteratorImpl &other) const { return m_Pos - other.m_Pos; }

    // 复合赋值
    IteratorImpl &operator+=(difference_type n) {
      m_Pos += n;
      return *this;
    }

    IteratorImpl &operator-=(difference_type n) {
      m_Pos -= n;
      return *this;
    }

    // 比较运算符
    bool operator==(const IteratorImpl &other) const { return m_Pos == other.m_Pos; }
    bool operator!=(const IteratorImpl &other) const { return !(*this == other); }
    bool operator<(const IteratorImpl &other) const { return m_Pos < other.m_Pos; }
    bool operator<=(const IteratorImpl &other) const { return m_Pos <= other.m_Pos; }
    bool operator>(const IteratorImpl &other) const { return m_Pos > other.m_Pos; }
    bool operator>=(const IteratorImpl &other) const { return m_Pos >= other.m_Pos; }

  private:
    deque_ptr_type m_Deque;
    ptrdiff_t m_Pos;
  };

public:
  using value_type = T;
  using size_type = size_t;
  using reference = T &;
  using const_reference = const T &;
  using pointer = T *;
  using const_pointer = const T *;

  // 迭代器类型别名
  using iterator = IteratorImpl<false>;
  using const_iterator = IteratorImpl<true>;
  using reverse_iterator = std::reverse_iterator<iterator>;
  using const_reverse_iterator = std::reverse_iterator<const_iterator>;

  // 构造函数
  LimitedDeque(size_t max_size) : m_Capacity(max_size), m_Head(0), m_Tail(0), m_Size(0) {
    if (m_Capacity == 0) {
      // std::cout << "LimitedDeque: capacity must be > 0, default 20\r\n";
      m_Capacity = 20;
    }
    m_Buffer = std::make_unique<T[]>(m_Capacity);
  }

  // 析构函数（可省略，因为 unique_ptr 会自动释放）
  ~LimitedDeque() = default;

  // 拷贝构造
  LimitedDeque(const LimitedDeque &other)
      : m_Capacity(other.m_Capacity), m_Head(other.m_Head), m_Tail(other.m_Tail), m_Size(other.m_Size) {
    m_Buffer = std::make_unique<T[]>(m_Capacity);

    for (size_t i = 0; i < m_Size; ++i) {
      m_Buffer[i] = other.m_Buffer[(other.m_Head + i) % other.m_Capacity];
    }
  }

  // 拷贝赋值
  LimitedDeque &operator=(const LimitedDeque &other) {
    if (this == &other) return *this;
    m_Buffer.reset();
    m_Capacity = other.m_Capacity;
    m_Size = other.m_Size;
    m_Buffer = std::make_unique<T[]>(m_Capacity);
    for (size_t i = 0; i < m_Size; ++i) {
      m_Buffer[i] = other.m_Buffer[(other.m_Head + i) % other.m_Capacity];
    }
    m_Head = 0;
    m_Tail = m_Size;
    return *this;
  }

  // 移动构造
  LimitedDeque(LimitedDeque &&other) noexcept
      : m_Buffer(std::move(other.m_Buffer)),
        m_Capacity(other.m_Capacity),
        m_Head(other.m_Head),
        m_Tail(other.m_Tail),
        m_Size(other.m_Size) {
    other.m_Buffer = nullptr;
    other.m_Capacity = 0;
    other.m_Head = 0;
    other.m_Tail = 0;
    other.m_Size = 0;
  }

  // 移动赋值
  LimitedDeque &operator=(LimitedDeque &&other) noexcept {
    if (this != &other) {
      m_Buffer = std::move(other.m_Buffer);
      m_Capacity = other.m_Capacity;
      m_Head = other.m_Head;
      m_Tail = other.m_Tail;
      m_Size = other.m_Size;
      other.m_Buffer = nullptr;
      other.m_Capacity = 0;
      other.m_Head = 0;
      other.m_Tail = 0;
      other.m_Size = 0;
    }
    return *this;
  }

  // 获取最大容量
  size_t get_max_size() const { return m_Capacity; }

  // 获取当前大小
  size_t size() const { return m_Size; }

  // 判空
  bool empty() const { return m_Size == 0; }

  // 清空
  void clear() { m_Head = m_Tail = m_Size = 0; }

  // 前端插入
  void push_front(const T &value) {
    if (m_Size >= m_Capacity) {
      // 满了，覆盖尾部元素（逻辑上是“最老的”）
      m_Tail = (m_Tail - 1 + m_Capacity) % m_Capacity;
      m_Buffer[m_Tail] = value;
      m_Head = (m_Head - 1 + m_Capacity) % m_Capacity;
    } else {
      m_Head = (m_Head - 1 + m_Capacity) % m_Capacity;
      m_Buffer[m_Head] = value;
      ++m_Size;
    }
  }

  // 尾端插入
  void push_back(const T &value) {
    if (m_Size >= m_Capacity) {
      // 满了，覆盖头部元素（逻辑上是“最老的”）
      m_Buffer[m_Head] = value;
      m_Head = (m_Head + 1) % m_Capacity;
      m_Tail = (m_Tail + 1) % m_Capacity;
    } else {
      m_Buffer[m_Tail] = value;
      m_Tail = (m_Tail + 1) % m_Capacity;
      ++m_Size;
    }
  }

  // 访问前端元素
  const T &front() const {
    if (empty()) {
      throw std::out_of_range("LimitedDeque::front(): empty deque");
    }
    return m_Buffer[m_Head];
  }

  T &front() {
    if (empty()) {
      throw std::out_of_range("LimitedDeque::front(): empty deque");
    }
    return m_Buffer[m_Head];
  }

  // 访问尾端元素
  const T &back() const {
    if (empty()) {
      throw std::out_of_range("LimitedDeque::back(): empty deque");
    }
    return m_Buffer[(m_Tail - 1 + m_Capacity) % m_Capacity];
  }

  T &back() {
    if (empty()) {
      throw std::out_of_range("LimitedDeque::back(): empty deque");
    }
    return m_Buffer[(m_Tail - 1 + m_Capacity) % m_Capacity];
  }

  // 下标访问（只读）
  const T &operator[](size_t index_) const {
    if (index_ >= m_Size) {
      throw std::out_of_range("LimitedDeque::operator[]: index out of range");
    }
    return m_Buffer[this->index(static_cast<ptrdiff_t>(index_))];
  }

  // 下标访问（可写）
  T &operator[](size_t index_) {
    if (index_ >= m_Size) {
      throw std::out_of_range("LimitedDeque::operator[]: index out of range");
    }
    return m_Buffer[this->index(static_cast<ptrdiff_t>(index_))];
  }

  // 迭代器接口
  iterator begin() { return iterator(this, 0); }
  iterator end() { return iterator(this, static_cast<ptrdiff_t>(m_Size)); }

  const_iterator begin() const { return const_iterator(this, 0); }
  const_iterator end() const { return const_iterator(this, static_cast<ptrdiff_t>(m_Size)); }

  const_iterator cbegin() const { return begin(); }
  const_iterator cend() const { return end(); }

  reverse_iterator rbegin() { return reverse_iterator(end()); }
  reverse_iterator rend() { return reverse_iterator(begin()); }

  const_reverse_iterator rbegin() const { return const_reverse_iterator(end()); }
  const_reverse_iterator rend() const { return const_reverse_iterator(begin()); }

  const_reverse_iterator crbegin() const { return rbegin(); }
  const_reverse_iterator crend() const { return rend(); }
};
