package hashmap;

/**
 * MapInterface 接口定义了主类需要实现的方法
 * @author zhangyu
 * @date 2019/1/2 19:39
 **/

public interface MapInterface<K, V> {
    public V put(K key, V value);
    public V get(K key);
    // 定义内部实现的接口，获取key和value的值
    interface Entry<K, V> {
        public K getKey();
        public V getValue();
    }
}
