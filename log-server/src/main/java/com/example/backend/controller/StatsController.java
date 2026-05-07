package com.example.backend.controller;

import com.example.backend.service.StatsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/stats")
@RequiredArgsConstructor
public class StatsController {

    private final StatsService statsService;

    @GetMapping("/overview")
    public ResponseEntity<Map<String, Object>> overview() {
        return ResponseEntity.ok(statsService.overview());
    }

    @GetMapping("/daily")
    public ResponseEntity<List<Map<String, Object>>> daily() {
        return ResponseEntity.ok(statsService.daily());
    }

    @GetMapping("/domain")
    public ResponseEntity<List<Map<String, Object>>> domain() {
        return ResponseEntity.ok(statsService.domain());
    }

    @GetMapping("/profile")
    public ResponseEntity<Map<String, List<Map<String, Object>>>> profile() {
        return ResponseEntity.ok(statsService.profile());
    }

    @GetMapping("/top-policies")
    public ResponseEntity<List<Map<String, Object>>> topPolicies() {
        return ResponseEntity.ok(statsService.topPolicies());
    }

    @GetMapping("/clarifying")
    public ResponseEntity<List<Map<String, Object>>> clarifying() {
        return ResponseEntity.ok(statsService.clarifying());
    }
}
