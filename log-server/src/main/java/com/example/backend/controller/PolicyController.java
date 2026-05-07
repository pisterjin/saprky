package com.example.backend.controller;

import com.example.backend.dto.PolicyResponse;
import com.example.backend.entity.PolicyEntity;
import com.example.backend.service.LogService;
import com.example.backend.service.PolicyService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;


@RestController
@RequestMapping("/api/policies")
@RequiredArgsConstructor // 이걸 적어야 LogService가 자동으로 연결됩니다.
public class PolicyController {

    private final PolicyService policyService;

    @GetMapping("/{id}")
    public ResponseEntity<PolicyResponse> getPolicy(
            @PathVariable Long id,
            @RequestHeader(value = "X-User-Id", defaultValue = "anonymous") String userId,
            @RequestHeader(value = "X-Session-Id", defaultValue = "unknown") String sessionId) {

        PolicyResponse response = policyService.getPolicyById(id, userId, sessionId);
        return ResponseEntity.ok(response);
    }
}