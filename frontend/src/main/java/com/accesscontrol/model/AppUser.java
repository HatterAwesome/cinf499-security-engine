package com.accesscontrol.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.index.Indexed;
import org.springframework.data.mongodb.core.mapping.Document;

// Stores application user accounts in MongoDB.
@Document(collection = "users")
public class AppUser {

    @Id
    private String id;

    @Indexed(unique = true)
    private String username;

    // Store a BCrypt hash here, never the original password.
    private String password;

    // Examples: ROLE_ADMIN and ROLE_OPERATOR.
    private String role;

    public AppUser() {
    }

    public AppUser(String username, String password, String role) {
        this.username = username;
        this.password = password;
        this.role = role;
    }

    public String getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public String getRole() {
        return role;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setRole(String role) {
        this.role = role;
    }
}
