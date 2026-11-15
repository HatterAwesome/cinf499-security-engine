package com.accesscontrol;

import com.accesscontrol.model.AppUser;
import org.springframework.security.core.Authentication;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class AdminUserController {

    private final AppUserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AdminUserController(
            AppUserRepository userRepository,
            PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    @GetMapping("/admin/users")
    public String users(Model model) {
        model.addAttribute("users", userRepository.findAll());
        return "admin-users";
    }

    @PostMapping("/admin/users")
    public String createUser(
            @RequestParam String username,
            @RequestParam String password,
            @RequestParam String role,
            RedirectAttributes redirectAttributes,
            Model model) {

        username = username.trim();

        if (username.isBlank() || username.length() > 40) {
            return creationError(model,
                    "Username is required and must be 40 characters or fewer.");
        }

        if (password.length() < 12 || password.length() > 72) {
            return creationError(model,
                    "Password must be between 12 and 72 characters.");
        }

        if (!validRole(role)) {
            return creationError(model, "Choose a valid role.");
        }

        if (userRepository.findByUsername(username).isPresent()) {
            return creationError(model, "That username already exists.");
        }

        AppUser user = new AppUser();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setRole(role);
        userRepository.save(user);

        redirectAttributes.addFlashAttribute(
                "success", "User account created successfully.");

        return "redirect:/admin/users";
    }

    @GetMapping("/admin/users/{id}/edit")
    public String editUser(
            @PathVariable String id,
            Authentication authentication,
            Model model,
            RedirectAttributes redirectAttributes) {

        AppUser user = userRepository.findById(id).orElse(null);

        if (user == null) {
            redirectAttributes.addFlashAttribute("error", "User not found.");
            return "redirect:/admin/users";
        }

        if (user.getUsername().equals(authentication.getName())) {
            redirectAttributes.addFlashAttribute(
                    "error", "You cannot edit your own administrator account here.");
            return "redirect:/admin/users";
        }

        model.addAttribute("user", user);
        return "edit-user";
    }

    @PostMapping("/admin/users/{id}/edit")
    public String updateUser(
            @PathVariable String id,
            @RequestParam String username,
            @RequestParam String role,
            @RequestParam(required = false, defaultValue = "") String password,
            Authentication authentication,
            Model model,
            RedirectAttributes redirectAttributes) {

        AppUser user = userRepository.findById(id).orElse(null);

        if (user == null) {
            redirectAttributes.addFlashAttribute("error", "User not found.");
            return "redirect:/admin/users";
        }

        if (user.getUsername().equals(authentication.getName())) {
            redirectAttributes.addFlashAttribute(
                    "error", "You cannot edit your own administrator account here.");
            return "redirect:/admin/users";
        }

        username = username.trim();

        if (username.isBlank() || username.length() > 40) {
            return editError(model, user,
                    "Username is required and must be 40 characters or fewer.");
        }

        if (!validRole(role)) {
            return editError(model, user, "Choose a valid role.");
        }

        if (userRepository.findByUsername(username)
                .filter(existing -> !existing.getId().equals(user.getId()))
                .isPresent()) {
            return editError(model, user, "That username already exists.");
        }

        if (!password.isBlank()
                && (password.length() < 12 || password.length() > 20)) {
            return editError(model, user,
                    "A new password must be between 12 and 72 characters.");
        }

        user.setUsername(username);
        user.setRole(role);

        if (!password.isBlank()) {
            user.setPassword(passwordEncoder.encode(password));
        }

        userRepository.save(user);

        redirectAttributes.addFlashAttribute(
                "success", "User account updated successfully.");

        return "redirect:/admin/users";
    }

    @PostMapping("/admin/users/{id}/delete")
    public String deleteUser(
            @PathVariable String id,
            Authentication authentication,
            RedirectAttributes redirectAttributes) {

        AppUser user = userRepository.findById(id).orElse(null);

        if (user == null) {
            redirectAttributes.addFlashAttribute("error", "User not found.");
            return "redirect:/admin/users";
        }

        if (user.getUsername().equals(authentication.getName())) {
            redirectAttributes.addFlashAttribute(
                    "error", "You cannot delete your own account.");
            return "redirect:/admin/users";
        }

        userRepository.delete(user);

        redirectAttributes.addFlashAttribute(
                "success", "User account deleted successfully.");

        return "redirect:/admin/users";
    }

    private boolean validRole(String role) {
        return "ROLE_ADMIN".equals(role)
                || "ROLE_OPERATOR".equals(role);
    }

    private String creationError(Model model, String message) {
        model.addAttribute("error", message);
        model.addAttribute("users", userRepository.findAll());
        return "admin-users";
    }

    private String editError(Model model, AppUser user, String message) {
        model.addAttribute("error", message);
        model.addAttribute("user", user);
        return "edit-user";
    }
}
