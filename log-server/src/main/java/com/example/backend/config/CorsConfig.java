package com.example.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Value("${cors.allowed-origins:http://localhost:3000}")
    private String allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        // POST 로그 엔드포인트: 프론트 출처만 허용
        registry.addMapping("/api/log")
                .allowedOrigins(allowedOrigins.split(","))
                .allowedMethods("POST", "OPTIONS")
                .allowedHeaders("Content-Type", "X-API-Key");

        registry.addMapping("/api/click")
                .allowedOrigins(allowedOrigins.split(","))
                .allowedMethods("POST", "OPTIONS")
                .allowedHeaders("Content-Type", "X-API-Key");

        // GET 통계 엔드포인트: 대시보드(파일 직접 열기) 포함 허용
        registry.addMapping("/api/stats/**")
                .allowedOriginPatterns("*")
                .allowedMethods("GET", "OPTIONS")
                .allowedHeaders("Content-Type");

        registry.addMapping("/api/logs/**")
                .allowedOrigins(allowedOrigins.split(","))
                .allowedMethods("GET", "OPTIONS")
                .allowedHeaders("Content-Type");
    }
}
