package com.example.docmindAI.controller;

import com.example.docmindAI.config.JwtUtils;
import com.example.docmindAI.model.User;
import com.example.docmindAI.repository.UserRepository;
import com.example.docmindAI.service.GoogleTokenVerifier;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Optional;

@RestController
@RequestMapping("/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final GoogleTokenVerifier googleTokenVerifier;
    private final UserRepository userRepository;
    private final JwtUtils jwtUtils;
    private final PasswordEncoder passwordEncoder;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody RegisterRequest request) {
        if (userRepository.findByEmail(request.getEmail()).isPresent()) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body("Email already in use");
        }

        User user = User.builder()
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .name(request.getName())
                .provider("LOCAL")
                .role("USER")
                .build();

        userRepository.save(user);
        log.info("New Local User Registered: {}", request.getEmail());
        
        String token = jwtUtils.generateToken(user);
        return ResponseEntity.ok(new AuthResponse(token, user));
    }

    @PostMapping("/login")
    public ResponseEntity<?> login(@RequestBody LoginRequest request) {
        Optional<User> userOpt = userRepository.findByEmail(request.getEmail());

        if (userOpt.isEmpty()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid email or password");
        }

        User user = userOpt.get();

        // Critical Check: If provider is GOOGLE, reject manual login
        if ("GOOGLE".equals(user.getProvider())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN)
                    .body("This account is linked with Google. Please use 'Sign in with Google'.");
        }

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid email or password");
        }

        log.info("User logged in (LOCAL): {}", user.getEmail());
        String token = jwtUtils.generateToken(user);
        return ResponseEntity.ok(new AuthResponse(token, user));
    }

    @GetMapping("/validate")
    public ResponseEntity<?> validateToken(java.security.Principal principal) {
        if (principal == null) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid or expired token");
        }

        // The principal is a UsernamePasswordAuthenticationToken whose .getPrincipal() is our User entity
        if (principal instanceof org.springframework.security.authentication.UsernamePasswordAuthenticationToken authToken) {
            Object userObj = authToken.getPrincipal();
            if (userObj instanceof User user) {
                return ResponseEntity.ok(user);
            }
        }

        // Fallback: try to find by name (which should be email for our setup)
        Optional<User> userOpt = userRepository.findByEmail(principal.getName());
        return userOpt.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.status(HttpStatus.NOT_FOUND).build());
    }

    @PostMapping("/google")
    public ResponseEntity<?> authenticateWithGoogle(@RequestBody TokenRequest tokenRequest) {
        
        Optional<GoogleIdToken.Payload> payloadOptional = googleTokenVerifier.verifyToken(tokenRequest.getIdToken());

        if (payloadOptional.isEmpty()) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Invalid Google token");
        }

        GoogleIdToken.Payload payload = payloadOptional.get();

        String providerId = payload.getSubject(); // 'sub'
        String email = payload.getEmail();
        String name = (String) payload.get("name");
        String pictureUrl = (String) payload.get("picture");

        // Use findByProviderId for robust identification
        // We also check by email as a fallback if providerId is missing for some reason
        User user = userRepository.findByProviderId(providerId)
                .orElseGet(() -> userRepository.findByEmail(email).orElse(null));

        if (user == null) {
            user = User.builder()
                    .email(email)
                    .name(name)
                    .picture(pictureUrl)
                    .providerId(providerId)
                    .provider("GOOGLE")
                    .role("USER")
                    // createdAt is handled by @PrePersist
                    .build();
            userRepository.save(user);
            log.info("New User Registered: {}", email);
        } else {
            // Optional: update picture or name if changed in Google
            boolean updated = false;
            if (user.getProviderId() == null) {
                 user.setProviderId(providerId);
                 user.setProvider("GOOGLE");
                 updated = true;
            }
            if (updated) {
                userRepository.save(user);
            }
            log.info("User logged in: {}", email);
        }

        String jwt = jwtUtils.generateToken(user);

        return ResponseEntity.ok(new AuthResponse(jwt, user));
    }
}

@Data
class RegisterRequest {
    private String email;
    private String password;
    private String name;
}

@Data
class LoginRequest {
    private String email;
    private String password;
}

@Data
class TokenRequest {
    private String idToken;
}

@Data
@NoArgsConstructor
@AllArgsConstructor
class AuthResponse {
    private String token;
    private User user;
}
