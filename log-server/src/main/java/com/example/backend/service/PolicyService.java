package com.example.backend.service;

import com.example.backend.dto.PolicyResponse;
import com.example.backend.entity.PolicyEntity;
import com.example.backend.repository.PolicyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;

@Service
@RequiredArgsConstructor
public class PolicyService {

    private final PolicyRepository policyRepository;
    private final LogService logService; // ← 추가

    public PolicyResponse getPolicyById(Long id, String userId, String sessionId) { // ← 파라미터 추가
        try {
            PolicyEntity entity = policyRepository.findById(id)
                    .orElseThrow(() -> new RuntimeException("정책을 찾을 수 없습니다."));

            // 정책 조회 로그
            logService.savePolicy(userId, sessionId, String.valueOf(id)); // ← 추가

            return PolicyResponse.builder()
                    .category(entity.getCategory())
                    .title(entity.getTitle())
                    .summary(entity.getDescription())    // description → summary
                    .applicationPeriod(entity.getDeadline())
                    .target(entity.getTarget())
                    .amount(entity.getAmount())
                    .linkUrl(entity.getLinkUrl())
                    .dDay(calculateDDay(entity.getDDayDate())) // D-day 계산 별도 메서드
                    .build();

        } catch (Exception e) {
            logService.saveError(userId, sessionId, "정책 조회 실패 id=" + id + " " + e.getMessage()); // ← 추가
            throw e;
        }
    }

    private String calculateDDay(LocalDate dDayDate) {
        if (dDayDate == null) return "상시";

        long days = LocalDate.now().until(dDayDate, java.time.temporal.ChronoUnit.DAYS);

        if (days < 0)  return "마감";
        if (days == 0) return "D-day";
        return "D-" + days;
    }
}