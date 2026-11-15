package com.accesscontrol.model;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

// Stores a simulated physical access-control door.
@Document(collection = "doors")
public class Door {

    @Id
    private String id;

    @NotBlank(message = "Door name is required.")
    @Size(max = 80, message = "Door name must be 80 characters or fewer.")
    private String name;

    @NotBlank(message = "Location is required.")
    @Size(max = 120, message = "Location must be 120 characters or fewer.")
    private String location;

    @NotBlank(message = "Choose a door status.")
    @Pattern(regexp = "SECURE|UNLOCKED|OFFLINE",
             message = "Choose a valid door status.")
    private String status;

    public Door() {
    }

    public Door(String name, String location, String status) {
        this.name = name;
        this.location = location;
        this.status = status;
    }

    public String getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getLocation() {
        return location;
    }

    public String getStatus() {
        return status;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public void setStatus(String status) {
        this.status = status;
    }
}
