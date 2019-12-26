package hashmap;

/**
 * 测试手写的hashmap
 * @author zhangyu
 * @date 2019/1/2 19:48
 **/


public class MapTest {
    public static void main(String[] args) {
        MapInterface<String, Object> map = new EasyHashMap<>();
        map.put("name", "zhangyu");
        map.put("age", 18);
        map.put("address", "jiangsu");
        map.put("sex", "male");
        map.put(null, "zhangyu");

        System.out.println(map.get("name"));
        System.out.println(map.get("age"));
        System.out.println(map.get("address"));
        System.out.println(map.get("sex"));
        System.out.println(map.get(null));
    }
}
