package com.example.docmindAI.config;

import com.example.docmindAI.model.User;
import org.junit.jupiter.api.Test;
import org.springframework.test.util.ReflectionTestUtils;

import static org.junit.jupiter.api.Assertions.*;

class JwtUtilsTest {

    @Test
    void testTokenGenerationAndValidation() {
        JwtUtils jwtUtils = new JwtUtils();
        ReflectionTestUtils.setField(jwtUtils, "secretKey", "my-super-secret-jwt-key-which-should-be-very-long-for-security-reasons-1234567890");
        ReflectionTestUtils.setField(jwtUtils, "jwtExpiration", 86400000L);

        User user = User.builder()
                .id(1L)
                .email("test@example.com")
                .role("USER")
                .build();

        String token = jwtUtils.generateToken(user);
        assertNotNull(token);
        assertEquals("test@example.com", jwtUtils.extractEmail(token));
        assertTrue(jwtUtils.isTokenValid(token));
    }
}
