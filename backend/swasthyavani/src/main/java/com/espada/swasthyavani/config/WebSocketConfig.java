/*
 * Copyright (c) 2025 Nextiva, Inc. to Present.
 * All rights reserved.
 */

package com.espada.swasthyavani.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.messaging.simp.config.SimpleBrokerRegistration;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;
import org.springframework.web.socket.config.annotation.EnableWebSocket;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.SockJsServiceRegistration;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;
import org.springframework.web.socket.config.annotation.WebSocketTransportRegistration;

/**
 * Class Description goes here.
 * Created by shubhamsarraf on 26/04/25
 */
@Configuration
@EnableWebSocket
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer{

    SimpleBrokerRegistration simpleBrokerRegistration;

    @Override public void registerStompEndpoints(StompEndpointRegistry registry) {
        SockJsServiceRegistration registration =
                registry.addEndpoint("/socket").setAllowedOriginPatterns("*").withSockJS();
        registration.setWebSocketEnabled(true);
    }

    @Override public void configureMessageBroker(MessageBrokerRegistry registry) {

        ThreadPoolTaskScheduler te = new ThreadPoolTaskScheduler();
        te.setPoolSize(1);
        te.setThreadNamePrefix("socket-heartbeat-thread-");
        te.initialize();

        simpleBrokerRegistration = registry.enableSimpleBroker("/topic")
                .setHeartbeatValue(new long[] {10000, 10000})
                .setTaskScheduler(te);
        registry.setApplicationDestinationPrefixes(
                "/public");

    }

    @Override public void configureWebSocketTransport(WebSocketTransportRegistration registry) {

        registry
                .setSendTimeLimit(10 * 10000)
                .setSendBufferSizeLimit(2048 * 2048)
                .setMessageSizeLimit(2 * 1024 * 1024);

    }
}
