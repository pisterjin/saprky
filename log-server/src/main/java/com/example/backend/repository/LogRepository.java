package com.example.backend.repository;

import com.example.backend.entity.LogEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface LogRepository extends JpaRepository<LogEntity, Long> {
    List<LogEntity> findByUserId(String userId);

    Page<LogEntity> findByLogType(String logType, PageRequest pageRequest);

}