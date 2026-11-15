package com.accesscontrol.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;

// Stores a simulated access-control event.
@Document(collection = "access_events")
public class AccessEvent {

    @Id
    private String id;

    private String doorName;
    private String personName;
    private String result;
    private String details;
    private LocalDateTime timestamp;

    public AccessEvent() {
    }

    public AccessEvent(String doorName, String personName,
                       String result, String details,
                       LocalDateTime timestamp) {
        this.doorName = doorName;
        this.personName = personName;
        this.result = result;
        this.details = details;
        this.timestamp = timestamp;
    }

    public String getId() {
        return id;
    }

    public String getDoorName() {
        return doorName;
    }

    public String getPersonName() {
        return personName;
    }

    public String getResult() {
        return result;
    }

    public String getDetails() {
        return details;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public void setId(String id) {
        this.id = id;
    }

    public void setDoorName(String doorName) {
        this.doorName = doorName;
    }

    public void setPersonName(String personName) {
        this.personName = personName;
    }

    public void setResult(String result) {
        this.result = result;
    }

    public void setDetails(String details) {
        this.details = details;
    }

    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}
