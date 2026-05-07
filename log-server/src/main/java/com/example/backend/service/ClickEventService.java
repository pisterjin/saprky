package com.example.backend.service;

import com.example.backend.dto.ClickEventRequest;
import com.example.backend.entity.PolicyClickEvent;
import com.example.backend.repository.PolicyClickEventRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class ClickEventService {

    private final PolicyClickEventRepository clickRepo;

    @Async
    @Transactional
    public void save(ClickEventRequest req) {
        clickRepo.save(PolicyClickEvent.builder()
                .sessionId(req.getSessionId())
                .policyId(req.getPolicyId())
                .policyTitle(req.getPolicyTitle())
                .category(req.getCategory())
                .clickedAt(req.getClickedAt())
                .build());
    }
}
