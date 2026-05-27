import java.util.*;

public class ThreadUnsafe {

    // Bug 1: Non-thread-safe counter — race condition
    private int counter = 0;

    public void increment() {
        counter++;
    }

    public int getCounter() {
        return counter;
    }

    // Bug 2: ArrayList in multithreaded context — not thread safe
    private List<String> sharedList = new ArrayList<>();

    public void addItem(String item) {
        sharedList.add(item);
    }

    // Bug 3: Double-checked locking done wrong — missing volatile
    private static ThreadUnsafe instance;

    public static ThreadUnsafe getInstance() {
        if (instance == null) {
            synchronized (ThreadUnsafe.class) {
                instance = new ThreadUnsafe();
            }
        }
        return instance;
    }

    // Bug 4: Busy waiting — burns CPU with infinite loop
    public void waitForResult(boolean ready) {
        while (!ready) {
            // doing nothing — CPU spinning at 100%
        }
    }

    // Bug 5: HashMap not thread safe — concurrent modification
    private Map<String, String> cache = new HashMap<>();

    public String getFromCache(String key) {
        return cache.get(key);
    }

    public void putInCache(String key, String value) {
        cache.put(key, value);
    }

    // Bug 6: Thread created but never managed
    public void startBackgroundTask() {
        Thread t = new Thread(() -> {
            System.out.println("Running...");
        });
        t.start();
        // thread never joined or tracked
    }
}