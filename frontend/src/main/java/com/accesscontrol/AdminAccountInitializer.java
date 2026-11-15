package com.accesscontrol;

import com.accesscontrol.model.AppUser;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

// Creates the initial administrator account if it does not exist.
@Component
public class AdminAccountInitializer implements CommandLineRunner {

    private final AppUserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AdminAccountInitializer(
            AppUserRepository userRepository,
            PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @Override
    public void run(String... args) {
        String username = System.getenv("APP_ADMIN_USERNAME");
        String password = System.getenv("APP_ADMIN_PASSWORD");

        if (username == null || username.isBlank()
                || password == null || password.isBlank()) {
            throw new IllegalStateException(
                    "Admin credentials must be set in environment variables.");
        }

        // Do not overwrite an existing administrator's password.
        if (userRepository.findByUsername(username).isPresent()) {
            System.out.println("Admin account already exists.");
            return;
        }

        // Hash the password before saving it.
        String passwordHash = passwordEncoder.encode(password);

        AppUser admin = new AppUser(
                username,
                passwordHash,
                "ROLE_ADMIN"
        );

        userRepository.save(admin);
        System.out.println("Initial admin account created.");
    }
}
