package com.example.backend.config;

import io.github.bucket4j.Bandwidth;
import io.github.bucket4j.Bucket;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.time.Duration;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class RateLimitFilter extends OncePerRequestFilter {

    @Value("${rate-limit.requests-per-minute:30}")
    private int requestsPerMinute;

    private static final Set<String> PROTECTED_PATHS = Set.of("/api/log", "/api/click");

    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        if ("POST".equals(request.getMethod()) && PROTECTED_PATHS.contains(request.getRequestURI())) {
            String ip = resolveClientIp(request);
            Bucket bucket = buckets.computeIfAbsent(ip, k ->
                    Bucket.builder()
                            .addLimit(Bandwidth.simple(requestsPerMinute, Duration.ofMinutes(1)))
                            .build()
            );

            if (!bucket.tryConsume(1)) {
                response.setStatus(429);
                response.setContentType("application/json");
                response.getWriter().write("{\"error\":\"Too Many Requests\"}");
                return;
            }
        }
        chain.doFilter(request, response);
    }

    private String resolveClientIp(HttpServletRequest request) {
        String forwarded = request.getHeader("X-Forwarded-For");
        if (forwarded != null && !forwarded.isBlank()) {
            return forwarded.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
