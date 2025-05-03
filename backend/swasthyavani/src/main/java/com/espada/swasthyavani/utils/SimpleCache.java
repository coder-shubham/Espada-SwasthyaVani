/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.utils;

import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */
public class SimpleCache<K, V> {

    private static class CacheEntry<V> {
        private final V value;
        private Instant lastUpdated;

        CacheEntry(V value) {
            this.value = value;
            this.lastUpdated = Instant.now();
        }

        void refresh() {
            this.lastUpdated = Instant.now();
        }
    }

    private final Map<K, CacheEntry<V>> cache = new ConcurrentHashMap<>();

    public void put(K key, V value) {
        cache.put(key, new CacheEntry<>(value));
    }

    public V get(K key) {
        CacheEntry<V> entry = cache.get(key);
        if (entry != null) {
            entry.refresh();
            return entry.value;
        }
        return null;
    }

    public void remove(K key) {
        cache.remove(key);
    }

    public void cleanUp(long olderThanMillis) {
        Instant now = Instant.now();
        cache.entrySet().removeIf(entry ->
                now.toEpochMilli() - entry.getValue().lastUpdated.toEpochMilli() > olderThanMillis
                        && !entry.getKey().equals("telehistory"));
    }
}
