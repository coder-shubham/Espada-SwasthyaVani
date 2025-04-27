/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.service;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import com.espada.swasthyavani.utils.SimpleCache;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 27/04/25
 */

@Service
public class CacheService {

    private final SimpleCache<String, Object> cache = new SimpleCache<>();

    public void saveToCache(String key, Object value) {
        cache.put(key, value);
    }

    public Object getFromCache(String key) {
        return cache.get(key);
    }

    public void removeFromCache(String key) {
        cache.remove(key);
    }

    @Scheduled(fixedDelay = 60000) // Every 1 minute
    public void cleanUpCache() {
        System.out.println("Cleaning up old cache entries...");
        cache.cleanUp(5 * 60 * 1000); // 5 minutes in milliseconds
    }

}
