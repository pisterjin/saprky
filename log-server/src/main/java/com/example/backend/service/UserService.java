package com.example.backend.service;

import com.example.backend.common.Common;
import com.example.backend.entity.UserEntity;
import com.example.backend.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;

    public UserEntity join(UserEntity user) {
        // 지역 정보를 암호화해서 저장
        user.setRegion(Common.encrypt(user.getRegion()));
        return userRepository.save(user);
    }
}