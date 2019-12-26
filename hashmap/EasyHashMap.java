package hashmap;

/**
 * hashmap主体类
 * @author zhangyu
 * @date 2019/1/2 19:43
 **/


public class EasyHashMap<K,V> implements MapInterface<K,V> {

    // 默认大小为 16
    private static final int DEFAULT_INITIAL_CAPACITY = 1 << 4;
    // 默认负载因子0.75
    private static final float DEFAULT_LOAD_FACTOR = 0.75f;
    private float loadFactor = 0;
    private int initCapacity = 0;
    private Entry<K, V>[] table = null;

    // 如果没有定义那就是默认的大小
    public EasyHashMap() {
        this.loadFactor = DEFAULT_LOAD_FACTOR;
        this.initCapacity = DEFAULT_INITIAL_CAPACITY;
        table = new Entry[this.initCapacity];
    }

    // 有参数构造，按照设定的参数进行创建
    public EasyHashMap(int initCapacity, float loadFactor) {
        this.loadFactor = loadFactor;
        this.initCapacity = initCapacity;
        table = new Entry[this.initCapacity];
    }

    // 获得hash值
    private int hash(K key) {
        int h;
        return (key == null) ? 0 : Math.abs(h = key.hashCode());
    }

    @Override
    public V put(K key, V value) {
        // 获取index的值（取模运算），但是在hashmap源码中不是这种实现
        int index = hash(key) % initCapacity;
        if (table[index] != null) {
            Entry<K, V> e = table[index];
            Entry<K, V> e2 = null;
            while (e != null) {
                if (hash(e.key) == hash(key) && e.key.equals(key)) {
                    e.value = value;
                    return value;
                }
                e2 = e;
                e = e.next;
            }
            e2.next = new Entry<>(key, value, null, index);
        } else {
            // 如果table[index]为空，就直接把元素插入下面
            Entry<K, V> e = new Entry<>(key, value, null, index);
            table[index] = e;
        }
        return value;
    }

    @Override
    public V get(K key) {
        // 获取它的下标，但是在hashmap源码中不是这么实现
        // hashmap的源码实现方式：index=hash(key)&(n-1),因为计算机更适合做与或运算
        int index = hash(key) % initCapacity;
        // 创建一个table数组
        Entry<K, V> e = table[index];
        if (e == null) {
            return null;
        }
        while (e != null) {
            if ((e.key == null && key == null) || hash(e.key) == hash(key) && e.key.equals(key)) {
                return e.value;
            }
            e = e.next;
        }
        return null;
    }

    // 内部类对象
    public class Entry<K, V> implements MapInterface.Entry<K, V> {
        private K key;
        private V value;
        private Entry<K, V> next;
        private int index;
        public Entry(K k, V v, Entry<K, V> next, int index) {
            this.key = k;
            this.value = v;
            this.next = next;
            this.index = index;
        }
        public K getKey() {
            return key;
        }
        public V getValue() {
            return value;
        }
        public Entry getNext() {
            return next;
        }
    }
}
