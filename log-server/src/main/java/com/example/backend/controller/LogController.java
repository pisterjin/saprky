package com.example.backend.controller;

import com.example.backend.dto.ChatLogRequest;
import com.example.backend.dto.ClickEventRequest;
import com.example.backend.dto.LogResponse;
import com.example.backend.entity.LogEntity;
import com.example.backend.service.ChatLogService;
import com.example.backend.service.ClickEventService;
import com.example.backend.service.LogService;
import lombok.RequiredArgsConstructor;
import jakarta.validation.Valid;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class LogController {

    private final LogService logService;
    private final ChatLogService chatLogService;
    private final ClickEventService clickEventService;

    // 대화 로그 저장 (프론트 fire-and-forget)
    @PostMapping("/api/log")
    public ResponseEntity<Void> saveLog(@Valid @RequestBody ChatLogRequest req) {
        chatLogService.save(req);
        return ResponseEntity.ok().build();
    }

    // 정책 카드 클릭 이벤트 저장
    @PostMapping("/api/click")
    public ResponseEntity<Void> saveClick(@Valid @RequestBody ClickEventRequest req) {
        clickEventService.save(req);
        return ResponseEntity.ok().build();
    }

    // 전체 조회 (페이징)
    @GetMapping("/api/logs")
    public Page<LogEntity> getLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return logService.getLogs(page, size);
    }

    // 레벨별 필터 (INFO / ERROR)
    @GetMapping("/api/logs/level/{level}")
    public Page<LogEntity> getByLevel(
            @PathVariable String level,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "20") int size) {
        return logService.getLogsByLevel(level, page, size);
    }
}