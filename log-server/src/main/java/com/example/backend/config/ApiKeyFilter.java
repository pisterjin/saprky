package com.example.backend.config;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Set;

@Component
public class ApiKeyFilter extends OncePerRequestFilter {

    @Value("${log.api-key}")
    private String apiKey;

    private static final Set<String> PROTECTED_PATHS = Set.of("/api/log", "/api/click");

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {
        if ("POST".equals(request.getMethod()) && PROTECTED_PATHS.contains(request.getRequestURI())) {
            String key = request.getHeader("X-API-Key");
            if (key == null || !key.equals(apiKey)) {
                response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
                response.setContentType("application/json");
                response.getWriter().write("{\"error\":\"Unauthorized\"}");
                return;
            }
        }
        chain.doFilter(request, response);
    }
}
