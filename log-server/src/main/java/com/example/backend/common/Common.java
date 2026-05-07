package com.example.backend.common;

import java.util.UUID;
import java.util.Base64;
import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;
import java.nio.charset.StandardCharsets;

public class Common {

    // 설계서 v2.0 요구사항: AES-256 암호화 키 (반드시 32자여야 함)
    private static final String SECRET_KEY = "sparky-secret-key-12345678901234"; // 32자 확인됨
    private static final String ALGORITHM = "AES/ECB/PKCS5Padding"; // 보안 모드 명시

    // UUID 생성 (사용자 식별용)
    public static String generateUUID() {
        return UUID.randomUUID().toString();
    }

    // [수정] 데이터 암호화
    public static String encrypt(String plainText) {
        if (plainText == null) return null;
        try {
            SecretKeySpec secretKey = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "AES");
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, secretKey);
            byte[] encryptedBytes = cipher.doFinal(plainText.getBytes(StandardCharsets.UTF_8));
            return Base64.getEncoder().encodeToString(encryptedBytes);
        } catch (Exception e) {
            // 에러 시 원본 대신 에러 로그를 남기고 빈 값 또는 예외 처리를 권장합니다.
            System.err.println("Encryption Error: " + e.getMessage());
            return "";
        }
    }

    // [추가] 데이터 복호화 (DB에서 읽어올 때 필요)
    public static String decrypt(String encryptedText) {
        if (encryptedText == null || encryptedText.isEmpty()) return "";
        try {
            SecretKeySpec secretKey = new SecretKeySpec(SECRET_KEY.getBytes(StandardCharsets.UTF_8), "AES");
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, secretKey);
            byte[] decodedBytes = Base64.getDecoder().decode(encryptedText);
            byte[] decryptedBytes = cipher.doFinal(decodedBytes);
            return new String(decryptedBytes, StandardCharsets.UTF_8);
        } catch (Exception e) {
            System.err.println("Decryption Error: " + e.getMessage());
            return "";
        }
    }
}