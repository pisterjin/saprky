package com.example.backend.controller;

import com.example.backend.entity.UserEntity;
import com.example.backend.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {

    private final UserService userService;

    @PostMapping("/onboarding")
    public UserEntity registerUser(@RequestBody UserEntity user) {
        // 유저 정보를 저장하고 결과를 반환
        return userService.join(user);
    }
}