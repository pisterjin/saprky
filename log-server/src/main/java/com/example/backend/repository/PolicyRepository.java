package com.example.backend.repository;

import com.example.backend.entity.PolicyEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PolicyRepository extends JpaRepository<PolicyEntity, Long> {
}